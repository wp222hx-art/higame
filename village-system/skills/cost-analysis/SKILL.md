---
name: cost-analysis
description: "成本分析 — 对指定作物或地块进行精细成本核算，找出降本增效空间。"
argument-hint: "[作物/地块]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---
# 成本分析
## 工作流
1. 归集直接成本（种子、肥料、农药、灌溉、人工）
2. 分摊间接成本（农机折旧、设施维护、管理费用）
3. 计算亩均成本和斤均成本
4. 与行业基准对比，找出偏高项
5. 输出降本建议和预期节省金额
