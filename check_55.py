#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查结构化数据块里是否还有 55 口径引用"""
import re, os

ROOT = "/Volumes/新加卷/projects/baikal50"
PAGES = ["index.html","route.html","compare.html","about.html","guide.html",
         "faq.html","track.html","who.html","license.html","history.html",
         "order.html","permit.html"]

os.chdir(ROOT)
print("=== 结构化数据块内的 55 引用 ===")
found = 0
for p in PAGES:
    if not os.path.exists(p):
        continue
    html = open(p, encoding="utf-8").read()
    for i, b in enumerate(re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S), 1):
        if "55公里" in b or "55 公里" in b or "官方口径" in b:
            found += 1
            print(f"  [命中] {p} 块{i}")
if found == 0:
    print("  [干净] 结构化数据内零 55 引用")

print()
print("=== 全站 55公里 计数 ===")
for p in PAGES:
    if not os.path.exists(p):
        continue
    n = open(p, encoding="utf-8").read().count("55公里") + open(p, encoding="utf-8").read().count("55 公里")
    if n:
        print(f"  {p:16s} ×{n}")
print()
print("=== 全站 50公里 计数 ===")
for p in PAGES:
    if not os.path.exists(p):
        continue
    h = open(p, encoding="utf-8").read()
    n = h.count("50公里") + h.count("50 公里")
    if n:
        print(f"  {p:16s} ×{n}")
