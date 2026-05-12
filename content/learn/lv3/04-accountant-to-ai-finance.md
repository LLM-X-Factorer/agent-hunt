---
title: 会计 → AI Finance / Audit AI (具体怎么转)
order: 4
summary: 12 周路径：1-4 周补 SQL + Python + RPA，5-8 周做 1 个真实自动化案例（最值钱：自己公司的财务流程），9-12 周投四大 / 央企财务数字化 / 财税 SaaS。**避开 Anthropic / xAI 的 LLM 训练标注岗**。
reading_minutes: 9
linked_professions:
  - accountant
linked_roles:
  - { market: domestic, role_id: ai_transformation }
---

# 会计 → AI Finance / Audit AI 具体怎么转

这一篇不讲「为什么转」（看 [会计职业页](/professions/accountant) + [会计 Lv2 篇](/learn/lv2/accountant)），只讲**怎么一步一步转**。

**重要提醒**：避开 xAI / Anthropic / Cohere 在国内招的「Accounting Expert / Finance LLM Training Specialist」岗 — 这些是 LLM 数据标注外包工，月薪 8-15k，没有职业 progression。**真正有 progression 的 AI Finance 岗在四大 / 央企数字化 / 财税 SaaS**。

## 总览：12 周路径

```
第 1-4 周：补 SQL + Python + RPA 三件套
第 5-8 周：做 1 个真实财务流程自动化案例（用自己公司数据最值钱）
第 9-12 周：投四大 Audit AI / 央企财务数字化 / 财税 SaaS AI PM
```

不需要辞职，工作日晚上 + 周末 6-8h / 周，总投入约 80h。

## 第 1-4 周：补技术底子

会计师面试 AI Finance 岗最大的优势是「真懂业务 + 持证」，最大的劣势是「Excel 高级 + SQL 不熟 + 没编程经验」。这 4 周补这个差距。

**Week 1：Excel 高级 + Power Query**

如果你的 Excel 还停在 vlookup + 透视表 level，先补完这些：

- **Power Query**：从多个 csv / 数据库源拉数据 + 清洗 + 合并 — 必备
- **Power Pivot / DAX**：复杂报表用，比 vlookup 强 10 倍
- **VBA 基础**：自动跑月结流程的入门工具

**目标**：能用 Power Query 自动从 10 个 Excel 文件 + 1 个数据库聚合数据 → 跑出月度报表 → 节省 N 小时手工。

**Week 2：SQL 入门**

SQL 是 AI Finance 的入门门票。学这些：

- Select / Where / Group By / Having / Join（inner / left / right）
- 子查询 + 窗口函数（row_number / rank / lag / lead）
- 聚合函数（sum / avg / count / case when）

推荐资源：**LeetCode Database 题库**（前 50 题刷完）+ **SQLBolt 互动教程**（免费）。

**目标**：能写出「从 ERP 数据库取最近 12 个月、按部门 + 客户聚合应收账款 + 计算账龄分布」这种查询。

**Week 3：Python 入门 + RPA 工具**

Python：pandas + openpyxl（读写 Excel）+ requests（拉数据）。**1 周就能上手做财务自动化脚本**。

RPA 工具任选 1 个：
- **UiPath**（功能强但学习曲线陡）
- **Power Automate**（微软系，和 Excel / Outlook 配合好，会计师最友好）
- **影刀 RPA**（国内 SaaS，中文教程多）

**目标**：能用 RPA 把「打开网银 → 下载流水 → 导入 Excel → 比对账单」这种重复劳动跑成全自动。

**Week 4：写「我的业务方法论文档」**

写下面 6 个 section（每个 500-1000 字）：

1. 我做过的最复杂的会计 / 审计 / 财务分析场景
2. 我处理过的最难的财务 case（前后过程 + 关键决策 + 合规判断）
3. 我对「财务流程 vs 自动化」的认知（哪些流程一定要人判断 / 哪些应该全自动）
4. 我用过的所有 ERP / 财务系统（金蝶 / 用友 / SAP / Oracle / 用 hi）
5. 如果让 AI 介入审计 / 月结 / 财务分析，AI 应该做什么、做不了什么
6. 财会 + AI 结合最有价值的 3 个场景是什么

**这份文档是面试核心素材**。

## 第 5-8 周：做一个真实自动化案例

**Week 5：选场景（强烈推荐用自己公司的真实流程）**

3 个推荐场景（**第一个最值钱**）：

| 场景 | 数据来源 | 难度 | 简历价值 |
|---|---|---|---|
| **公司月结流程自动化**（凭证 OCR / 报销审核 / 对账） | 你自己工作的真实数据 | 中 | ⭐⭐⭐⭐⭐ |
| **应收账款账龄 + 风险预警建模** | 你自己公司应收数据（脱敏） | 中 | ⭐⭐⭐⭐ |
| **公开财报数据 + 财务比率分析** | Wind / 同花顺 / Tushare | 低 | ⭐⭐⭐ |

