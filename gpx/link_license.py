#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在版权行开头加「使用条款」链接，让 license.html 可从每页到达。幂等。"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OLD = '<br /><p class="copyright" id="baikal50-copyright">© 2025 贝加尔湖50径'
NEW = ('<br /><p class="copyright" id="baikal50-copyright">'
       '<a href="/license.html" style="color:inherit;text-decoration-color:#999;'
       'text-underline-offset:3px;">使用条款</a>　'
       '© 2025 贝加尔湖50径')

n = 0
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("._"):
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if "使用条款</a>" in t:
        continue
    if OLD in t:
        t = t.replace(OLD, NEW, 1)
        p.write_text(t, encoding="utf-8")
        n += 1
        print(f"  ✓ {p.name}")
print(f"共 {n} 页加条款链接")
