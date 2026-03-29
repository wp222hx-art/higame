---
name: fertilizer-plan
description: "施肥方案制定 — 根据土壤检测、作物需肥规律、目标产量，制定精准施肥方案。"
argument-hint: "[作物] [地块]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# 施肥方案制定
## 工作流
1. 读取目标地块土壤检测报告
2. 确定目标作物和产量目标
3. 计算各生育期需肥量（N-P-K + 微量元素）
4. 扣除土壤供给量，得出施肥量
5. 制定基肥 + 追肥时间表
6. 推荐肥料品牌和采购量
