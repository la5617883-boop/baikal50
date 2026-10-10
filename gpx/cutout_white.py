#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抠白底徽章（强化版）：针对纯白/近白背景 + 浅色主体的图。
问题：主体含浅灰/银白部件（如睡袋），太激进会把主体抠掉；
      太宽松会留白边。解法：
  1) 背景判定用「与纯白的距离」+ 「最大通道值很高」
  2) alpha 软过渡（0-40 距离区间线性）
  3) 边缘收缩（可调）去白边
  4) 收缩后在边界处做 1px 羽化，避免硬锯齿
  5) 只留最大连通域
用法：python3 gpx/cutout_white.py <src> <dst> <erode>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resize_alpha import read_png, write_rgba
from collections import deque

SRC, DST = sys.argv[1], sys.argv[2]
ERODE = int(sys.argv[3]) if len(sys.argv) > 3 else 4
WHITE_LO = float(sys.argv[4]) if len(sys.argv) > 4 else 20.0   # 距白 < 此值 => 纯背景
WHITE_HI = float(sys.argv[5]) if len(sys.argv) > 5 else 55.0   # 距白 > 此值 => 纯前景

W, H, nch, px = read_png(SRC)
print('src', SRC, W, H, 'nch', nch)

def P(x, y):
    i = (y * W + x) * nch
    return px[i], px[i+1], px[i+2]

# 参考白（四角）
cs = [P(2,2), P(W-3,2), P(2,H-3), P(W-3,H-3)]
wr = sum(c[0] for c in cs)//4; wg = sum(c[1] for c in cs)//4; wb = sum(c[2] for c in cs)//4
print('参考白:', (wr, wg, wb), '四角:', cs)

def dist_white(r, g, b):
    return ((r-wr)**2 + (g-wg)**2 + (b-wb)**2) ** 0.5

fg = bytearray(W*H)
for y in range(H):
    base = y*W*nch
    for x in range(W):
        si = base + x*nch
        d = dist_white(px[si], px[si+1], px[si+2])
        if d <= WHITE_LO:
            v = 0
        elif d >= WHITE_HI:
            v = 255
        else:
            v = int((d - WHITE_LO) / (WHITE_HI - WHITE_LO) * 255)
        fg[y*W+x] = v

hard = bytearray(1 if fg[i] > 90 else 0 for i in range(W*H))

# 最大连通域
label = [0]*(W*H); cur = 0; best_lab = 0; best_sz = 0
for sy in range(H):
    for sx in range(W):
        idx = sy*W+sx
        if hard[idx] == 0 or label[idx] != 0: continue
        cur += 1; q = deque([idx]); label[idx] = cur; sz = 0
        while q:
            p = q.popleft(); sz += 1
            py, pxx = divmod(p, W)
            for ny, nx in ((py-1,pxx),(py+1,pxx),(py,pxx-1),(py,pxx+1)):
                if 0 <= ny < H and 0 <= nx < W:
                    ni = ny*W+nx
                    if hard[ni] and label[ni] == 0:
                        label[ni] = cur; q.append(ni)
        if sz > best_sz: best_sz, best_lab = sz, cur
print('连通域', cur, '最大', best_sz, f'{best_sz/(W*H)*100:.1f}%')

mask = bytearray(W*H)
for i in range(W*H):
    if label[i] == best_lab: mask[i] = 1

# 收缩去白边
c = mask
for _ in range(ERODE):
    nx = bytearray(c)
    for y in range(1, H-1):
        for x in range(1, W-1):
            i = y*W+x
            if c[i] == 0: continue
            if (c[i-1]==0 or c[i+1]==0 or c[i-W]==0 or c[i+W]==0 or
                c[i-W-1]==0 or c[i-W+1]==0 or c[i+W-1]==0 or c[i+W+1]==0):
                nx[i] = 0
    c = nx
me = c
print('收缩', ERODE, 'px ->', sum(me), f'{sum(me)/(W*H)*100:.1f}%')

# bbox
minx, miny, maxx, maxy = W, H, -1, -1
for y in range(H):
    for x in range(W):
        if me[y*W+x]:
            if x<minx: minx=x
            if x>maxx: maxx=x
            if y<miny: miny=y
            if y>maxy: maxy=y
print('bbox', minx, miny, maxx, maxy, 'w', maxx-minx+1, 'h', maxy-miny+1)

cw = max(maxx-minx+1, maxy-miny+1)
cx2 = (minx+maxx)//2; cy2 = (miny+maxy)//2
x0 = cx2-cw//2; y0 = cy2-cw//2

sq = bytearray(cw*cw*4)
for oy in range(cw):
    sy = y0+oy
    if sy < 0 or sy >= H: continue
    for ox in range(cw):
        sx = x0+ox
        if sx < 0 or sx >= W: continue
        i = sy*W+sx
        di = (oy*cw+ox)*4
        si = i*nch
        sq[di]=px[si]; sq[di+1]=px[si+1]; sq[di+2]=px[si+2]
        if me[i]:
            sq[di+3] = 255
        else:
            near = False
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    ny, nx = sy+dy, sx+dx
                    if 0<=ny<H and 0<=nx<W and me[ny*W+nx]:
                        near=True; break
                if near: break
            sq[di+3] = min(180, fg[i]) if near else 0
write_rgba(DST, cw, cw, sq)
print('->', DST, cw, 'x', cw, os.path.getsize(DST), 'bytes')
