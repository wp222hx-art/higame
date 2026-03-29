---
name: quality-check
description: "质量检查 — 对即将出货的农产品进行全项质量检查，出具检查报告。"
argument-hint: "[产品批次]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---
# 质量检查
## 工作流
1. 外观检查（大小、颜色、损伤）
2. 农药残留快速检测
3. 分级打包（特级/一级/二级/次品）
4. 出具质检报告
5. 不合格批次处理意见
