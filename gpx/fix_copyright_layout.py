#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正：版权 <p> 前面缺换行，导致与页脚文字同排渲染。
给该行加 <br/> 前缀并强制 block 显示。
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKER = "baikal50-copyright"

OLD_STYLE = "footer .copyright{letter-spacing:0;text-indent:0;margin:14px 0 0;"
NEW_STYLE = ("footer .copyright{display:block;width:100%;letter-spacing:0;"
             "text-indent:0;margin:14px 0 0;")

count = 0
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("._"):
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    orig = text
    # 样式强化：确保块级
    text = text.replace(OLD_STYLE, NEW_STYLE)
    # 在版权行前补换行标签，避免与前面行内元素同排
    if MARKER in text:
        text = text.replace('<p class="copyright"',
                            '<br /><p class="copyright"')
    if text != orig:
        p.write_text(text, encoding="utf-8")
        count += 1

print(f"已修正 {count} 个文件")
