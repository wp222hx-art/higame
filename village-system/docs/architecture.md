# 智慧农村管理系统 — 多代理协作架构

> 参照 Claude Code Game Studios 的 48 代理工作室模式，为中国农村设计的
> **AI 辅助村级治理与农业产销一体化管理系统**。
>
> **32 个代理 · 25 个工作流 · 一个协调的 AI 团队**

---

## 为什么需要这个系统

中国农村面临的核心挑战：一家一户的分散种植、信息不对称、销售渠道单一、
年轻人外流导致管理人才短缺。传统的"村干部 + 农技员"模式已经无法应对
现代农业的复杂性 — 从精准种植到品牌电商，每个环节都需要专业知识。

**智慧农村管理系统**通过 AI 代理架构解决这个问题：不是一个通用助手，
而是 32 个专业化代理，组成一个**虚拟村级管理团队**。每个代理有明确的
职责、协作路径和质量标准，覆盖从"种什么"到"卖给谁"的全链条。

---

## 设计哲学

### 从游戏工作室到农村治理的映射

| Game Studios 概念 | 农村系统映射 | 说明 |
|-------------------|-------------|------|
| Creative Director | 村支书/村长 | 全局决策，方向把控 |
| Technical Director | 农业技术总监 | 技术路线决策 |
| Producer | 运营总监 | 进度、资源、协调 |
| Department Leads | 部门负责人 | 种植/销售/财务/后勤 |
| Specialists | 专业人员 | 各领域执行层 |
| Game Pillars | 村庄发展支柱 | 不可妥协的核心原则 |
| Sprint Plan | 农事日历/季度计划 | 阶段性任务管理 |
| GDD | 种植方案/销售方案 | 详细执行文档 |
| QA Testing | 质量检测/安全检查 | 产品和过程质量把控 |
| Release | 上市/出货 | 农产品发布和交付 |

### 核心原则 (村庄发展支柱)

1. **因地制宜** — 所有决策基于本地土壤、气候、水源等实际条件，不盲目跟风
2. **产销一体** — 种植决策必须考虑销售端需求，不种卖不出去的东西
3. **可持续发展** — 土地轮作、生态平衡、长期收益优先于短期利润
4. **集体利益** — 个户决策需考虑对全村的影响，资源共享优于内部竞争
5. **数据驱动** — 用数据指导决策，不凭经验和感觉拍脑袋

---

## 组织架构

```
Tier 1 — 村级领导层 (战略决策)
  village-chief          农业技术总监           运营总监
  (村长/村支书)          (agri-tech-director)   (operations-director)

Tier 2 — 部门负责人 (领域管理)
  种植部长               销售部长               财务部长
  质检部长               后勤部长               品牌部长
  生态环保负责人

Tier 3 — 专业人员 (执行层)
  土壤专家       气象分析师     种子专家       灌溉工程师
  病虫害防治师   农机专家       采收专家       仓储专家
  电商运营师     直播销售师     批发渠道专家   物流专家
  定价分析师     包装设计师     食品安全检测员 有机认证专家
  会计           成本分析师     土地规划师     水利专家
  农旅融合专家   培训师
```

### 部门划分

| 部门 | 负责人代理 | 专业代理 | 核心职责 |
|------|-----------|---------|---------|
| **种植部** | planting-director | soil-expert, meteorologist, seed-expert, irrigation-engineer, pest-control-expert, machinery-expert, harvest-expert | 从选种到收获的全流程 |
| **销售部** | sales-director | ecommerce-operator, livestream-seller, wholesale-expert, logistics-expert, pricing-analyst | 全渠道销售和分销 |
| **品牌部** | brand-director | packaging-designer, agritourism-expert | 品牌建设和增值 |
| **质检部** | quality-director | food-safety-inspector, organic-certifier | 质量和安全 |
| **财务部** | finance-director | accountant, cost-analyst | 资金管理和成本控制 |
| **后勤部** | logistics-director | warehouse-expert, land-planner, water-expert | 基础设施和资源 |
| **生态部** | ecology-director | trainer | 可持续发展和培训 |

---

## 协作协议

**与游戏工作室一致：用户驱动协作，非自主执行。**

每个任务遵循：**提问 → 方案 → 决策 → 草案 → 批准**

1. 代理必须先了解实际情况（土壤数据、气候条件、市场行情）
2. 代理提供 2-4 个方案及优劣分析
3. 村民/管理者做最终决策
4. 代理出具详细执行草案
5. 经批准后方可执行

---

## Skill (工作流) 概览

### 种植管理
`/crop-plan` `/soil-analysis` `/pest-alert` `/irrigation-plan` `/harvest-schedule`
`/rotation-plan` `/seed-select` `/fertilizer-plan`

### 销售管理
`/market-analysis` `/pricing-strategy` `/channel-plan` `/launch-product`
`/brand-build` `/livestream-plan`

### 运营管理
`/seasonal-plan` `/budget-review` `/cost-analysis` `/resource-check`
`/weather-alert` `/training-plan`

### 质量与认证
`/quality-check` `/organic-audit` `/food-safety-review`

### 团队协调
`/team-planting` `/team-sales` `/team-harvest`

---

## 项目结构

```
CLAUDE.md                           # 主配置
village-system/
  agents/                           # 32 个代理定义
  skills/                           # 25 个工作流
  rules/                            # 领域管理标准
  hooks/                            # 自动化验证
  docs/
    architecture.md                 # 本文档
    planting/                       # 种植体系文档
      crop-cycle-guide.md           # 作物周期指南
      rotation-system.md            # 轮作制度
      soil-management.md            # 土壤管理
      pest-management.md            # 病虫害管理
      irrigation-guide.md           # 灌溉指南
    sales/                          # 销售体系文档
      channel-strategy.md           # 渠道策略
      pricing-model.md              # 定价模型
      brand-building.md             # 品牌建设
      supply-chain.md               # 供应链管理
      ecommerce-playbook.md         # 电商运营手册
    governance/                     # 治理文档
      decision-framework.md         # 决策框架
      collaboration-protocol.md     # 协作协议
      resource-allocation.md        # 资源分配
    operations/                     # 运营文档
      seasonal-calendar.md          # 农事日历
      budget-template.md            # 预算模板
      risk-register.md              # 风险登记
  templates/                        # 文档模板
    crop-plan-template.md
    sales-report-template.md
    quality-inspection-template.md
```

---

## 与原系统的对应关系

| 原系统 | 农村系统 | 数量 |
|--------|---------|------|
| 48 Agents | 32 Agents | 精简但覆盖全链条 |
| 37 Skills | 25 Skills | 聚焦农业产销核心流程 |
| 8 Hooks | 6 Hooks | 适配农业场景的自动化 |
| 11 Rules | 8 Rules | 各领域管理标准 |
| 29 Templates | 15 Templates | 农业文档模板 |
