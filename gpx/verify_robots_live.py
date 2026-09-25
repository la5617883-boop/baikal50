#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""线上最终验收：抓真实 robots.txt，解析并对关键路径判定。"""
import re
import subprocess

url = "https://baikal50.cn/robots.txt"
txt = subprocess.run(["curl", "-s", "-L", "--max-time", "20", url],
                     capture_output=True, text=True).stdout

groups, agents, rules, sitemaps = [], [], [], []
for raw in txt.splitlines():
    line = raw.split("#")[0].strip()
    if not line or ":" not in line:
        continue
    k, _, v = line.partition(":")
    k, v = k.strip().lower(), v.strip()
    if k == "user-agent":
        if agents and rules:
            groups.append((agents, rules))
            agents, rules = [], []
        agents.append(v)
    elif k == "sitemap":
        sitemaps.append(v)
    elif k in ("allow", "disallow"):
        rules.append((k, v))
if agents:
    groups.append((agents, rules))


def match(pat, path):
    if not pat:
        return False
    rx = "^" + "".join(".*" if c == "*" else "$" if c == "$" else re.escape(c)
                       for c in pat)
    if not pat.endswith("$"):
        rx += ".*"
    return re.search(rx, path) is not None


def judge(ua, path):
    sel = None
    for a, r in groups:
        if ua in a:
            sel = (a, r)
            break
    if sel is None:
        for a, r in groups:
            if "*" in a:
                sel = (a, r)
                break
    if sel is None:
        return True
    a, r = sel
    best = None
    for d, p in r:
        if match(p, path) and (best is None or len(p) > best[0]):
            best = (len(p), d == "allow")
    return True if best is None else best[1]


CASES = [
    ("Googlebot", "/", True), ("Googlebot", "/route.html", True),
    ("Googlebot", "/track.html", True),
    ("Googlebot", "/baikal50-trail.gpx", True),
    ("Googlebot", "/track-summary.json", False),
    ("GPTBot", "/index.html", True), ("GPTBot", "/who.html", True),
    ("GPTBot", "/baikal50-trail.gpx", True),
    ("GPTBot", "/track-summary.json", False),
    ("ClaudeBot", "/baikal50-trail.gpx", True),
    ("PerplexityBot", "/track.html", True),
    ("YandexBot", "/baikal50-trail-full.gpx", True),
    ("*", "/track-other.json", False), ("*", "/license.html", True),
]

print(f"线上 {url}  解析出 {len(groups)} 组，{len(sitemaps)} sitemap")
print("-" * 66)
bad = 0
for ua, path, exp in CASES:
    got = judge(ua, path)
    ok = got == exp
    bad += 0 if ok else 1
    print(f"  {'✓' if ok else '✗'} {ua:14s} {path:26s} {'允许' if got else '禁止'}")
print("-" * 66)
print(f"Sitemap: {sitemaps}")
print(f"结论：{'全部通过 ✓' if not bad else f'失败 {bad} 项 ✗'}")
