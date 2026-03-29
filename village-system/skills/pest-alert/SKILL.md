---
name: pest-alert
description: "病虫害预警与防治 — 根据当前季节、气候条件和历史数据，发布病虫害预警并给出防治方案。"
argument-hint: "[作物] [症状描述]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, WebSearch
---

# 病虫害预警与防治

## 工作流
1. 识别病虫害类型（根据描述或图片）
2. 评估危害程度和扩散风险
3. 制定防治方案（优先生物防治和物理防治）
4. 化学防治作为最后手段（附安全间隔期）
5. 输出防治操作指导卡
