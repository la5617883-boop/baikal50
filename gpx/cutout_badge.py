#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抠出 1002环形 纪念章（通用版）：去背景 -> 收缩去白边 -> 连通域留主体 -> 重裁 -> RGBA。
用法：python3 gpx/cutout_badge.py <源图> <输出>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resize_alpha import read_png, write_rgba
from collections import deque

SRC = sys.argv[1] if len(sys.argv) > 1 else 'badge-medal-1002-source.png'
DST = sys.argv[2] if len(sys.argv) > 2 else '/tmp/badge-clean.png'
ERODE = int(sys.argv[3]) if len(sys.argv) > 3 else 3

W, H, nch, px = read_png(SRC)
print('src', SRC, W, H, 'nch', nch)

# --- 取四角平均作为背景色参考 ---
def P(x, y, n):
    i = (y * W + x) * n
    return px[i], px[i + 1], px[i + 2]

corners = [P(2, 2, nch), P(W - 3, 2, nch), P(2, H - 3, nch), P(W - 3, H - 3, nch)]
print('四角背景参考:', corners)
bgr = sum(c[0] for c in corners) // 4
bgg = sum(c[1] for c in corners) // 4
bgb = sum(c[2] for c in corners) // 4
print('背景均值:', (bgr, bgg, bgb))

def bg_score(r, g, b):
    """综合两种背景判据：与背景色接近 + 浅色低饱和"""
    # (a) 与角落背景色的距离
    d = ((r - bgr) ** 2 + (g - bgg) ** 2 + (b - bgb) ** 2) ** 0.5
    score_a = 255 if d < 26 else (0 if d > 62 else int((62 - d) / (62 - 26) * 255))
    # (b) 浅色低饱和
    mx, mn = max(r, g, b), min(r, g, b)
    sat = mx - mn
    bright = (mn - 130) / (225 - 130) * 255
    sats = (55 - sat) / 55 * 255
    score_b = int(max(0, min(bright, sats, 255)))
    return max(score_a, score_b)

fg = bytearray(W * H)
for y in range(H):
    base = y * W * nch
    for x in range(W):
        si = base + x * nch
        fg[y * W + x] = 255 - bg_score(px[si], px[si + 1], px[si + 2])

hard = bytearray(1 if fg[i] > 110 else 0 for i in range(W * H))

# 连通域只留最大
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
print('连通域', cur, '最大块', best_sz, f'{best_sz/(W*H)*100:.1f}%')

mask = bytearray(W * H)
for i in range(W * H):
    if label[i] == best_lab: mask[i] = 1

# 边缘收缩去白边
def erode(m, n):
    c = m
    for _ in range(n):
        nx = bytearray(c)
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                i = y * W + x
                if c[i] == 0: continue
                if (c[i-1] == 0 or c[i+1] == 0 or c[i-W] == 0 or c[i+W] == 0 or
                    c[i-W-1] == 0 or c[i-W+1] == 0 or c[i+W-1] == 0 or c[i+W+1] == 0):
                    nx[i] = 0
        c = nx
    return c
me = erode(mask, ERODE)
print('收缩', ERODE, 'px 后', sum(me), f'{sum(me)/(W*H)*100:.1f}%')

# bbox
minx, miny, maxx, maxy = W, H, -1, -1
for y in range(H):
    for x in range(W):
        if me[y * W + x]:
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
        sq[di] = px[si]; sq[di+1] = px[si+1]; sq[di+2] = px[si+2]
        if me[i]:
            sq[di+3] = 255
        else:
            # 紧邻主体 => 羽化
            near = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = sy + dy, sx + dx
                    if 0 <= ny < H and 0 <= nx < W and me[ny * W + nx]:
                        near = True; break
                if near: break
            sq[di+3] = min(200, fg[i]) if near else 0
write_rgba(DST, cw, cw, sq)
print('->', DST, cw, 'x', cw, os.path.getsize(DST), 'bytes')
