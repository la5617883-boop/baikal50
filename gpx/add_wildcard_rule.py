#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给具名爬虫组统一补 /track-*.json 通配禁令（幂等）。
具名组原本只禁 track-summary.json，未覆盖同类新文件；补后与默认组一致。"""
import pathlib
import re

p = pathlib.Path(__file__).resolve().parent.parent / "robots.txt"
t = p.read_text(encoding="utf-8")

# 每个具名组的末尾 "Disallow: /track-summary.json" 后补通配行
# 但不动最后的 "*" 组（它已有）
lines = t.splitlines()
out, added = [], 0
for i, line in enumerate(lines):
    out.append(line)
    if line.strip() == "Disallow: /track-summary.json":
        # 往前找本组的 UA（到上一个 User-agent 为止）
        j = len(out) - 2
        ua = ""
        while j >= 0:
            s = out[j].strip()
            if s.lower().startswith("user-agent:"):
                ua = s.split(":", 1)[1].strip()
                break
            j -= 1
        if ua != "*":
            # 检查下一行是否已是通配
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if nxt != "Disallow: /track-*.json":
                out.append("Disallow: /track-*.json")
                added += 1

p.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"已为 {added} 个具名爬虫组补通配禁令")
