# Wikivoyage 编辑稿（方案 A + B）

> 用途：补 GBT 徒步信息到 Wikivoyage，修掉现成的 dead link。
> **合规前提**：只写事实、放个人可查的实用信息、**不放商业链接**（baikal50.cn 不能作为来源贴进去）。
> 生成日期：2026-09-18

---

# 方案 A：英文版 Wikivoyage（en.wikivoyage.org/wiki/Lake_Baikal）

## 现状（已实测）

`==Do==` 章节下的 `===Itineraries===` 目前**只有一行**，且链接已失效：

```
===Itineraries===
*Frolikha Adventure Coastline Track, as part of the future [https://en.greatbaikaltrail.org/ Great Baikal Trail]{{Dead link|date=April 2023 |bot=InternetArchiveBot }}.
```

## 建议替换为（直接粘贴）

```
===Itineraries===
* '''Great Baikal Trail (GBT)''' – a planned 1,800 km network of hiking trails around the lake; several sections are complete and waymarked. The best-known section is the western shore route from [[Listvyanka]] to Bolshoye Goloustnoye, roughly {{km|50}}, usually walked in 3 days with camping. The trail passes Bolshiye Koty village and Cape Kadilny, mostly along the lakeshore through taiga forest. Much of the route lies inside Pribaikalsky National Park, which requires a permit (разрешение) – arrange it in advance. There is no mobile signal on most of the route. The shorter Listvyanka–Bolshiye Koty section (about {{km|25}}) can be done as a day hike or overnight, with a hydrofoil boat back to Listvyanka in summer.
* Frolikha Adventure Coastline Track, in the north of the lake, also part of the Great Baikal Trail network.
```

## 顺带修掉的内容

- 原链接 `en.greatbaikaltrail.org` 已失效（标记 2023-04）→ **直接删掉该链接**，改写为不带链接的叙述
- `Frolikha` 那条去掉 shell 里的 dead link 标记，改成纯文字

## ⚠️ 注意

- **不要**在这段里写 "baikal50.cn"、"怪咖叔"、"book with us" 等
- 维基语法：`{{km|50}}` 会自动渲染成 "50 km"；`[[Listvyanka]]` 是内部链接
- 提交前先预览（Show preview），确认没报错

---

# 方案 B：中文版 Wikivoyage（zh.wikivoyage.org/wiki/贝加尔湖）

## 现状（已实测）

全文 6798 字。GBT 只在"观光"章节出现一句，**且链接失效**：

```
弗罗里哈冒险海岸线路道，作为未来大贝加尔湖步道[失效连结]的一部分。
```

"活动"章节写了冰路、小火车、博物馆、狗拉雪橇、熏白鲑，**但完全没写徒步**。"旅行路线"章节也没有 GBT。

## 建议：在「活动」章节补一段徒步内容（直接粘贴）

```
=== 徒步 ===

'''大贝加尔湖步道'''（俄语：Большая Байкальская тропа，英语：Great Baikal Trail，简称 GBT／ББТ）是围绕贝加尔湖规划的一套徒步步道系统，规划总长约1800公里，目前已完成若干区段并设有路标。

其中最经典、也是中文旅行者走得最多的一段，位于湖的西岸：从利斯特维扬卡（Листвянка）出发，沿湖岸经大科特（Большие Коты）、卡迪利内角，到大戈洛（Большое Голоустное），全长约50公里，通常安排3天，途中在湖边扎营。沿途一侧是泰加林（针叶林），一侧是湖面，大部分路段没有手机信号。

线路大部分位于贝加尔国家公园（Прибайкальский национальный парк）范围内，进入保护区需要办理国家公园通行许可（разрешение），建议出发前提前办好。

如果时间有限，可以只走利斯特维扬卡到大科特这一段（约25公里），夏季有气垫船（水翼船）可以坐回利斯特维扬卡。
```

## 顺带修掉

"观光"章节里那句：
```
弗罗里哈冒险海岸线路道，作为未来大贝加尔湖步道[失效连结]的一部分。
```
→ 改成：
```
弗罗里哈冒险海岸线路道，同属大贝加尔湖步道（Great Baikal Trail）系统的一部分。
```

## ⚠️ 注意

- **不要**写 "怪咖叔"、"贝加尔湖50径"（中文语境新造词，维基不认）、"baikal50.cn"
- 中文维基导游用简体、维基语法同上
- 中文维基导游活跃编辑少，编辑通常能留存，但也意味着**审核慢**

---

# 提交步骤（用户本人操作）

1. 打开对应页面 → 点右上「编辑」（Edit）
2. 若弹窗，选 **source editor**（源码编辑器）
3. 找到对应章节，把上面内容粘进去
4. **先点「显示预览」（Show preview）** 确认渲染正常
5. 填编辑摘要（Edit summary），例如：
   - 英文：`Expand Itineraries: add Great Baikal Trail section, fix dead link`
   - 中文：`补充活动章节：大贝加尔湖步道徒步信息；修复失效链接`
6. 点「保存页面」（Save page）
7. **建议先注册账号再编辑**（匿名编辑的 IP 会公开显示；注册账号更稳）

---

# 后续可做（暂不建议）

- **英文 Wikipedia 新建 "Great Baikal Trail" 条目**：目前空白，机会最大，但**缺第三方媒体报道支撑，新条目很可能被提删**。建议先积累媒体报道（如户外杂志、新闻）再做。
- **俄文 Wikipedia**：现有词条挂着"关注度存疑"，补内容可以帮忙，但风险中等。
