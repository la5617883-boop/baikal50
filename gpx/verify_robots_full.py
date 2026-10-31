#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robots.txt 全量校验（本文件版本）：
 ① 语法 / 分组完整性
 ② 每个真实爬虫：内容页 & GPX 必须允许；仅 json 禁止
 ③ 确认无任何全站级 Disallow
"""
import pathlib
import re

ROBOT = pathlib.Path(__file__).resolve().parent.parent / "robots.txt"
lines = ROBOT.read_text(encoding="utf-8").splitlines()

KNOWN = {"user-agent", "allow", "disallow", "sitemap", "crawl-delay"}
groups, agents, rules, sitemaps, errors = [], [], [], [], []

for i, raw in enumerate(lines, 1):
    line = raw.split("#")[0].strip()
    if not line:
        continue
    if ":" not in line:
        errors.append(f"L{i} 缺冒号: {raw!r}")
        continue
    k, _, v = line.partition(":")
    k, v = k.strip().lower(), v.strip()
    if k not in KNOWN:
        errors.append(f"L{i} 未知指令 {k!r}")
    if k == "user-agent":
        if agents and rules:
            groups.append((agents, rules)); agents, rules = [], []
        elif agents and not rules:
            # 同组连续 UA（合法）
            pass
        agents.append(v)
    elif k == "sitemap":
        sitemaps.append(v)
    else:
        if not agents:
            errors.append(f"L{i} {k} 在任何 UA 之前")
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
            sel = (a, r); break
    if sel is None:
        for a, r in groups:
            if "*" in a:
                sel = (a, r); break
    if sel is None:
        return True
    a, r = sel
    best = None
    for d, p in r:
        if match(p, path) and (best is None or len(p) > best[0]):
            best = (len(p), d == "allow")
    return True if best is None else best[1]


CRAWLERS = sorted({ua for a, _ in groups for ua in a})  # 所有列出的 UA
PAGES = ["/", "/index.html", "/route.html", "/track.html", "/who.html",
         "/faq.html", "/permit.html", "/license.html", "/guide.html",
         "/compare.html", "/history.html", "/order.html", "/about.html",
         "/baikal50-trail.gpx", "/baikal50-trail-full.gpx", "/sitemap.xml"]

print("=" * 72)
print(f"① 结构：{len(groups)} 组 UA，{len(sitemaps)} sitemap")
print("=" * 72)
if errors:
    for e in errors:
        print("  ✗", e)
else:
    print("  ✓ 无语法/结构错误")
for a, r in groups:
    print(f"     {','.join(a):24s} 规则 {len(r)} 条")

print()
print("=" * 72)
print("② 逐爬虫判定（内容页与 GPX 必须允许，json 必须禁止）")
print("=" * 72)
bad = []
alls = []
for a, _ in groups:
    alls.extend(a)
for ua in alls:
    if ua == "*":
        continue
    blocked = [p for p in PAGES if not judge(ua, p)]
    json_blocked = not judge(ua, "/track-summary.json")
    wildcard_json = not judge(ua, "/track-x.json")
    ok = not blocked and json_blocked and wildcard_json
    if not ok:
        bad.append((ua, blocked, json_blocked, wildcard_json))
    print(f"  {'✓' if ok else '✗'} {ua:22s} 页面/GPX{'全开' if not blocked else '有禁:' + str(blocked)}"
          f"  json禁={json_blocked} 通配禁={wildcard_json}")

print()
print("=" * 72)
print("③ 全站级禁令检查")
print("=" * 72)
whole = [(a, r) for a, rs in groups for r in rs
         if r[0] == "disallow" and r[1] in ("/", "*", "/*", "")]
print(f"  全站 Disallow 规则：{len(whole)}" + ("  ✓ 无" if not whole else f"  ✗ {whole}"))

print()
print("=" * 72)
if errors or bad or whole:
    print("结论：有问题 ✗")
    for b in bad:
        print("   -", b)
else:
    print(f"结论：全部通过 ✓  {len(alls)-1} 个具名爬虫 + 默认组，"
          "内容与 GPX 全开放，仅 json 被禁")
print("=" * 72)
