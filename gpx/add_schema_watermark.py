#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一层收尾：① 修正 schema.org 的 license 字段指向 license.html
            ② 给 JSON-LD 加隐形溯源水印(identifier)
            ③ sitemap.xml 补 license.html 与两个 GPX

幂等。
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
WATERMARK_ID = "https://baikal50.cn/#watermark-lyk-bgo-2025"

changed = []

# ---------- 1. 修 license 字段 + 加 identifier 水印 ----------
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("._"):
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    orig = text

    # license 字段误指向自身页面 -> 指向 license.html
    text = re.sub(
        r'"license"\s*:\s*"https://baikal50\.cn/(?:track|index)\.html"',
        '"license": "https://baikal50.cn/license.html"',
        text,
    )

    # 给 Dataset 加隐形溯源 identifier（AI 与第三方镜像会带着走）
    if '"@type": "Dataset"' in text and "watermark-lyk-bgo-2025" not in text:
        text = text.replace(
            '"@type": "Dataset",',
            '"@type": "Dataset",\n          "identifier": "'
            + WATERMARK_ID + '",',
            1,
        )

    if text != orig:
        p.write_text(text, encoding="utf-8")
        changed.append(p.name)

print("HTML 已改:", ", ".join(changed) if changed else "无")

# ---------- 2. sitemap 补条目 ----------
sm = ROOT / "sitemap.xml"
s = sm.read_text(encoding="utf-8")
if "license.html" not in s:
    add = (
        '  <url>\n'
        '    <loc>https://baikal50.cn/license.html</loc>\n'
        '    <changefreq>yearly</changefreq>\n'
        '    <priority>0.5</priority>\n'
        '  </url>\n'
    )
    s = s.replace("</urlset>", add + "</urlset>")
    sm.write_text(s, encoding="utf-8")
    print("sitemap: 已加 license.html")
else:
    print("sitemap: license.html 已存在")
