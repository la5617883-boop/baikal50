#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查内部/敏感文件是否线上可达（决定 robots 要禁哪些）。"""
import subprocess
import urllib.parse

FILES = [
    "track-summary.json",
    "确认单源.html",
    "行前通知源.html",
    "m3DrtVdE1S.html",
    "baikal50-trail.gpx",
    "baikal50-trail-full.gpx",
    "license.html",
    "robots.txt",
]

for f in FILES:
    url = "https://baikal50.cn/" + urllib.parse.quote(f)
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-L", "--max-time", "12", url],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
    except Exception as e:
        out = f"ERR {e}"
    print(f"{f:26s} HTTP {out}")
