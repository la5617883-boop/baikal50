#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交付前验证：① JSON-LD 合法性 ② 版权覆盖 ③ 页脚结构 ④ GPX 合法性"""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
fails = []

print("=" * 62)
print("①  JSON-LD 合法性")
print("=" * 62)
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("._"):
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for i, m in enumerate(re.finditer(
            r'<script type="application/ld\+json">(.*?)</script>', text, re.S), 1):
        try:
            json.loads(m.group(1))
        except Exception as e:
            fails.append(f"{p.name} JSON-LD#{i}: {e}")
            print(f"  ✗ {p.name} #{i}: {e}")
        else:
            print(f"  ✓ {p.name} JSON-LD#{i}")

print()
print("=" * 62)
print("②  版权署名覆盖（footer 内应含 baikal50-copyright）")
print("=" * 62)
pages = [p for p in sorted(ROOT.glob("*.html"))
         if not p.name.startswith("._")
         and not re.match(r"^(baidu_verify_|google)", p.name)
         and p.name not in ("m3DrtVdE1S.html",)]
miss = []
for p in pages:
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    has_footer = "</footer>" in t
    has_cr = "baikal50-copyright" in t
    if not (has_footer and has_cr):
        miss.append(p.name)
        fails.append(f"{p.name} 缺版权行")
        print(f"  ✗ {p.name}  footer={has_footer} copyright={has_cr}")
print(f"  共 {len(pages)} 页，缺失 {len(miss)} 页"
      + ("" if miss else "  ✓ 全覆盖"))

print()
print("=" * 62)
print("③  页脚标签配对")
print("=" * 62)
for p in [ROOT / n for n in ["index.html", "track.html", "license.html", "faq.html"]]:
    t = p.read_text(encoding="utf-8")
    o, c = t.count("<footer"), t.count("</footer>")
    ok = "✓" if o == c else "✗"
    if o != c:
        fails.append(f"{p.name} footer 不配对 {o}/{c}")
    print(f"  {ok} {p.name}: <footer>={o} </footer>={c}")

print()
print("=" * 62)
print("④  GPX 合法性与元数据")
print("=" * 62)
NS = {"g": "http://www.topografix.com/GPX/1/1"}
for name in ["baikal50-trail.gpx", "baikal50-trail-full.gpx"]:
    p = ROOT / name
    try:
        root = ET.parse(p).getroot()
    except Exception as e:
        fails.append(f"{name} XML: {e}")
        print(f"  ✗ {name}: {e}")
        continue
    md = root.find("g:metadata", NS)
    have = [tag for tag in ["name", "desc", "author", "copyright", "keywords"]
            if md is not None and md.find("g:" + tag, NS) is not None]
    wm = "baikal50.cn:trail" in p.read_text(encoding="utf-8")
    ok = len(have) == 5 and wm
    print(f"  {'✓' if ok else '✗'} {name}: 元数据 {len(have)}/5, 水印={'有' if wm else '无'}")
    if not ok:
        fails.append(f"{name} 元数据不全")

print()
print("=" * 62)
print(f"结论：{'全部通过 ✓' if not fails else '失败 ' + str(len(fails)) + ' 项 ✗'}")
for f in fails:
    print("   -", f)
print("=" * 62)
