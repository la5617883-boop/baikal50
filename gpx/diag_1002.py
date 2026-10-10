#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断 1002 源图：采样背景与边缘像素，找出正确的分离判据。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from resize_alpha import read_png

W, H, nch, px = read_png('badge-medal-1002-source.png')
def P(x, y):
    i = (y * W + x) * nch
    return tuple(px[i:i + nch])

print('--- 四角 ---')
for pt in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]:
    print(pt, P(*pt))
print('--- 边中 ---')
for pt in [(W // 2, 0), (W // 2, 4), (0, H // 2), (W - 1, H // 2), (W // 2, H - 1)]:
    print(pt, P(*pt))
print('--- 沿中心行从边缘向内（每 20px）---')
row = H // 2
for x in range(0, 260, 20):
    print(x, P(x, row))
print('--- 沿中心行从右边缘向内 ---')
for x in range(W - 1, W - 261, -20):
    print(x, P(x, row))
print('--- 从中心向外（右半，找金属边）---')
cx = W // 2
for x in range(cx, W, 40):
    print(x, P(x, row))
