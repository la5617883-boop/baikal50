#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二层"是否误伤 AI"检查：
 ① 抓线上真实 robots.txt 解析
 ② 对每个真实 AI/搜索爬虫 UA 判定：页面允许？GPX 允许？只禁 json？
 ③ 反向确认：有没有哪个 AI 爬虫被整站 Disallow
 ④ 检查是否误伤 sitemap、图片、license
"""
import re
import subprocess

txt = subprocess.run(
    ["curl", "-s", "-L", "--max-time", "20", "https://baikal50.cn/robots.txt"],
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
            groups.append((agents, rules)); agents, rules = [], []
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


# 最可能来抓我们的真实 AI / 搜索爬虫
CRAWLERS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",
    "ClaudeBot", "Claude-Web", "anthropic-ai",
    "PerplexityBot", "Perplexity-User",
    "Googlebot", "Google-Extended", "Bingbot", "Baiduspider",
    "YandexBot", "Applebot", "Applebot-Extended",
    "CCBot", "Bytespider", "Amazonbot", "DuckDuckBot",
    "meta-externalagent", "cohere-ai", "YouBot",
]

# 必须允许的路径（放开=不误伤）
MUST_ALLOW = ["/", "/index.html", "/route.html", "/track.html", "/who.html",
              "/faq.html", "/permit.html", "/license.html", "/guide.html",
              "/compare.html", "/history.html", "/order.html", "/about.html",
              "/baikal50-trail.gpx", "/baikal50-trail-full.gpx",
              "/sitemap.xml"]

print("=" * 74)
print("线上 robots.txt 对每个 AI/搜索爬虫的判定")
print("=" * 74)
print(f"解析出 {len(groups)} 组 UA, {len(sitemaps)} sitemap\n")

blocked_any = []
for ua in CRAWLERS:
    disallowed = [p for p in MUST_ALLOW if not judge(ua, p)]
    json_ok = judge(ua, "/track-summary.json")
    status = "✓" if not disallowed else "✗"
    note = ""
    if disallowed:
        note = f"  <-- 误伤: {disallowed}"
        blocked_any.append((ua, disallowed))
    if json_ok:
        note += "  <-- json 未被禁?!"
        blocked_any.append((ua, ["json 未禁"]))
    print(f"  {status} {ua:22s} 内容页/GPX 全允许={not disallowed}"
          f"  json已禁={not json_ok}{note}")

print()
print("=" * 74)
print("结论")
print("=" * 74)
if blocked_any:
    print(f"  ✗ 发现 {len(blocked_any)} 处问题：")
    for ua, ps in blocked_any:
        print(f"     {ua}: {ps}")
else:
    print("  ✓ 全部 22 个 AI/搜索爬虫：内容页与 GPX 均允许，仅 json 被禁")
    print("  ✓ 没有任何爬虫被整站 Disallow")

# 额外：确认没有 Disallow: / 这种全站禁令
whole = [r for a, rs in groups for r in rs
         if r[0] == "disallow" and r[1] in ("/", "*", "/*")]
print()
print(f"  全站级 Disallow 规则数：{len(whole)}"
      + ("  ✓ 无" if not whole else f"  ✗ {whole}"))
