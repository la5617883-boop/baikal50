#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robots.txt 语法与语义校验：
 ① 指令合法性（已知指令白名单）
 ② 每个 User-agent 组是否有有效规则
 ③ 关键路径的判定结果（用 Google 官方解析规则模拟）
"""
import pathlib
import re

ROBOT = pathlib.Path(__file__).resolve().parent.parent / "robots.txt"
KNOWN = {"user-agent", "allow", "disallow", "sitemap", "crawl-delay",
         "host", "clean-param", "request-rate", "visit-time"}

lines = ROBOT.read_text(encoding="utf-8").splitlines()

groups = []          # [(agents, [(directive, path), ...])]
cur_agents = []
cur_rules = []
errors = []
warns = []
sitemaps = []

for i, raw in enumerate(lines, 1):
    line = raw.split("#")[0].strip()
    if not line:
        continue
    if ":" not in line:
        errors.append(f"L{i}: 缺少冒号 -> {raw!r}")
        continue
    key, _, val = line.partition(":")
    key = key.strip().lower()
    val = val.strip()

    if key not in KNOWN:
        warns.append(f"L{i}: 非标准指令 {key!r}")

    if key == "user-agent":
        if cur_rules or (cur_agents and cur_rules):
            groups.append((cur_agents, cur_rules))
            cur_agents, cur_rules = [], []
        cur_agents.append(val)
    elif key == "sitemap":
        sitemaps.append(val)
    elif key in ("allow", "disallow"):
        if not cur_agents:
            errors.append(f"L{i}: {key} 出现在任何 User-agent 之前（无效指令）")
        cur_rules.append((key, val))
    else:
        if not cur_agents:
            errors.append(f"L{i}: {key} 出现在任何 User-agent 之前")
        cur_rules.append((key, val))

if cur_agents:
    groups.append((cur_agents, cur_rules))

print("=" * 64)
print("① 指令合法性")
print("=" * 64)
print(f"  解析出 {len(groups)} 个 UA 组，{len(sitemaps)} 条 Sitemap")
if errors:
    for e in errors:
        print("  ✗", e)
else:
    print("  ✓ 无结构性错误")
for w in warns:
    print("  ⚠", w)

print()
print("=" * 64)
print("② 分组检查（每组须至少有一条规则，且 UA 非空）")
print("=" * 64)
for agents, rules in groups:
    flag = "✓" if agents and rules else "✗"
    print(f"  {flag} UA={agents}  规则数={len(rules)}")
    if not rules:
        errors.append(f"UA组 {agents} 无任何规则")

print()
print("=" * 64)
print("③ 关键路径判定（模拟 Googlebot 解析）")
print("=" * 64)


def match(pattern: str, path: str) -> bool:
    """robots 通配符匹配：* 任意字符，$ 结尾锚定。"""
    if pattern == "":
        return False
    regex = "^"
    for ch in pattern:
        if ch == "*":
            regex += ".*"
        elif ch == "$":
            regex += "$"
        else:
            regex += re.escape(ch)
    if not pattern.endswith("$"):
        regex += ".*"
    return re.search(regex, path) is not None


def judge(ua: str, path: str):
    """返回 (是否允许, 命中的组说明)"""
    best = None  # (命中长度, allow?)
    chosen_rules = None
    for agents, rules in groups:
        if ua not in agents and "*" not in agents:
            continue
        chosen_rules = (agents, rules)
        break
    # 若精确组没命中，回落到 *
    if chosen_rules is None:
        for agents, rules in groups:
            if "*" in agents:
                chosen_rules = (agents, rules)
                break
    if chosen_rules is None:
        return True, "无匹配组(默认允许)"
    agents, rules = chosen_rules
    for d, p in rules:
        if match(p, path):
            if best is None or len(p) > best[0]:
                best = (len(p), d == "allow", p)
    if best is None:
        return True, f"组{agents}无规则命中"
    return best[1], f"组{agents} 命中 {best[2]!r}"


TESTS = [
    ("Googlebot", "/index.html", True),
    ("Googlebot", "/track.html", True),
    ("Googlebot", "/track-summary.json", False),
    ("GPTBot", "/index.html", True),
    ("GPTBot", "/track.html", True),
    # 方案B：GPX 保持开放（内含版权署名元数据，让 AI 读到 = 替本站署名）
    ("GPTBot", "/baikal50-trail.gpx", True),
    ("GPTBot", "/baikal50-trail-full.gpx", True),
    ("ClaudeBot", "/baikal50-trail.gpx", True),
    ("PerplexityBot", "/baikal50-trail.gpx", True),
    ("Google-Extended", "/baikal50-trail.gpx", True),
    ("YandexBot", "/baikal50-trail.gpx", True),
    ("SomeRandomBot", "/index.html", True),
    ("SomeRandomBot", "/baikal50-trail.gpx", True),
    ("SomeRandomBot", "/track-summary.json", False),
    # 通配也要挡住同类 json 数据包
    ("SomeRandomBot", "/track-anything.json", False),
    ("SomeRandomBot", "/license.html", True),
    ("SomeRandomBot", "/route.html", True),
    ("SomeRandomBot", "/sitemap.xml", True),
]

fails = 0
for ua, path, expect in TESTS:
    got, why = judge(ua, path)
    ok = got == expect
    if not ok:
        fails += 1
        errors.append(f"{ua} {path} 期望{expect} 实际{got}")
    print(f"  {'✓' if ok else '✗'} {ua:16s} {path:26s} "
          f"{'允许' if got else '禁止':4s}  ({why})")

print()
print("=" * 64)
print("④ Sitemap")
print("=" * 64)
for s in sitemaps:
    print(f"  {'✓' if s.startswith('http') else '✗'} {s}")

print()
print("=" * 64)
if errors:
    print(f"结论：失败 {len(errors)} 项 ✗")
    for e in errors:
        print("   -", e)
else:
    print("结论：全部通过 ✓  robots.txt 可安全上线")
print("=" * 64)
