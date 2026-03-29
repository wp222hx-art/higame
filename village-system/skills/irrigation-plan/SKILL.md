---
name: irrigation-plan
description: "灌溉方案设计 — 根据作物需水量、水源条件、地块特征制定灌溉计划。"
argument-hint: "[地块] [作物]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# 灌溉方案设计
## 工作流
1. 评估水源条件（水量、水质、取水成本）
2. 计算作物各生育期需水量
3. 对比灌溉方式（漫灌/沟灌/喷灌/滴灌）的适用性和经济性
4. 输出灌溉日历和设施配置方案
