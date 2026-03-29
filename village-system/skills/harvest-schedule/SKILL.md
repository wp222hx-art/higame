---
name: harvest-schedule
description: "采收计划编排 — 根据作物成熟度、天气预报、销售订单，制定详细的采收时间表和人员安排。"
argument-hint: "[作物] [地块]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# 采收计划编排
## 工作流
1. 评估作物成熟度（距采收还有多少天）
2. 对照天气预报选定采收窗口
3. 对接销售部确认订单和交付时间
4. 编排采收人员、农机、包装物资调度表
5. 输出每日采收任务清单
