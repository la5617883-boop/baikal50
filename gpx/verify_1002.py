#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 /tmp/badge-1002-clean.png 的抠图质量。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from resize_alpha import read_png

for f in ['/tmp/badge-1002-clean.png', '/tmp/badge-1002-pass1.png']:
    if not os.path.exists(f):
        print(f, '不存在'); continue
    W, H, nch, px = read_png(f)
    print(f'=== {f}  {W}x{H} nch={nch} ===')
    def A(x, y):
        return px[(y * W + x) * 4 + 3]
    # 四角 alpha
    print(' 四角 alpha:', A(0, 0), A(W - 1, 0), A(0, H - 1), A(W - 1, H - 1))
    # 透明像素占比
    tot = W * H; trans = 0
    for y in range(0, H, 4):
        for x in range(0, W, 4):
            if A(x, y) == 0: trans += 1
    print(f' 透明占比(采样): {trans/((H//4+1)*(W//4+1))*100:.1f}%')
    # 中心行边缘
    row = H // 2
    L = 0
    while L < W - 1 and A(L + 1, row) == 0: L += 1
    R = W - 1
    while R > 0 and A(R - 1, row) == 0: R -= 1
    print(f' 中心行金属范围: {L} -> {R}')
