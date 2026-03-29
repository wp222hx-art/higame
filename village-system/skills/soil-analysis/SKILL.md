---
name: soil-analysis
description: "土壤分析报告 — 解读土壤检测数据，评估肥力状况，给出改良建议和施肥配方。"
argument-hint: "[地块编号]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# 土壤分析报告

## 工作流
1. 读取地块土壤检测数据（pH值、有机质、氮磷钾、微量元素）
2. 与标准值对比，标记异常指标
3. 分析土壤变化趋势（对比历史数据）
4. 给出改良建议（施什么肥、施多少、什么时候施）
5. 输出施肥配方卡
