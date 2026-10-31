#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 GPX 元数据注入结果：XML 合法性 + 各字段存在性。"""
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
NS = {"g": "http://www.topografix.com/GPX/1/1"}

for name in ["baikal50-trail.gpx", "baikal50-trail-full.gpx"]:
    p = ROOT / name
    try:
        root = ET.parse(p).getroot()
        md = root.find("g:metadata", NS)
        print(f"{name}  XML合法 ✓")
        for tag in ["name", "desc", "author", "copyright", "keywords"]:
            el = md.find("g:" + tag, NS) if md is not None else None
            if el is None:
                print(f"    {tag:10s} 缺失 ✗")
            else:
                txt = (el.text or el.find("g:name", NS).text or "").strip()
                txt = txt.replace("\n", " ")[:70]
                print(f"    {tag:10s} ✓  {txt}")
    except Exception as e:
        print(f"{name}  XML错误: {e}")
    print()
