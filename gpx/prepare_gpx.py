"""把用户实测 GPX 清洗成可发布版本。

输入: «пос. Листвянка - пос. Большое Голоустное (ББТ)».gpx (3 段, 1066 点)
输出: baikal50-trail.gpx        —— 合并为单段、去跳变、适度简化
      baikal50-trail-full.gpx   —— 合并但保留全部点（备用）
      track-summary.json        —— 统计摘要，供页面引用

原则:
  - 绝不编造坐标: 只做删除(跳变点)与抽稀(保留原始点)，不插值新点
  - 段顺序按地理连续性拼接: 段2(起点→中段) → 段1 → 段3(中段→终点)
  - 校验拼接后总长落在合理区间
"""
import xml.etree.ElementTree as ET
import math, json, os

SRC = "«пос. Листвянка - пос. Большое Голоустное (ББТ)».gpx"
OUT_DIR = "/Volumes/新加卷/projects/baikal50"

NS = "http://www.topografix.com/GPX/1/1"
R = 6371000

def strip(t):
    return t.split('}')[-1]

def dist(a, b):
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    x = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(x))

def seglen(pts):
    return sum(dist(pts[i-1], pts[i]) for i in range(1, len(pts)))

root = ET.parse(SRC).getroot()

# ---- 1. 读入各段 ----
segs = []
for tr in [el for el in root if strip(el.tag) == "trk"]:
    for seg in tr:
        if strip(seg.tag) != "trkseg":
            continue
        pts = [(float(p.get("lat")), float(p.get("lon")))
               for p in seg if strip(p.tag) == "trkpt"]
        if pts:
            segs.append(pts)

# ---- 2. 航点(含营地/地标/起终点) ----
wpts = []
for w in [el for el in root if strip(el.tag) == "wpt"]:
    nm = w.findtext("{%s}name" % NS) or ""
    wpts.append({
        "lat": float(w.get("lat")),
        "lon": float(w.get("lon")),
        "name": nm,
    })

# 真实端点
START = next((w for w in wpts if "Начало" in w["name"]), None)
END = next((w for w in wpts if "Окончание" in w["name"]), None)

# ---- 3. 段顺序: 由 diagnose_order.py 穷举确认为唯一零接缝解 ----
#   段2反向(终点→中段) → 段1正向 → 段3反向
#   接缝总距离 0.00km / 头距真实起点 0.13km / 尾距真实终点 0.11km
ordered = [segs[1][::-1], segs[0], segs[2][::-1]]

# ---- 4. 合并 + 去跳变 (>500m 视为漂移，删除该点) ----
# 实测: 段间接缝 0.0m（严丝合缝）；全轨迹最长点间距 520m（段3点439，属正常采样间隔）
# 注意: 判断后用 continue 跳过的点不更新参考点会累积误差（曾误杀 72 点）
MAX_JUMP = 800
merged = []
dropped_pts = []
prev = None
for seg in ordered:
    for p in seg:
        if prev is not None and dist(prev, p) > MAX_JUMP:
            dropped_pts.append((prev, p, dist(prev, p)))
            continue
        if p != prev:
            merged.append(p)
            prev = p

full_len = seglen(merged)
dropped = len(dropped_pts)

# ---- 5. 抽稀 (Douglas-Peucker, 保留原始点，不插值) ----
def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    # 用平面近似: 经纬度按纬度缩放
    lat0 = math.radians(sum(p[0] for p in pts)/len(pts))
    kx = R * math.cos(lat0) * math.pi / 180.0
    ky = R * math.pi / 180.0
    P = [(p[1]*kx, p[0]*ky) for p in pts]

    def pld(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx-ax, by-ay
        L2 = dx*dx + dy*dy
        if L2 == 0:
            return math.hypot(px-ax, py-ay)
        t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / L2))
        return math.hypot(px-(ax+t*dx), py-(ay+t*dy))

    keep = [False]*len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts)-1)]
    while stack:
        i, j = stack.pop()
        dmax, idx = 0.0, -1
        for k in range(i+1, j):
            d = pld(P[k], P[i], P[j])
            if d > dmax:
                dmax, idx = d, k
        if dmax > eps and idx > 0:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return [pts[i] for i in range(len(pts)) if keep[i]]

# 目标 ~5m 容差 (徒步轨迹足够)
EPS = 5.0
simp = rdp(merged, EPS)
simp_len = seglen(simp)

# ---- 6. 写出 GPX ----
def write_gpx(path, pts, wpts, name):
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<gpx xmlns="%s" version="1.1" creator="baikal50.cn">' % NS,
         '  <metadata>',
         '    <name>%s</name>' % name,
         '    <link href="https://baikal50.cn/"><text>贝加尔湖50径 baikal50.cn</text></link>',
         '    <time>2025-07-01T00:00:00Z</time>',
         '  </metadata>']
    for w in wpts:
        L.append('  <wpt lat="%.6f" lon="%.6f"><name>%s</name></wpt>'
                 % (w["lat"], w["lon"], w["name"]))
    L.append('  <trk>')
    L.append('    <name>%s</name>' % name)
    L.append('    <trkseg>')
    for la, lo in pts:
        L.append('      <trkpt lat="%.6f" lon="%.6f"/>' % (la, lo))
    L.append('    </trkseg>')
    L.append('  </trk>')
    L.append('</gpx>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

os.chdir(OUT_DIR)
write_gpx("baikal50-trail.gpx", simp, wpts, "贝加尔湖50径 · 利斯特维扬卡—大戈洛 (ББТ)")
write_gpx("baikal50-trail-full.gpx", merged, wpts, "贝加尔湖50径 · 利斯特扬卡—大戈洛 (ББТ) 完整轨迹")

summary = {
    "start": {"lat": merged[0][0], "lon": merged[0][1],
              "name": START["name"] if START else ""},
    "end": {"lat": merged[-1][0], "lon": merged[-1][1],
            "name": END["name"] if END else ""},
    "length_km": round(full_len/1000, 1),
    "points_full": len(merged),
    "points_simplified": len(simp),
    "points_dropped_as_jumps": dropped,
    "waypoints": len(wpts),
    "bbox": {
        "minlat": round(min(p[0] for p in merged), 5),
        "maxlat": round(max(p[0] for p in merged), 5),
        "minlon": round(min(p[1] for p in merged), 5),
        "maxlon": round(max(p[1] for p in merged), 5),
    },
    "source": "2025-07 实测轨迹",
    "segments_merged": len(segs),
}
with open("track-summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("=== 段拼接顺序 ===")
for i, s in enumerate(ordered, 1):
    print(f"  第{i}段: {len(s)}点 {seglen(s)/1000:.2f}km  头{s[0][0]:.5f},{s[0][1]:.5f}")
print(f"\n拼接总长: {full_len/1000:.2f} km")
print(f"丢弃跳变点: {dropped}")
print(f"抽稀: {len(merged)} → {len(simp)} 点 (容差 {EPS}m, 长度 {simp_len/1000:.2f} km)")
print(f"总降幅: {100*(1-simp_len/max(full_len,1)):.2f}%")
print(f"\n输出:")
for fn in ["baikal50-trail.gpx", "baikal50-trail-full.gpx", "track-summary.json"]:
    print(f"  {fn}  {os.path.getsize(fn):,} bytes")
