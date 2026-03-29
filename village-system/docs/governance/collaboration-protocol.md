# 协作协议

> 32个代理如何高效协同？本文档规定代理间的沟通规则、信息传递和冲突解决机制。

---

## 一、协作基本原则

### 1.1 三大原则

```
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  用户驱动      │  │  垂直委托      │  │  横向协商      │
│               │  │               │  │               │
│ 所有最终决策   │  │ 上级可委托     │  │ 同级代理可     │
│ 由用户(村民/   │  │ 下级执行任务   │  │ 互相请求协助   │
│ 管理者)做出    │  │ 但不可越级     │  │ 不可越权指挥   │
└───────────────┘  └───────────────┘  └───────────────┘
```

### 1.2 信息传递规则

| 方向 | 规则 | 示例 |
|------|------|------|
| 上→下（委托） | 明确任务、标准、期限 | village-chief 委托 planting-director 制定春季方案 |
| 下→上（汇报） | 带数据、带方案、带建议 | soil-expert 向 planting-director 报告地块检测结果 |
| 平级（协商） | 说明需求、提供信息、约定响应 | sales-director 告诉 planting-director 市场需要大蒜 |
| 跨部门（请求） | 通过上级协调或直接请求 | logistics-expert 请 warehouse-expert 协助出库 |

---

## 二、部门间协作机制

### 2.1 种植-销售协同

```
年度规划时：
  sales-director    → pricing-analyst: 调研市场需求
  pricing-analyst   → sales-director: 市场需求报告
  sales-director    → planting-director: 下年需要什么品种、什么产量
  planting-director → soil-expert + seed-expert: 评估可行性
  planting-director → sales-director: 可种植品种和预计产量
  
  双方对齐 → operations-director 制定综合计划 → village-chief 审批

采收时：
  harvest-expert    → sales-director: 即将采收XX品种XX数量
  sales-director    → 各渠道代理: 分配销售任务
  logistics-expert  → warehouse-expert: 准备仓储/冷链
```

### 2.2 质量-销售协同

```
出货前：
  quality-director → food-safety-inspector: 抽检
  food-safety-inspector → quality-director: 检测报告
  quality-director → sales-director: 放行/拦截通知
  
如质量问题：
  quality-director → planting-director: 追溯到种植环节
  quality-director → logistics-director: 追溯到仓储/物流环节
```

### 2.3 财务-运营协同

```
预算编制：
  operations-director → 各部门负责人: 提交下季预算
  各部门负责人 → finance-director: 预算申请
  finance-director → accountant + cost-analyst: 审核
  finance-director → village-chief: 汇总预算报批

支出控制：
  各代理 → finance-director: 超预算申请
  finance-director → operations-director: 评估必要性
  operations-director/village-chief → 审批
```

---

## 三、冲突解决机制

### 3.1 常见冲突类型

| 冲突类型 | 示例 | 解决路径 |
|---------|------|---------|
| 种销矛盾 | 销售说种A，种植说种不了 | operations-director 协调 |
| 资源争夺 | 两个部门都需要同一台机器 | logistics-director 调度 |
| 预算冲突 | 超预算支出 vs 紧急需要 | finance-director → village-chief |
| 品质vs效率 | 质检标准过严影响发货 | quality-director 与 sales-director 协商标准 |
| 短期vs长期 | 今年多赚 vs 养好地 | village-chief 最终裁决 |

### 3.2 冲突升级路径

```
同级代理无法协商
    │
    ▼
部门负责人协调（24小时内）
    │
    ├── 解决 → 记录备案
    │
    └── 未解决
         │
         ▼
    operations-director 跨部门协调（48小时内）
         │
         ├── 解决 → 记录备案
         │
         └── 未解决
              │
              ▼
         village-chief 最终裁决
              │
              └── 裁决 → 各方执行
```

---

## 四、信息共享规范

### 4.1 共享数据分类

| 数据类型 | 产生者 | 使用者 | 更新频率 |
|---------|--------|--------|---------|
| 土壤检测报告 | soil-expert | planting-director, ecology-director | 每季 |
| 市场价格 | pricing-analyst | sales-director, planting-director | 每日 |
| 库存数据 | warehouse-expert | sales-director, logistics-expert | 实时 |
| 财务报表 | accountant | village-chief, finance-director | 每月 |
| 气象预报 | meteorologist | 全体 | 每日 |
| 病虫害监测 | pest-control-expert | planting-director, ecology-director | 每周 |

### 4.2 紧急通知机制

```
紧急等级：
  🔴 一级紧急（全村通知）：自然灾害、重大病虫害、安全事故
  🟡 二级紧急（相关部门通知）：价格暴跌、设备故障、质量问题
  🟢 三级通知（相关人员通知）：天气变化、农事提醒、出货通知

通知流程：
  发现紧急情况 → 报告直属上级 → 上级评估等级 → 发出对应通知
  
  🔴 一级：meteorologist/pest-control-expert → village-chief → 全村
  🟡 二级：专业代理 → 部门负责人 → 相关部门
  🟢 三级：专业代理 → 相关人员
```

---

## 五、代理协作

| 代理 | 协作框架中的角色 |
|------|----------------|
| `operations-director` | 跨部门协调主要负责人 |
| `village-chief` | 冲突最终裁决者 |
| `各部门负责人` | 部门内协调 |
| `各专业代理` | 信息产生和任务执行 |

## 六、关联技能

- `/team-planting` — 种植团队协同
- `/team-sales` — 销售团队协同
- `/team-harvest` — 采收团队协同
- `/resource-check` — 资源调度盘点
