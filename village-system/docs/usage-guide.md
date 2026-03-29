# 智慧农村管理系统 — 完整使用指南

> 这份文档手把手教你如何使用这套 AI 多代理协作体系管理一个农村的种植、销售和日常运营。

---

## 一、这套系统是什么？

简单来说：**它是一个「虚拟村级管理团队」**。

传统农村管理靠村干部一人身兼数职——懂种植、懂销售、懂财务、懂品牌……这不现实。

这套系统把管理工作拆分成 **32 个专业角色（代理）**，每个角色负责一个细分领域。你（村长/管理者）只需要：

1. **提出问题** — "今年种什么最赚钱？"
2. **看方案** — 系统给你 2-3 个方案对比
3. **做决策** — 你拍板选哪个
4. **看执行** — 系统自动分配任务到各代理

---

## 二、快速开始（5 分钟上手）

### 第一步：了解你的团队

```
你的直接下属只有 3 个人：
  🏛️ 村长(你自己)
      ├── 🔬 农业技术总监 — 所有技术决策问他
      ├── 📊 运营总监 — 日常运营协调问他
      └── (其他 7 个部门负责人由他们管理)
```

### 第二步：选一个场景开始

| 你想做什么 | 使用的工作流(Skill) | 第一步 |
|-----------|-------------------|----|
| 制定年度种植计划 | `/crop-plan` | 告诉系统你的土地面积、当地气候 |
| 分析该种什么赚钱 | `/market-analysis` | 系统调研市场行情给你建议 |
| 开始做电商卖货 | `/channel-plan` | 系统帮你规划渠道布局 |
| 检查土地状况 | `/soil-analysis` | 启动土壤检测流程 |
| 做个季度计划 | `/seasonal-plan` | 系统按农事日历生成计划 |

### 第三步：运行第一个工作流

以 **「年度种植方案」** 为例：

```
你输入：/crop-plan 蔬菜 春季

系统会：
  1. planting-director（种植部长）接手
  2. 调用 soil-expert 查看土壤数据
  3. 调用 meteorologist 查看气候条件
  4. 调用 pricing-analyst 查看市场行情
  5. 给你 2-3 套方案（稳健型/增长型/创新型）
  6. 你选一个，系统输出详细执行计划
```

---

## 三、核心使用场景详解

### 场景 1：年度种植规划

**时间**：每年 11-12 月

```
步骤：
1. /soil-analysis            → 全村土地检测
2. /market-analysis           → 来年市场行情预测
3. /rotation-plan             → 检查轮作要求
4. /crop-plan [主打品种]       → 生成种植方案
5. /budget-review             → 核算投入预算
6. /seasonal-plan             → 生成全年农事日历

参与代理：
  planting-director → soil-expert → meteorologist
  → seed-expert → pricing-analyst → finance-director

产出文档：
  ✅ 年度种植方案（使用 crop-plan-template.md 模板）
  ✅ 全年农事日历
  ✅ 农资采购清单
  ✅ 年度预算表
```

**实际操作示例**：

```
你：我们村有 200 亩地，100 亩水田，60 亩旱地，40 亩山地。
    去年种了双季稻和蔬菜，效益一般。今年想提高收入。

系统回应：
  📊 soil-expert 报告：100 亩水田土壤良好，60 亩旱地有机质偏低
  🌤️ meteorologist 报告：当地年均温 18°C，雨季 5-8 月
  💹 pricing-analyst 报告：今年草莓行情看涨，辣椒供应过剩

  planting-director 提供 3 套方案：

  方案A（稳健型）：
    水田：早稻+晚稻 80亩，稻虾共作 20亩
    旱地：番茄 30亩，黄瓜 20亩，辣椒 10亩
    山地：柑橘 40亩
    预期总收入：120万  成本：55万  利润：65万

  方案B（增长型）：
    水田：早稻+晚稻 60亩，稻虾共作 20亩，莲藕 20亩
    旱地：大棚草莓 20亩，番茄 20亩，有机蔬菜 20亩
    山地：柑橘 30亩，猕猴桃 10亩
    预期总收入：180万  成本：85万  利润：95万
    ⚠️ 风险：草莓大棚初始投资大（60万）

  方案C（创新型）：
    ...（农旅融合方向）

  🎯 推荐方案B：利润高30万，虽然投资大但2年可回本。

你：选方案B，但草莓先做10亩试试。

系统：收到！调整方案并生成详细执行计划...
```

---

### 场景 2：产品上市销售

**时间**：产品采收前 2-4 周

