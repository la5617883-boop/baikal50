#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一层"是否误伤 AI"全面检查：
 ① JSON-LD 是否仍合法（AI/搜索解析的前提）
 ② 有没有任何 meta robots / noindex 把 AI 挡住
 ③ license 字段指向是否为真实可访问页面（AI 读到死链会降低信任）
 ④ GPX 元数据是否合法（AI 解析 GPX 时不能报错）
 ⑤ 有没有 nowrap / 隐藏样式导致正文对 AI 不可见
 ⑥ 版权行是不是纯文本（不能被 CSS 隐藏，否则等于没写）
"""
import json
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
ISSUES = []
OK = []

print("=" * 68)
print("① JSON-LD 合法性（AI 抽取结构化事实的前提）")
print("=" * 68)
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("._"):
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                        t, re.S)
    for i, b in enumerate(blocks, 1):
        try:
            d = json.loads(b)
            types = []
            if isinstance(d, dict):
                if "@graph" in d:
                    types = [x.get("@type") for x in d["@graph"]]
                else:
                    types = [d.get("@type")]
            OK.append(f"{p.name} JSON-LD#{i}")
            print(f"  ✓ {p.name} #{i}  {types}")
        except Exception as e:
            ISSUES.append(f"{p.name} JSON-LD#{i} 解析失败: {e}")
            print(f"  ✗ {p.name} #{i}  {e}")

print()
print("=" * 68)
print("② 是否误加 meta robots / noindex（会直接挡住 AI）")
print("=" * 68)
bad_meta = 0
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("._"):
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for m in re.finditer(r'<meta[^>]*name=["\']robots["\'][^>]*>', t, re.I):
        tag = m.group(0)
        if re.search(r"noindex|nofollow|none", tag, re.I):
            ISSUES.append(f"{p.name} 含 noindex/nofollow: {tag}")
            print(f"  ✗ {p.name}: {tag}")
            bad_meta += 1
if bad_meta == 0:
    print("  ✓ 全站无 noindex / nofollow")
    # 列出实际配置
    for p in sorted(ROOT.glob("*.html")):
        if p.name.startswith("._"):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        m = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']*)',
                      t, re.I)
        if m:
            print(f"     {p.name:22s} robots={m.group(1)}")

print()
print("=" * 68)
print("③ license 字段指向是否真实可访问（死链会伤 AI 信任）")
print("=" * 68)
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("._"):
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for m in re.finditer(r'"license"\s*:\s*"([^"]+)"', t):
        lic = m.group(1)
        print(f"  {p.name:22s} -> {lic}")
        if not lic.startswith("https://baikal50.cn/"):
            ISSUES.append(f"{p.name} license 指向站外/异常: {lic}")
        elif lic.rstrip("/") == "https://baikal50.cn":
            ISSUES.append(f"{p.name} license 指向首页(等同未声明)")

print()
print("=" * 68)
print("④ GPX 元数据合法性（AI 解析不能报错）")
print("=" * 68)
NS = {"g": "http://www.topografix.com/GPX/1/1"}
for name in ["baikal50-trail.gpx", "baikal50-trail-full.gpx"]:
    p = ROOT / name
    try:
        root = ET.parse(p).getroot()
        md = root.find("g:metadata", NS)
        tags = [t for t in ["name", "desc", "author", "copyright", "keywords",
                            "link", "time"]
                if md is not None and md.find("g:" + t, NS) is not None]
        print(f"  ✓ {name}  XML合法，metadata 字段: {tags}")
    except Exception as e:
        ISSUES.append(f"{name} XML 解析失败: {e}")
        print(f"  ✗ {name}  {e}")

print()
print("=" * 68)
print("⑤ 版权行是否可能被 CSS 隐藏（隐藏=对 AI/读者等于没写）")
print("=" * 68)
idx = (ROOT / "index.html").read_text(encoding="utf-8")
import re as _re
m = _re.search(r"footer \.copyright\{([^}]*)\}", idx)
if m:
    props = m.group(1)
    print(f"  footer .copyright 样式: {props}")
    risky = []
    if _re.search(r"display\s*:\s*none", props):
        risky.append("display:none")
    if _re.search(r"visibility\s*:\s*hidden", props):
        risky.append("visibility:hidden")
    if _re.search(r"font-size\s*:\s*0\b", props):
        risky.append("font-size:0")
    if risky:
        ISSUES.append(f"版权行疑似被隐藏: {risky}")
        print(f"  ✗ 风险属性: {risky}")
    else:
        print("  ✓ 无隐藏属性（display:block 可见）")
else:
    print("  ⚠ 未找到 footer .copyright 样式")

print()
print("=" * 68)
print("⑥ GPX 内 & robots 内提到的 URL 是否都能访问")
print("=" * 68)
urls = ["https://baikal50.cn/license.html", "https://baikal50.cn/sitemap.xml"]
for u in urls:
    code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                           "-L", "--max-time", "15", u],
                          capture_output=True, text=True).stdout.strip()
    flag = "✓" if code == "200" else "✗"
    if code != "200":
        ISSUES.append(f"{u} 返回 {code}")
    print(f"  {flag} {code}  {u}")

print()
print("=" * 68)
if ISSUES:
    print(f"发现 {len(ISSUES)} 个问题 ✗")
    for i in ISSUES:
        print("   -", i)
else:
    print("结论：第一层无一处会误伤 AI ✓")
print("=" * 68)