**第一个最值钱**：能说「我在 XX 公司用 RPA 节省了 N 小时月结时间」是面试官最爱听的具体数据。

**Week 6-7：跑实施 + 出结果**

- 用 RPA + Python 把整个流程跑通
- 记录数据：**节省了多少小时 / 错误率从 X% 降到 Y%**（这是 ROI 数字）
- 写一份「实施方案 + ROI 计算 + 风险评估」报告

**Week 8：写成案例 + 简历素材**

包含：
- 解决的问题（业务背景 + 当前痛点）
- 系统设计（RPA + AI 哪一段，规则 + 模型哪一段）
- **实施效果**（节省时间 / 减少错误 / 业务方反馈）
- 反思：哪些没自动化（人判断的边界）

**这是面试核心 deliverable**。

## 第 9-12 周：投简历 + 面试

**Week 9：改简历**

把原来的「N 年会计 / 审计」升级成「N 年财会业务 + 财务数字化 + 1 个真实自动化案例」。
- 财会经历保留，但用「流程优化 / 数据驱动 / 合规判断」这种系统化语言重写
- 自动化 case 单独一段，附 ROI 数字 + 截图
- CPA / ACCA 持证作为简历亮点

**Week 10-11：投这 3 类公司**

| 优先级 | 公司类型 | 推荐岗位 |
|---|---|---|
| ⭐⭐⭐ | 四大 / 头部内审 AI 团队 | PwC AI Auditor、Deloitte Risk AI、EY 内审 AI、KPMG Digital Audit |
| ⭐⭐⭐ | 央企 / 大企业财务数字化 | 国资委直属 / 大型互联网 / 制造大厂 → 财务 BP + RPA / 财务系统 PM / 财务数字化经理 |
| ⭐⭐ | 财税 SaaS | 金蝶云 / 用友 / 慧算账 / 票易通 / 百望云 / 易票通 → AI 产品经理、解决方案经理 |

**Week 12：面试 + 谈 offer**

面试常见问题：
- 「为什么从纯财会转 AI」→ 用方法论文档第 5、6 节回答（讲业务 + 自动化 + AI 三者的边界）
- 「你的技术能力」→ 用 SQL + Python + RPA + 自动化 case 回答（重点：能讲清楚 ROI 数字）
- 「你怎么看 AI 替代会计」→ 用方法论文档第 3 节回答（流程 vs 业务判断）
- 「你能 hold 住建模吗」→ 诚实说「我能做应收账龄建模这种业务驱动的 ML，复杂的算法工程不是我的强项」

谈薪：会计 → AI Finance / Audit AI 起薪范围 **15-35k**，CPA 持证 + 大企业背景的能到 25-40k，比传统会计师高 30-80%。

## 不要犯的 3 个错

**1. 不要去考一堆 AI 证书**。微软 AI 认证 / 阿里云 ML 工程师认证对 AI Finance 岗几乎没用 — **面试官看 CPA + 真实自动化 case**，不看 AI 证书。

**2. 不要投 xAI / Anthropic / Cohere 的「Accounting Expert」岗**。这些是 LLM 数据标注外包工，**和真正的 AI Finance 职业路径完全是两条平行线**，做了对未来跳槽不加分。

**3. 不要尝试转纯算法 / 纯软件岗**。会计 → 纯算法的跨度太大（要 2-3 年），ROI 低。**留在「财会 + AI / 数字化」复合岗反而是稀缺组合**。

## 12 周后你应该长什么样

- 一份业务方法论文档（4000-6000 字）
- 一份真实自动化 case 报告（含 ROI 数字 + 截图）
- SQL + Python + RPA 三件套基础能力
- 改造后的简历 + 求职信
- 投了 10-20 家公司 + 拿到 3-5 个面试 + 1-3 个 offer

**核心是 80h 时间 + 你已有的财会经验 + CPA / ACCA 持证（如有）**。

## 长期成长方向

- **横向**：从月结自动化 → 全公司财务数字化 → 财务共享中心 lead
- **纵向**：财务数字化经理 → 财务 IT 总监 → CFO 数字化方向
- **顶档薪资**：四大 Senior Manager 级 Audit AI + 大型央企财务数字化总监 → 40-80k 月薪可达

## 下一步

- 想看会计 AI 转型完整数据 + pivot targets → [会计职业页](/professions/accountant)
- 想看「AI 转型 / 咨询」角色画像 → [AI 转型角色页](/roles/domestic/ai_transformation)
- 想看类似业务转岗参考 → [金融 → 量化研究员 Lv3 篇](/learn/lv3/finance-to-quant)
