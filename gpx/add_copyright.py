#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性脚本：给全站 HTML 页面页脚统一追加版权/使用条款一行。
幂等：已含标记的不重复插入。
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKER = "baikal50-copyright"

# 版权声明（简体中文，风格与站点统一的极简调性一致）
NOTICE_HTML = (
    '<p class="copyright" id="baikal50-copyright">'
    '© 2025 贝加尔湖50径 · baikal50.cn　保留所有权利。'
    '欢迎个人非商业使用（导航、行程参考、引用转载须注明来源 baikal50.cn）；'
    '商业使用须事先获得书面许可。'
    '</p>'
)

NOTICE_STYLE = (
    "footer .copyright{letter-spacing:0;text-indent:0;margin:14px 0 0;"
    "font-size:.92em;line-height:1.7;opacity:.8;}"
)


def patch_html(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return "skip(已有)"
    if "</footer>" not in text:
        return "skip(无 footer)"

    # 1) 注入样式（若有 <style> 块，插到第一个 </style> 前）
    if "</style>" in text and NOTICE_STYLE not in text:
        text = text.replace("</style>", "    " + NOTICE_STYLE + "\n</style>", 1)

    # 2) 在最后一个 </footer> 前插入版权行
    idx = text.rfind("</footer>")
    text = text[:idx] + "        " + NOTICE_HTML + "\n    " + text[idx:]

    path.write_text(text, encoding="utf-8")
    return "ok"


def main():
    targets = sorted(ROOT.glob("*.html"))
    # 跳过验证文件、macOS 资源分叉(._开头)等噪音
    targets = [p for p in targets
               if not p.name.startswith("._")
               and not re.match(r"^(baidu_verify_|google)", p.name)
               and p.name not in ("m3DrtVdE1S.html",)]
    for p in targets:
        try:
            print(f"{p.name:26s} {patch_html(p)}")
        except Exception as e:
            print(f"{p.name:26s} ERROR {e}")


if __name__ == "__main__":
    main()
