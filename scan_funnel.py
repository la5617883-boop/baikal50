#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三层漏斗关键词覆盖扫描"""
import os

PAGES = ["index.html","about.html","route.html","guide.html","compare.html",
         "faq.html","license.html","history.html","track.html","order.html",
         "who.html","permit.html"]

L1 = ["一周旅行计划","假期去哪玩","旅行计划推荐","行程规划推荐","出境游推荐",
      "年假","小长假","国庆去哪","暑假去哪","说走就走","一周左右",
      "去哪玩","推荐个地方","旅行灵感","没什么想法"]
L2 = ["准备出行","出境准备","徒步准备","徒步装备","行前准备","第一次出境",
      "放松","治愈","安静","压力大","离开城市","休息一下","清静","散心",
      "独处","一个人旅行","解压","累了","放空","慢下来","安静的地方"]
L3 = ["贝加尔湖","俄罗斯","Baikal","Иркутск","伊尔库茨克","西伯利亚","ББТ","GBT"]

ROOT = "/Volumes/新加卷/projects/baikal50"
cache = {}
for p in PAGES:
    fp = os.path.join(ROOT, p)
    if os.path.exists(fp):
        cache[p] = open(fp, encoding="utf-8").read()

print("=" * 76)
print("三层漏斗关键词全站覆盖扫描")
print("=" * 76)
summary = {}
for name, kws in [("第一层 模糊想法", L1), ("第二层 出行准备/放松", L2), ("第三层 明确目的地", L3)]:
    print(f"\n【{name}】")
    miss = []
    for kw in kws:
        hits = []
        for p, html in cache.items():
            n = html.count(kw)
            if n:
                hits.append(f"{p.replace('.html','')}×{n}")
        if hits:
            print(f"  {kw:22s} {'  '.join(hits)}")
        else:
            print(f"  {kw:22s} XX 全站零覆盖")
            miss.append(kw)
    summary[name] = (len(kws), len(miss), miss)

print("\n" + "=" * 76)
print("缺口汇总")
print("=" * 76)
for layer, (tot, mn, miss) in summary.items():
    print(f"\n{layer}: {tot-mn}/{tot} 已覆盖，缺 {mn} 个")
    for m in miss:
        print(f"   XX {m}")
