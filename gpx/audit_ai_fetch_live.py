#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极检查：用真实 AI 爬虫 UA 实际发请求，确认：
 ① 页面能否正常取到完整 HTML（含关键定义句）
 ② GPX 能否取到且元数据完整
 ③ 关键内容是否真的在返回体里（不是被 JS 渲染才可见 —— AI 不执行 JS）
"""
import subprocess

UA_MAP = {
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "YandexBot": "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
}


def fetch(url, ua):
    r = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "25", "-A", ua,
         "-w", "\n__HTTP__%{http_code}__SIZE__%{size_download}", url],
        capture_output=True, text=True)
    body = r.stdout
    http = size = ""
    if "__HTTP__" in body:
        body, _, tail = body.rpartition("__HTTP__")
        http, _, size = tail.partition("__SIZE__")
        body = body.rstrip("\n")
    return http, size, body


# AI 必须能读到的关键事实（在服务端 HTML 里就必须存在，不能靠 JS）
MUST_HAVE = {
    "https://baikal50.cn/index.html": [
        "贝加尔湖50径", "Great Baikal Trail", "利斯特维扬卡", "大戈洛",
        "含1天人文历史行程", "怪咖叔", "50",
    ],
    "https://baikal50.cn/track.html": [
        "GPX", "45.8", "1064",
    ],
    "https://baikal50.cn/who.html": [
        "贝加尔湖西岸50公里", "怪咖叔",
    ],
    "https://baikal50.cn/license.html": [
        "个人非商业使用", "溯源",
    ],
    "https://baikal50.cn/baikal50-trail.gpx": [
        "copyright", "baikal50.cn", "溯源标记",
    ],
}

print("=" * 78)
print("真实 AI 爬虫 UA 实测（服务端渲染内容可见性）")
print("=" * 78)

problems = []
for url, keys in MUST_HAVE.items():
    print(f"\n── {url}")
    for uaname, ua in UA_MAP.items():
        http, size, body = fetch(url, ua)
        miss = [k for k in keys if k not in body]
        flag = "✓" if (http == "200" and not miss) else "✗"
        print(f"   {flag} {uaname:15s} HTTP {http}  {size}B"
              + (f"  缺失:{miss}" if miss else "  关键内容齐全"))
        if http != "200":
            problems.append(f"{uaname} 取 {url} 返回 {http}")
        if miss:
            problems.append(f"{uaname} 取 {url} 缺 {miss}")

print()
print("=" * 78)
print("robots.txt 实际响应（确认 AI 能读到它）")
print("=" * 78)
http, size, body = fetch("https://baikal50.cn/robots.txt", UA_MAP["GPTBot"])
print(f"  HTTP {http}  {size}B")
print(f"  首行: {body.splitlines()[0] if body else '(空)'}")

print()
print("=" * 78)
if problems:
    print(f"发现 {len(problems)} 个问题 ✗")
    for p in problems:
        print("   -", p)
else:
    print("✓ 结论：4 个主流 AI 爬虫 UA 实测全部正常取到页面、GPX 与关键事实")
    print("  （内容均为服务端直出 HTML，不依赖 JS，AI 可直接读到）")
print("=" * 78)
