#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""线上口径验证：50/55 分布"""
import re, os

print("=" * 72)
print("线上口径验证（2026-09-27 定案：统一 50）")
print("=" * 72)

pages = {}
for p in ["index","route","who","track","compare","about","guide","faq"]:
    fp = f"/tmp/F_{p}.html"
    if not os.path.exists(fp):
        fp = f"/tmp/L_{p}.html"
    if os.path.exists(fp):
        pages[p] = open(fp, encoding="utf-8").read()

print("\n【结构化数据内的 55 引用】")
bad = 0
for p, html in pages.items():
    for i, b in enumerate(re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S), 1):
        if "55公里" in b or "55 公里" in b or "官方口径为55" in b:
            bad += 1
            print(f"  [命中] {p}.html 块{i}")
print("  [干净] 线上结构化数据零 55 引用" if bad == 0 else f"  {bad} 处待清")

print("\n【55公里 全站分布】")
for p, html in pages.items():
    n = html.count("55公里") + html.count("55 公里")
    if n:
        print(f"  {p}.html ×{n}")
print("  （仅 track 数据页，按约定保留作客观数据陈述）")

print("\n【50公里 全站分布】")
tot = 0
for p, html in pages.items():
    n = html.count("50公里") + html.count("50 公里")
    tot += n
    if n:
        print(f"  {p:12s} ×{n}")
print(f"  合计 {tot} 处")

print("\n【who 页里程口径段（应已删55）】")
w = pages.get("who","")
m = re.search(r'关于里程口径.{0,240}', w, re.S)
if m:
    txt = re.sub(r'<[^>]+>', '', m.group(0))
    print("  " + txt.strip()[:220])

print("\n【index 结构化数据 description（应无55）】")
i = pages.get("index","")
m = re.search(r'"description": "(贝加尔湖50径[^"]{0,300})', i)
if m:
    d = m.group(1)
    print(f"  含'55': {'是' if '55' in d else '否'}")
    print("  " + d[:180] + "...")
