#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""线上三层漏斗验证（抓真实线上文件）"""
import json, re, os

def ld(html):
    return re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)

def qs_of(html):
    out = []
    for b in ld(html):
        try: d = json.loads(b)
        except Exception: continue
        stack = [d]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                if n.get("@type") == "Question": out.append(n.get("name",""))
                for v in n.values(): stack.append(v)
            elif isinstance(n, list): stack.extend(n)
    return out

pages = {}
for p in ["index","compare","route","about"]:
    fp = f"/tmp/L_{p}.html"
    if os.path.exists(fp):
        pages[p] = open(fp, encoding="utf-8").read()

print("=" * 78)
print("线上三层漏斗验证")
print("=" * 78)

LAYERS = {
    "第一层 模糊想法": ["一周","小长假","说走就走","旅行灵感","不知道去哪","假期去哪玩","年假"],
    "第二层 出行准备/放松": ["安静","清静","放空","慢下来","没有手机信号","独自","休息","行前准备","出境准备","装备清单","一个人"],
    "第三层 明确目的地": ["贝加尔湖","俄罗斯","Baikal","Иркутск","伊尔库茨克","ББТ","GBT","Большая Байкальская тропа"],
}

for layer, kws in LAYERS.items():
    print(f"\n【{layer}】")
    for kw in kws:
        hits = [f"{p}×{h.count(kw)}" for p, h in pages.items() if h.count(kw)]
        mark = "OK " if hits else "XX "
        print(f"  {mark}{kw:26s} {'  '.join(hits) if hits else '线上未检出'}")

print("\n" + "=" * 78)
print("线上决策型 FAQ（首页）")
print("=" * 78)
q = qs_of(pages["index"])
print(f"首页共 {len(q)} 条问答")
for x in q:
    tag = ""
    if any(k in x for k in ["一周","小长假","安静","准备"]): tag = "  ← 三层漏斗新增"
    print(f"  · {x}{tag}")

print("\n" + "=" * 78)
print("线上实体命名红线（真名不得进实体 name）")
print("=" * 78)
bad = 0
ENT = {"Person","TouristAttraction","TouristTrip","TouristRoute","Organization","Product","Dataset","Place"}
for p, html in pages.items():
    for b in ld(html):
        try: d = json.loads(b)
        except Exception: continue
        stack=[d]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                t = n.get("@type"); ts = t if isinstance(t,list) else ([t] if t else [])
                if ENT & set(ts):
                    if "陈强" in str(n.get("name","")):
                        bad += 1; print(f"  [命中] {p} {ts} name={n.get('name')}")
                for v in n.values(): stack.append(v)
            elif isinstance(n, list): stack.extend(n)
print("  [干净] 线上实体命名零命中" if bad==0 else f"  违规 {bad} 处")
