#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""精简版：只测最关键的 4 个组合，短超时。"""
import subprocess

GPTBOT = ("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
          "GPTBot/1.2; +https://openai.com/gptbot")

CASES = [
    ("https://baikal50.cn/index.html",
     ["贝加尔湖50径", "Great Baikal Trail", "含1天人文历史行程", "怪咖叔"]),
    ("https://baikal50.cn/baikal50-trail.gpx",
     ["copyright", "baikal50.cn", "溯源标记"]),
    ("https://baikal50.cn/track.html", ["GPX", "45.8"]),
    ("https://baikal50.cn/robots.txt", ["GPTBot", "track-summary"]),
]

print(f"以 GPTBot UA 实测（超时 25s/次）\n")
bad = 0
for url, keys in CASES:
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "25", "-A", GPTBOT,
             "-o", "/tmp/_ai_body.txt", "-w", "%{http_code} %{size_download}", url],
            capture_output=True, text=True, timeout=35)
        http, size = (r.stdout.strip().split() + ["", ""])[:2]
        body = open("/tmp/_ai_body.txt", encoding="utf-8", errors="replace").read()
        miss = [k for k in keys if k not in body]
        ok = http == "200" and not miss
        bad += 0 if ok else 1
        print(f"  {'✓' if ok else '✗'} HTTP {http}  {size}B  {url}")
        print(f"      {'关键内容齐全' if not miss else '缺失: ' + str(miss)}")
    except subprocess.TimeoutExpired:
        bad += 1
        print(f"  ✗ 超时  {url}")

print(f"\n结论：{'全部通过 ✓' if bad == 0 else f'{bad} 项失败 ✗'}")
