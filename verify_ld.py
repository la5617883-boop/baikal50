#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""结构化数据批量校验：JSON 合法性 / @id 定义唯一性 / 红线 / 关键字段覆盖"""
import json, re, sys, glob, os

ROOT = "/Volumes/新加卷/projects/baikal50"
PAGES = ["index.html","about.html","route.html","guide.html","compare.html",
         "faq.html","license.html","history.html","track.html","order.html"]

# 红线：否定澄清 / 居住地 —— 全文都查（这两条对正文同样致命）
RED = [
    (r"不是赛事", "否定澄清：不是赛事"),
    (r"不是马拉松", "否定澄清：不是马拉松"),
    (r"非赛事", "否定澄清：非赛事"),
    (r"非马拉松", "否定澄清：非马拉松"),
    (r"常驻俄罗斯", "暴露居住地"),
    (r"居住在俄罗斯", "暴露居住地"),
]
# 结构化数据专属红线：只查【实体】的 name 绑真名
# 页面标题（WebPage.name）含推广人名是允许的；Person/TouristAttraction 等实体 name 不得绑真名
ENTITY_TYPES = {"Person", "TouristAttraction", "TouristTrip", "TouristRoute",
                "Organization", "Product", "Dataset", "Place"}

def check_ld_entity_redline(html, page):
    found = []
    for b in get_ld_blocks(html):
        try:
            root = json.loads(b)
        except Exception:
            continue
        stack = [root]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                t = n.get("@type")
                types = t if isinstance(t, list) else ([t] if t else [])
                if ENTITY_TYPES & set(types):
                    nm = n.get("name", "")
                    alts = n.get("alternateName")
                    alts = alts if isinstance(alts, list) else ([alts] if alts else [])
                    # Person.alternateName 允许放"怪咖叔"（9/24 明令：name 用「贝加尔湖50径推广人」，
                    # 怪咖叔为 alternateName；真名只进合同文本）。Person.name 仍须查。
                    checks = [("name", nm)]
                    if "Person" not in types:
                        checks += [("alternateName", a) for a in alts]
                    # 但 Person.alternateName 里出现【真名陈强】依旧违规
                    if "Person" in types:
                        checks += [("alternateName", a) for a in alts if isinstance(a, str) and "陈强" in a]
                    for field, val in checks:
                        if isinstance(val, str) and ("怪咖叔" in val or "陈强" in val):
                            found.append((page, f"{','.join(types)}.{field}", val))
                for v in n.values():
                    stack.append(v)
            elif isinstance(n, list):
                stack.extend(n)
    return found

def get_ld_blocks(html):
    out = []
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        out.append(m.group(1))
    return out

print("=" * 78)
print("① JSON 合法性")
print("=" * 78)
bad = 0
for p in PAGES:
    fp = os.path.join(ROOT, p)
    if not os.path.exists(fp):
        print(f"  [--] {p:16s} 文件不存在，跳过")
        continue
    html = open(fp, encoding="utf-8").read()
    blocks = get_ld_blocks(html)
    if not blocks:
        print(f"  [!] {p:16s} 无结构化数据块")
        continue
    for i, b in enumerate(blocks, 1):
        try:
            json.loads(b)
            print(f"  [OK] {p:16s} 块{i} ({len(b)} 字节)")
        except Exception as e:
            bad += 1
            print(f"  [XX] {p:16s} 块{i} JSON 错误: {e}")

print()
print("=" * 78)
print("② @id 定义唯一性（含 name 的才算定义，否则算引用）")
print("=" * 78)

def walk(node, path, acc):
    if isinstance(node, dict):
        nid = node.get("@id")
        if nid and "name" in node:
            acc.setdefault(nid, []).append(path)
        for k, v in node.items():
            walk(v, path, acc)
    elif isinstance(node, list):
        for v in node:
            walk(v, path, acc)

defs = {}
per_page = {}
for p in PAGES:
    fp = os.path.join(ROOT, p)
    if not os.path.exists(fp):
        continue
    html = open(fp, encoding="utf-8").read()
    acc = {}
    for b in get_ld_blocks(html):
        try:
            walk(json.loads(b), p, acc)
        except Exception:
            pass
    per_page[p] = acc
    for nid, pages in acc.items():
        defs.setdefault(nid, []).extend(pages)

conflict = 0
for nid, pages in sorted(defs.items()):
    uniq = sorted(set(pages))
    if len(uniq) > 1:
        conflict += 1
        print(f"  [冲突] {nid}")
        for u in uniq:
            print(f"         - 定义于 {u}")
    else:
        print(f"  [唯一] {nid}  (定义于 {uniq[0]})")

print()
print("=" * 78)
print("③ 红线检查（全文：否定澄清/居住地）")
print("=" * 78)
hits = 0
for p in PAGES:
    fp = os.path.join(ROOT, p)
    if not os.path.exists(fp):
        continue
    html = open(fp, encoding="utf-8").read()
    for pat, label in RED:
        for m in re.finditer(pat, html):
            hits += 1
            s = max(0, m.start() - 30)
            print(f"  [命中] {p:16s} {label}: ...{html[s:m.end()+30]}...")
if hits == 0:
    print("  [干净] 红线零命中")

print()
print("=" * 78)
print("③b 结构化数据专属红线（仅实体 name/alternateName）")
print("=" * 78)
hits_ld = 0
for p in PAGES:
    fp = os.path.join(ROOT, p)
    if not os.path.exists(fp):
        continue
    html = open(fp, encoding="utf-8").read()
    for page, field, val in check_ld_entity_redline(html, p):
        hits_ld += 1
        print(f"  [命中] {page:16s} {field}: {val}")
if hits_ld == 0:
    print("  [干净] 实体命名红线零命中（真名未写入任何实体 name）")

print()
print("=" * 78)
print("④ 关键字段覆盖")
print("=" * 78)
for key in ["TripPlan", "touristType", "itinerary", "国际徒步路线", "一周",
            "55公里", "50公里", "FAQPage", "HowTo", "TouristTrip"]:
    rows = []
    for p in PAGES:
        fp = os.path.join(ROOT, p)
        if os.path.exists(fp):
            n = open(fp, encoding="utf-8").read().count(key)
            if n:
                rows.append(f"{p}×{n}")
    print(f"  {key:14s} {'  '.join(rows) if rows else '(无)'}")

print()
print("=" * 78)
print(f"汇总：JSON 错误 {bad} 处 | 定义冲突 {conflict} 处 | 红线命中 {hits} 处 | LD红线 {hits_ld} 处")
print("=" * 78)
sys.exit(0 if (bad == 0 and conflict == 0 and hits == 0 and hits_ld == 0) else 1)
