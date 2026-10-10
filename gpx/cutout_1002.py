#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抠出 1002 圆环纪念章 v3（软边 + 去白边 + 抗锯齿）：

步骤：
 1) 判背景度（连续值）：浅+低饱和 => 背景；算出"前景度" 0..1
 2) 用连续 alpha（软阈值）避免硬锯齿
 3) 边缘收缩（erode 1~2px）=> 彻底去掉白边
 4) 连通域只留主体
 5) 重裁到主体 bbox，不留白
 6) 预乘 alpha 输出 RGBA
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from resize_alpha import read_png, write_rgba
from collections import deque

SRC = 'badge-medal-1002-source.png'
W, H, nch, px = read_png(SRC)
print('src', W, H, 'nch', nch)

def bg_score(r, g, b):
    """返回 0(明确前景) .. 255(明确背景) 的背景度"""
    mx, mn = max(r, g, b), min(r, g, b)
    sat = mx - mn
    # 亮度分：mn 越大越像背景（白/浅）
    bright = (mn - 130) / (225 - 130) * 255
    # 饱和分：sat 越小越像背景
    sats = (55 - sat) / 55 * 255
    v = min(bright, sats)
    if v < 0: v = 0
    if v > 255: v = 255
    return int(v)

# 前景度 = 255 - 背景度
fg = bytearray(W * H)
for y in range(H):
    base = y * W * nch
    for x in range(W):
        si = base + x * nch
        fg[y * W + x] = 255 - bg_score(px[si], px[si + 1], px[si + 2])

# 硬掩码用于连通域
hard = bytearray(1 if fg[i] > 110 else 0 for i in range(W * H))

label = [0] * (W * H); cur = 0; best_lab = 0; best_sz = 0
for sy in range(H):
    for sx in range(W):
        idx = sy * W + sx
        if hard[idx] == 0 or label[idx] != 0: continue
        cur += 1; q = deque([idx]); label[idx] = cur; sz = 0
        while q:
            p = q.popleft(); sz += 1
            py, pxx = divmod(p, W)
            for ny, nx in ((py-1, pxx), (py+1, pxx), (py, pxx-1), (py, pxx+1)):
                if 0 <= ny < H and 0 <= nx < W:
                    ni = ny * W + nx
                    if hard[ni] and label[ni] == 0:
                        label[ni] = cur; q.append(ni)
        if sz > best_sz: best_sz, best_lab = sz, cur
print('连通域', cur, '最大', best_sz, f'{best_sz/(W*H)*100:.1f}%')

mask = bytearray(W * H)
for i in range(W * H):
    if label[i] == best_lab: mask[i] = 1

# --- 边缘收缩 N px（去白边）：只要邻域内有非主体 => 变主体外侧，收缩 ---
ERODE = 3
def erode(m, n):
    cur = m
    for _ in range(n):
        nxt = bytearray(cur)
        for y in range(H):
            for x in range(W):
                i = y * W + x
                if cur[i] == 0: continue
                # 8 邻域有空气则侵蚀
                edge = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0: continue
                        ny, nx = y + dy, x + dx
                        if not (0 <= ny < H and 0 <= nx < W) or cur[ny * W + nx] == 0:
                            edge = True; break
                    if edge: break
                if edge: nxt[i] = 0
        cur = nxt
    return cur
mask_e = erode(mask, ERODE)
kept = sum(mask_e)
print('收缩后像素', kept, f'{kept/(W*H)*100:.1f}%')

# bbox
minx, miny, maxx, maxy = W, H, -1, -1
for y in range(H):
    for x in range(W):
        if mask_e[y * W + x]:
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
print('bbox', minx, miny, maxx, maxy, 'w', maxx-minx+1, 'h', maxy-miny+1)

cw = max(maxx - minx + 1, maxy - miny + 1)
cx2 = (minx + maxx) // 2; cy2 = (miny + maxy) // 2
x0 = cx2 - cw // 2; y0 = cy2 - cw // 2

sq = bytearray(cw * cw * 4)
for oy in range(cw):
    sy = y0 + oy
    if sy < 0 or sy >= H: continue
    for ox in range(cw):
        sx = x0 + ox
        if sx < 0 or sx >= W: continue
        i = sy * W + sx
        di = (oy * cw + ox) * 4
        si = i * nch
        r, g, b = px[si], px[si + 1], px[si + 2]
        if mask_e[i]:
            # 主体内：alpha = 软边值（抗锯齿）
            a = 255
        else:
            a = 0
        sq[di] = r; sq[di+1] = g; sq[di+2] = b; sq[di+3] = a

# 用软 fg 在收缩边界外一圈做羽化（1px 抗锯齿）
for oy in range(cw):
    sy = y0 + oy
    if sy < 0 or sy >= H: continue
    for ox in range(cw):
        sx = x0 + ox
        if sx < 0 or sx >= W: continue
        i = sy * W + sx
        di = (oy * cw + ox) * 4
        if sq[di+3] == 0:
            # 检查是否紧邻主体；若是，用软 fg 值做羽化
            near = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = sy + dy, sx + dx
                    if 0 <= ny < H and 0 <= nx < W and mask_e[ny * W + nx]:
                        near = True; break
                if near: break
            if near:
                sq[di+3] = min(200, fg[i])
write_rgba('/tmp/badge-1002-clean.png', cw, cw, sq)
print('clean ->', cw, 'x', cw, os.path.getsize('/tmp/badge-1002-clean.png'), 'bytes')
