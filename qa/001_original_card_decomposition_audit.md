# 原卡拆解 QA 001

## 结构计数

- worldbook：83 / 83 PASS
- 地点：11 / 11 PASS
- 男性角色：11 / 11 PASS
- 女性角色：25 / 25 PASS
- 核心规则：7 / 7 PASS
- 时间线候选：9 / 9 PASS
- 输出规则：2 / 2 PASS
- 记忆/变量条目：4 / 4 PASS
- 开场：正常开场 + 穿越开场，共 2 组 PASS

## 运行扩展

- regex_scripts = 0 PASS
- Tavern Helper scripts = 0 PASS
- Tavern Helper variables = 0 PASS
- `chara` 与 `ccv3` 嵌入 JSON 一致 PASS

## 时间线开关

原卡当前唯一启用的时间线候选：`74 / 时间线-第一季-上(多选一)`。其余 8 段保持 disabled，未擅自改变开关。

## 拆解覆盖

- 地点原文：已归档。
- 男性人物原文：已归档。
- 女性人物：25/25 均建立运行时索引并完成安全拆解正文；未成年角色性化字段未转录。
- 核心规则：已归档。
- 输出/状态规则：已归档。
- 记忆占位与清空变量规则：已归档。
- 第一季 4 段、第二季 4 段、第三季 1 段：全部归档。

结论：**ORIGINAL_CARD_DECOMPOSITION_BASELINE_PASS**