```
步骤：
1. /harvest-schedule          → 确认采收时间和产量
2. /quality-check             → 采前质量检测
3. /pricing-strategy          → 制定各渠道定价
4. /channel-plan              → 分配销售渠道
5. /launch-product            → 新产品上线
6. /livestream-plan           → 策划直播带货

参与代理：
  harvest-expert → quality-director → food-safety-inspector
  → pricing-analyst → sales-director → ecommerce-operator
  → livestream-seller → logistics-expert

产出文档：
  ✅ 采收排期表
  ✅ 质检报告（使用 quality-inspection-template.md）
  ✅ 各渠道定价表
  ✅ 上市计划
```

**实际操作示例**：

```
你：草莓大棚预计下周开始采收，估计产量 2000 斤/周，持续 4 个月。

系统回应：
  🔍 food-safety-inspector：抽检 5 批次，农残未检出 ✅
  💰 pricing-analyst：
    当前批发价 16 元/斤，电商均价 35 元/斤
    建议定价：
      批发：15 元/斤（走量 40%）
      电商：29.9 元/500g（利润 30%）
      直播：35.9 元/1kg（引流 20%）
      采摘：60 元/人（体验 10%）
  
  📦 sales-director 分配：
    批发：800 斤/周 → wholesale-expert 对接 2 家批发商
    电商：600 斤/周 → ecommerce-operator 上架抖音+拼多多
    直播：400 斤/周 → livestream-seller 每周 3 场直播
    采摘：200 斤/周 → agritourism-expert 周末开放
  
  🚛 logistics-expert：顺丰冷链协议已确认，首重 5 元
```

---

### 场景 3：日常运营管理

**时间**：全年持续

```
常用工作流：
  /weather-alert    → 每日气象预警（自动推送）
  /pest-alert       → 病虫害监测预警
  /resource-check   → 库存/设备/资金盘点
  /cost-analysis    → 月度成本分析
  /budget-review    → 预算执行检查

日常节奏：
  每天早上 → meteorologist 推送天气和农事提醒
  每周一   → operations-director 生成周工作计划
  每月初   → finance-director 出具月度财务报告
  每季度   → village-chief 主持季度总结会
```

---

### 场景 4：应急处理

```
情况：连续暴雨预警

  🔴 meteorologist 触发一级预警
      │
  自动执行：
      ├── weather-alert-trigger.sh 发出系统通知
      ├── planting-director → 评估哪些地块需要抢收
      ├── machinery-expert → 调度收割机抢收成熟作物
      ├── irrigation-engineer → 检查排水系统
      ├── warehouse-expert → 准备仓储空间
      └── logistics-director → 调度防洪物资

  你需要决策：
  - 是否启动全村抢收？（planting-director 提供建议）
  - 预算动用应急储备金？（finance-director 审批）
```

---

## 四、26 个工作流速查表

### 种植管理（8个）

| 命令 | 用途 | 使用时机 |
|------|------|---------|
| `/crop-plan` | 年度种植方案 | 每年 11-12 月 |
| `/soil-analysis` | 土壤检测分析 | 每季度 |
| `/rotation-plan` | 轮作方案 | 制定种植计划前 |
| `/seed-select` | 品种选择 | 播种前 2-3 月 |
| `/fertilizer-plan` | 施肥方案 | 每个生长阶段 |
| `/irrigation-plan` | 灌溉方案 | 干旱期/新设施 |
| `/pest-alert` | 病虫害预警 | 全年监测 |
| `/harvest-schedule` | 采收排期 | 成熟前 2 周 |

### 销售管理（6个）

| 命令 | 用途 | 使用时机 |
|------|------|---------|
| `/market-analysis` | 市场调研 | 年度规划/新品前 |
| `/pricing-strategy` | 定价策略 | 上市前/价格波动时 |
| `/channel-plan` | 渠道规划 | 年度/新品上线 |
| `/launch-product` | 产品上市 | 新品发布 |
| `/brand-build` | 品牌建设 | 持续进行 |
| `/livestream-plan` | 直播策划 | 每周 |

### 运营管理（6个）

| 命令 | 用途 | 使用时机 |
|------|------|---------|
| `/seasonal-plan` | 季度计划 | 每季度初 |
| `/budget-review` | 预算评审 | 每月/每季 |
| `/cost-analysis` | 成本分析 | 每月 |
| `/resource-check` | 资源盘点 | 每月/紧急时 |
| `/weather-alert` | 气象预警 | 自动触发 |
| `/training-plan` | 培训计划 | 每季度 |

### 质量认证（3个）

| 命令 | 用途 | 使用时机 |
|------|------|---------|
| `/quality-check` | 质量检测 | 出货前/例行 |
| `/organic-audit` | 有机认证审核 | 认证期 |
| `/food-safety-review` | 食品安全评审 | 定期/事故后 |

### 团队协调（3个）

| 命令 | 用途 | 使用时机 |
|------|------|---------|
| `/team-planting` | 种植团队协同 | 农忙期 |
| `/team-sales` | 销售团队协同 | 上市期 |
| `/team-harvest` | 采收团队协同 | 采收期 |

