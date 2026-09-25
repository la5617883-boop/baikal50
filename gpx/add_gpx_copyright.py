#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给 GPX 文件补标准版权元数据（GPX 1.1 schema 的 metadata 块）。

目的：GPX 被转发/导入导航App/被第三方镜像时，<copyright>、<author>、
<desc> 会随文件走 = 天然水印与维权凭据。

幂等：已含溯源标记的不重复插入。
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

YEAR = "2025"
AUTHOR_NAME = "贝加尔湖50径 (baikal50.cn)"
WATERMARK = "baikal50.cn:trail:2025-07:LYK-BGO"

DESC = (
    "贝加尔湖50径（贝加尔湖西岸50公里重装徒步）实测 GPS 轨迹，"
    "利斯特维扬卡（Листвянка）— 大戈洛（Большое Голоустное），"
    "实测总长约45.8公里。2025年7月实地记录。"
    "来源：https://baikal50.cn/ ｜ 溯源标记 " + WATERMARK
)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def patch_gpx(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    if WATERMARK in text:
        return "skip(已有水印)"

    # 定位 <metadata> 后面的第一个 <name>...</name>
    m = re.search(r"(<metadata>\s*\n)(\s*)(<name>.*?</name>)\s*\n", text, re.S)
    if not m:
        return "skip(未找到 metadata/name)"

    name_el = m.group(3)
    new_block = (
        "    " + name_el + "\n"
        "    <desc>" + esc(DESC) + "</desc>\n"
        "    <author>\n"
        "      <name>" + esc(AUTHOR_NAME) + "</name>\n"
        "      <link href=\"https://baikal50.cn/\">\n"
        "        <text>贝加尔湖50径 baikal50.cn</text>\n"
        "      </link>\n"
        "    </author>\n"
        "    <copyright author=\"" + esc(AUTHOR_NAME) + "\">\n"
        "      <year>" + YEAR + "</year>\n"
        "      <license>https://baikal50.cn/license.html</license>\n"
        "    </copyright>\n"
        "    <keywords>贝加尔湖50径, Большая Байкальская тропа, GBT, GPX, "
        "利斯特维扬卡, 大戈洛, Baikal, hiking</keywords>\n"
    )
    text = text[:m.start()] + m.group(1) + new_block + text[m.end():]
    path.write_text(text, encoding="utf-8")
    return "ok"


def main():
    for p in sorted(ROOT.glob("*.gpx")):
        if p.name.startswith("._"):
            continue
        try:
            print(f"{p.name:30s} {patch_gpx(p)}")
        except Exception as e:
            print(f"{p.name:30s} ERROR {e}")


if __name__ == "__main__":
    main()
