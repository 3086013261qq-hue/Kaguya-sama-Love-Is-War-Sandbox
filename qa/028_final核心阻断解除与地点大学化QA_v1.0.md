# 028 final核心阻断解除与地点大学化 QA v1.0

## 目标

本轮只处理两个收尾层：

1. 解除旧 final assembler / core rules 对当前真实替身世界观的反向覆盖；
2. 按“最小大学化”原则完成地点层。

本轮不等于完整最终装配，不提前把30名替身使者、全部替身能力、9条蓝灯、22条绿灯与新大学替身版时间线一次性写入旧83条结构。

---

## 1. final assembler旧阻断

旧 `worldbook/final/assemble_worldbook.py` 曾硬编码覆盖：

- ID56：大学AU / 迁移式学籍规则；
- ID57：旧极端关系/柴刀结局替换逻辑；
- ID61：明确宣称“无超自然力量、异能必须解释为巧合或脑补”的反替身规则。

本轮已修改 assembler：

- [PASS] 删除 ID56 / 57 / 61 的硬编码内容覆盖机制。
- [PASS] assembler只做世界内文本净化，不再自行设计另一套世界观。
- [PASS] 新增 anti-Stand legacy marker 检查；若后续模块重新出现“绝对唯物无超自然”等旧规则，构建应直接失败而不是静默输出。
- [PASS] 输出描述明确为“秀知院大学 × 替身”。

状态：`LEGACY_ASSEMBLER_CORE_OVERRIDE: RESOLVED`

---

## 2. Stand-ready core安全基线

新增：

- `worldbook/final/30_core_rules_stand_ready.json`

并由 `manifest.json` 正式替代旧 `30_core_rules.json` 进入 assembly order。

关键处理：

- [PASS] ID56改为纯世界内“大学学籍与年级”规则，不再使用AU/迁移提示语。
- [PASS] ID57旧柴刀/强制BadEnd规则退出当前核心，保留为空禁用槽位以维持0-82旧ID覆盖。
- [PASS] ID61明确：替身是真实超常精神表现，替身能力、伤害与环境后果真实发生，不得解释成脑补或巧合。
- [PASS] ID61同时保留恋爱头脑战、大学群像与现实社会后果，避免世界被改写成纯战斗场。
- [PASS] 情绪只能增幅既有能力，不凭空创造新能力；欲望不等于爱/信任/承诺/同意。

说明：旧 `30_core_rules.json` 仍作为Git历史中的旧构建输入文件存在，但已不在当前manifest装配链中；当前运行装配只读取 `30_core_rules_stand_ready.json`。

状态：`STAND_READY_CORE_BASELINE: PASS`

---

## 3. 地点母本保护

只读母本：

- `locations/original_locations.md`

本轮未覆盖、未删除。

新增正式源：

- `locations/university_locations.md`

新增final模块：

- `worldbook/final/00_locations_university.json`

`manifest.json` 已改为装配 `00_locations_university.json`，不再读取旧 `00_locations.json`。

状态：`ORIGINAL_LOCATION_MOTHERFILE_PRESERVED: PASS`

---

## 4. 地点最小大学化

原地点总结构不扩张，保持11个实际地点 + 起止占位ID。

非校园地点保持原功能：

- 站前KTV
- 老字号拉面店
- 家庭餐厅
- 藤原家宅邸
- 白银家公寓
- 早坂爱的秘密房间
- 四宫家本邸

只对校园4条做大学化：

### 秀知院大学·桌游研究会活动室
- “桌游部”改为大学“桌游研究会”。
- “普通社团教室”改成学生组织活动大楼内的研究会活动室。

### 秀知院大学·天台
- 保留原天台结构。
- 视野对象改为大学运动场、学部建筑与东京城市景观。
- 不新增独立地图机制。

### 秀知院大学·学生会室
- 保留沙发、茶几、茶具、会长办公桌等原核心视觉。
- 文件用途明确为预算、社团/研究会申请、活动企划与会议记录。
- “贵族学校”措辞改为“名门大学”。

### 秀知院大学
- “综合型贵族学校”改为“顶级私立综合大学”。
- 增加各学部教学楼、研究设施、图书馆、公共学习空间等大学功能。
- “大量学生储物鞋柜”改为大学语境的学生储物柜、公告区与公共学习空间。
- 原古典欧式主楼、钟楼、运动场、中庭、体育馆与旧校舍视觉骨架保留。

状态：`LOCATION_UNIVERSITY_MINIMAL_ADAPTATION: PASS`

---

## 5. 当前manifest状态

当前83条旧结构的安全装配入口已经完成两项替换：

- `00_locations.json` → `00_locations_university.json`
- `30_core_rules.json` → `30_core_rules_stand_ready.json`

因此旧地点高中措辞与旧反超自然核心都不会再通过当前manifest进入运行时。

状态：`LEGACY_LOCATION_AND_CORE_INPUTS_REMOVED_FROM_MANIFEST: PASS`

---

## 6. 仍未完成的最终扩展装配

以下已完成内容目前仍处于各自正式源/QA层，尚未全部写入最终Character Book模块：

- 9条蓝灯核心规则完整拆分；
- 22条绿灯设定；
- 30名替身使者中的替身增强人物条目；
- 14名无替身原作角色按大学世界线原样继承；
- 30份独立替身能力条目；
- 白银父与7名原创角色；
- `timeline/university-stand/` 三季大学替身版时间线。

因此：

`LEGACY_FINAL_ASSEMBLY_BLOCKER: RESOLVED`

但：

`FULL_FINAL_INTEGRATION: PENDING`

当前可以安全进入下一阶段的“完整总装配与ID重排/扩展”，不应直接把旧83条输出误称为最终完整卡。

---

## 结论

`LEGACY_ASSEMBLER_CORE_OVERRIDE: RESOLVED`

`STAND_READY_CORE_BASELINE: PASS`

`LOCATION_UNIVERSITY_MINIMAL_ADAPTATION: PASS`

`ORIGINAL_LOCATION_MOTHERFILE_PRESERVED: PASS`

`LEGACY_LOCATION_AND_CORE_INPUTS_REMOVED_FROM_MANIFEST: PASS`

`FULL_FINAL_INTEGRATION: PENDING`