---

## 五、自动化验证（Hooks）说明

系统内置 6 个自动化检查，在关键操作时自动运行：

| Hook | 什么时候触发 | 做什么 | 结果 |
|------|------------|--------|------|
| `validate-rotation` | 提交种植计划 | 检查是否违反轮作规则 | 茄科连作→阻断 |
| `validate-quality` | 提交检测报告 | 检查报告是否完整 | 缺字段→阻断 |
| `validate-pricing` | 修改产品定价 | 检查毛利率是否合理 | 低于成本→警告 |
| `weather-alert-trigger` | 天气数据更新 | 检查是否有极端天气 | 暴雨/霜冻→预警 |
| `validate-expense` | 提交支出记录 | 检查审批权限 | >5000 无审批→阻断 |
| `validate-brand-assets` | 上传品牌文件 | 检查命名规范 | 大写/空格→警告 |

---

## 六、文档模板使用方法

### 1. 种植方案模板 (crop-plan-template.md)

```
什么时候用：每次制定新品种种植方案时
怎么用：
  1. 复制模板
  2. 填写基本信息（作物、面积、地块）
  3. 让 planting-director 填写技术细节
  4. 让 pricing-analyst 填写收益预估
  5. 提交 village-chief 审批
```

### 2. 销售报告模板 (sales-report-template.md)

```
什么时候用：每月/每季度末
怎么用：
  1. sales-director 汇总各渠道数据
  2. pricing-analyst 分析价格趋势
  3. ecommerce-operator 提供线上数据
  4. 生成对比分析和下期计划
```

### 3. 质检报告模板 (quality-inspection-template.md)

```
什么时候用：每批产品出货前
怎么用：
  1. food-safety-inspector 采样检测
  2. 填写感官/理化/农残检测结果
  3. quality-director 审核判定
  4. 合格→放行出货；不合格→处理
```

---

## 七、代理协作规则

### 你只需要跟 3 个人说话

```
大方向问题 → 直接说（系统自动路由给 village-chief 代理）
技术问题   → "让技术总监看看"（agri-tech-director）
运营问题   → "让运营看看"（operations-director）
```

### 代理之间自动协作

```
你说："今年想种草莓，可行吗？"

自动流转：
  village-chief → "让种植部评估"
    planting-director → 调用 soil-expert（土壤行不行？）
    planting-director → 调用 meteorologist（温度行不行？）
    planting-director → 调用 seed-expert（什么品种好？）
  
  village-chief → "让销售部看市场"
    sales-director → 调用 pricing-analyst（行情怎么样？）
    sales-director → 调用 ecommerce-operator（线上好卖吗？）
  
  village-chief → "让财务算账"
    finance-director → 调用 cost-analyst（投入多少？）

  最后汇总给你：
    技术可行 ✅（需建大棚，温度适合）
    市场看好 ✅（毛利率 60-70%）
    投入较大 ⚠️（10 亩需投入 12 万）
    建议：先做 5 亩试点，成功后扩大
```

---

## 八、一年运营时间表

```
1月  ：年度总结 + 来年计划定稿 + 年货节
2月  ：春耕备耕 + 育苗 + 农资采购
3月  ：春播 + 果树春管 + 草莓旺季
4月  ：定植 + 插秧 + 春季农旅
5月  ：田管 + 防虫 + 618 预热
6月  ：早稻收割 + 水果上市 + 618 大促
7月  ：盛夏管理 + 抗旱 + 直播发力
8月  ：秋播 + 葡萄采收 + 丰收节准备
9月  ：丰收季 + 草莓定植 + 国庆备货
10月 ：秋收 + 冬播 + 双11 预热
11月 ：总结 + 来年调研 + 双11/双12
12月 ：冬管 + 培训 + 预算 + 年货备货
```

---

## 九、常见问题

**Q: 这套系统需要安装什么软件？**
A: 需要安装 Claude Code CLI，然后 clone 项目仓库，在 Claude Code 中运行即可。

**Q: 我不懂技术，能用吗？**
A: 可以。你只需要用自然语言说你想做什么，系统会自动调用对应的代理和工作流。

**Q: 数据从哪里来？**
A: 土壤数据需要实际检测后录入，市场数据可以让代理联网查询，历史数据需要逐步积累。

**Q: 一个人能管理吗？**
A: 可以。这套系统的设计初衷就是让 1-2 个人借助 AI 代理完成原本需要一个团队的工作。

**Q: 能定制吗？**
A: 完全可以。你可以：
  - 增减代理（修改 agents/ 目录）
  - 修改工作流（修改 skills/ 目录）
  - 调整规则（修改 rules/ 目录）
  - 添加新的验证钩子（修改 hooks/ 目录）
