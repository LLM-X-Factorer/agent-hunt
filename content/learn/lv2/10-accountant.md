---
title: 会计 — 这职业到底是干啥的
order: 10
summary: 会计转 AI 的入口非常清晰 — 「报表自动生成 + AI 审计 + RPA 自动化」事务所内部已经在跑。18 条样本中位 8.5k 看似低，但被 AI 数据标注员岗拉低；真实「AI 会计师 / Audit AI」岗位月薪在 15-40k。
reading_minutes: 6
linked_professions:
  - accountant
linked_roles:
  - { market: domestic, role_id: ai_transformation }
---

# 会计 — 这职业到底是干啥的

会计 + AI 的关系，像**「算盘 → 计算器 → AI 工具」的三级跳**。

- 1980 年前：会计师手摇算盘记账
- 1990-2010：金蝶 / 用友 SaaS 出现，会计师从「算」变成「核对 + 报表」
- 2024 年后：AI 介入 — 凭证 OCR / 智能记账 / 自动报表 / AI 审计 — 会计师再次升级，从「核对」变成「设计自动化流程 + 训练 AI 工具 + 做异常审计」

**每一次工具升级，旧岗位都没有消失**，但「不愿意学新工具的人」被工资压低 / 被边缘化。AI 时代的会计师，是「会用 AI + 懂规则」的双背景人。

## 会计做什么（具体）

传统 4 项主业：

1. **记账 + 凭证 + 报表**
2. **税务申报 + 税务筹划**
3. **审计 + 内控 + 合规**
4. **成本核算 + 预算 + 财务分析**

AI 增强版的会计 + 财务，新增 3 个方向：

5. **AI 审计工具实施**（四大 / 内审团队的 Audit AI / Risk AI）
6. **RPA + AI 财务自动化**（应收应付 / 报销 / 凭证 OCR / 银企对账）
7. **财税 SaaS + AI 产品 / 运营**（金蝶 / 用友 / 慧算账 + AI）

## 三套硬核能力

**1. 会计 / 审计底子（保留 + 强化）**。**这是 AI 工程师没法替代你的部分** — AI 工具能跑流程，但 corner case（特殊业务 / 税法解释 / 跨境会计）需要人判断。**CPA / ACCA 持证在 AI 时代不掉价**。

**2. Excel 高级 + SQL（必学）**。AI 会计的入口几乎全在「数据库 + 报表自动化」 — Excel 高级（透视表 / VBA / Power Query）+ SQL 查询是必备。**这一关很多老会计卡了 5 年没过**。

**3. RPA + 基础 Python（学一点）**。UiPath / Power Automate / 简单的 Python 数据脚本。**不需要写 100 行代码，会改改现成模板就够用**。

## 会计 + AI 的真实数据（重要的数据解读）

agent-hunt 抓到 **18 条会计 + AI 岗位样本**：

| 指标 | 数据 |
|---|---|
| 样本量 | 18 条 |
| 中位月薪 | **8.5k**（p25 8k / p75 21k） |
| 中位经验要求 | 1 年 |
| 头部公司 | xAI、Anthropic、Cohere（前 3 全是海外 AI 公司） |

**等一下，为什么会计中位才 8.5k？** 这是一个**重要的数据解读**：

agent-hunt 在「会计 + AI」label 下抓到的样本中，**很大一部分是「Accounting Expert」「Finance LLM Training Specialist」这类「数据标注员 + 领域专家」岗位** — xAI / Anthropic / Cohere 在招大量「财会专家给大模型做数据标注」的低薪岗（折合 8000-15000 月薪）。**这拉低了中位**。

**真实的「AI 会计师 / Audit AI 工程师」岗位月薪是 15-40k**，主要在：

- **四大 / 头部内审**（PwC AI Auditor / Deloitte Risk AI / EY 内审 AI）：18-35k
- **企业财务数字化团队**（央企 / 大型互联网 / 制造大厂）：15-30k
- **财税 SaaS 公司**（金蝶云 / 用友 / 慧算账 / 票易通）AI PM：20-40k

p75 21k 这个数字反映的就是真实「AI 会计师」岗位的上限。

## 怎么开始

**第一步：吃透 Excel + SQL**。这一关不过别想 AI 会计。**Excel 高级（透视表 / VBA / Power Query）+ SQL Select / Join / 子查询，必备**。3 个月可以打通。

**第二步：用 RPA 工具做一个真实自动化案例**。比如用 UiPath / Power Automate 自动跑「凭证 OCR → 审核 → 入账」流程。**简历里加一条「我用 RPA 节省了 N 小时月度结账」就比纯财会简历有差异化**。

**第三步：投这 3 类公司**：

| 优先级 | 公司类型 | 推荐岗位 |
|---|---|---|
| ⭐⭐⭐ | 四大 / 内审 AI 团队 | Audit AI / Risk AI / 审计数字化 |
| ⭐⭐ | 央企 / 大企业财务数字化 | 财务 BP + RPA / 财务系统 PM |
| ⭐ | 财税 SaaS（金蝶云 / 用友 / 慧算账） | AI 产品经理 / 解决方案经理 |

**不推荐**：「Accounting Expert for LLM Training」这类岗位 — 薪资低 + 没有职业 progression。

## 不适合谁

**1. 只做纯凭证 / 纯出纳 / 对软件流程优化抵触的人**。AI 在会计的入口都建立在「能把记账逻辑 → 流程 → 数据库设计」的认知翻译上，**纯记账经验不直接迁移**。

**2. 想完全脱离财会做纯产品 / 纯运营的人**。这跨度比同行业转 AI 大很多。**建议留在「会计 + AI」复合岗，是最高 ROI 的策略**。

**3. 抵触 SQL / 数据库的人**。SQL 是 AI 会计的入门门票 — **不愿学 SQL 就别考虑这条线**。

## 关键提醒：警惕「AI 数据标注员」岗位

xAI / Anthropic / Cohere 在国内招的「Finance Expert」「Accounting Expert」岗位，**绝大多数是「给大模型做财会知识标注」的零工岗**：

- 月薪 8000-15000，按时计费
- 没有职业 progression
- 项目周期 3-6 个月，结束即终止
- 对未来跳槽不形成有效经验

**如果你的目标是「在 AI 时代有真正职业 progression」，避开这类岗位**，target 上文列的「真 AI 会计师 / Audit AI」岗位。

## 下一步

- 想看会计完整 AI 转型 + pivot targets → [会计职业页](/professions/accountant)
- 想看金融分析师（同业务大类但 AI 渗透更深的路径）→ [金融 Lv2 篇](/learn/lv2/finance)
- Lv3 转岗具体路径 → [会计 → AI Finance / Audit AI（待写）](/learn/lv3/accountant-to-ai-finance)
