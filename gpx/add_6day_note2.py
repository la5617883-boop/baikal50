#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补漏第二批：who.html:150 正文定义句 + index.html meta description + index FAQ。
（先跑 add_6day_note.py 时漏掉的位置）
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

EDITS = [
    # who.html 正文定义句（与 190 行同段两个版本，前一版漏改）
    ("who.html",
     "从利斯特维扬卡（Листвянка）到大戈洛（Большое Голоустное），3天徒步、全程6天，全程位于贝加尔国家公园（Прибайкальский национальный парк）内。</strong>",
     "从利斯特维扬卡（Листвянка）到大戈洛（Большое Голоустное），3天徒步、全程6天（含1天人文历史行程），全程位于贝加尔国家公园（Прибайкальский национальный парк）内。</strong>"),

    # index.html meta description
    ("index.html",
     "50公里，3天徒步全程6天。国家公园内成熟路线",
     "50公里，3天徒步全程6天（含1天人文历史行程）。国家公园内成熟路线"),

    # index.html FAQ 定义句
    ("index.html",
     "从利斯特维扬卡到大戈洛，3天徒步、全程6天，绝大部分路段无手机信号。",
     "从利斯特维扬卡到大戈洛，3天徒步、全程6天（含1天人文历史行程），绝大部分路段无手机信号。"),
]

for fname, old, new in EDITS:
    p = ROOT / fname
    t = p.read_text(encoding="utf-8")
    cnt = t.count(old)
    if cnt == 0:
        print(f"{fname}: 未命中 -> {old[:40]}…")
        continue
    t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print(f"{fname}: 替换 {cnt} 处 ✓")
