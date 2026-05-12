---
title: 数据分析 / 数据科学家 — 这职业到底是干啥的
order: 13
summary: 数据岗在 AI 时代不是被取代，是被「升级」 — SQL + Python 基础 + LLM 评测能力。国内 164 岗 median 35k 但跨度大（15-65k），海外 384 岗 median 62k CNY/月。坐标看哪一档，先看你能输出的洞察类型。
reading_minutes: 6
linked_roles:
  - { market: domestic, role_id: data }
  - { market: international, role_id: data }
---

# 数据分析 / 数据科学家 — 这职业到底是干啥的

把数据岗想成**翻译家**。

公司有两套语言：

- **业务语言**：「这个月销售下滑了 12%」「华东区客单价比华北低」「老用户复购率不行」
- **数据库语言**：1.2 亿行交易表 + 800 个产品 SKU + 7 个国家 timezone + 4 个支付渠道

数据分析师的工作就是**在两种语言之间翻译** — 把业务问题翻成 SQL / Python 查询，把 1.2 亿行数据翻成「华东区客单价低是因为 XX 品类拖后腿」这种业务可执行的洞察。

**AI 时代这件事没变**，只是工具升级了 — 现在多了「LLM 帮你写 SQL」「LLM 帮你做评测分析」这一层。

## 数据岗的两个极端

数据岗在 AI 时代**最大的特点是分化严重** — 同样标题「数据分析师」/「Data Scientist」，能力要求可以差 5 倍：

| 类型 | 工作内容 | 月薪范围 |
|---|---|---|
| **偏 BI 报表** | 仪表盘 / Power BI / Tableau / 周报月报 | 10-20k（国内） |
| **偏业务分析** | 用 SQL 写复杂查询、做 A/B 实验设计、用 Python 跑回归 | 20-40k |
| **偏数据科学 / ML** | 建模 + 特征工程 + 上线模型 + 跑评测 | 35-70k |
| **偏 LLM 数据 / 评测** | 训练数据集设计 + LLM-as-judge + 模型评测 | 30-60k |

这是为什么 agent-hunt 国内数据角色 median 35k 但 p25 到 p75 跨度从 15k 到 65k — **不是行业波动，是「数据分析师」这个标题下面塞了 4 种完全不同的活**。

## 三套硬核能力

**1. SQL 真功底**。不是「会写 select」就行。要会：

- 窗口函数（row_number / rank / lag / lead）
- 子查询 + CTE（WITH 子句）
- 复杂 join（包括 anti-join / semi-join）
- 优化执行计划（看 EXPLAIN）

**这一关在国内数据岗很多人卡了 3-5 年没过** — 只会写简单 select 的人面试容易被刷。

**2. Python 数据栈 + 统计直觉**。pandas + numpy + scipy + matplotlib — 必备。再加：

- **A/B 实验设计**：怎么算样本量 / 怎么避免 p-hacking
- **基础 ML**：用 scikit-learn 跑回归 + 分类，至少懂为什么用 train/test split
- **因果推断基础**：DiD / 工具变量 / PSM 知道一点（高端业务分析岗会考）

**3. 业务理解 + 沟通**。**这是数据岗在 AI 时代最难替代的部分** — AI 可以自动写 SQL，但 AI 不知道「为什么业务方要这个数据」、不知道「这个洞察用什么方式告诉 CEO」。**会讲故事的数据分析师，永远稀缺**。

## 数据岗的真实数据

agent-hunt 国内 / 海外都有这条线：

| 指标 | 国内 | 海外 |
|---|---|---|
| 岗位数 | 164 | 384 |
| 中位月薪 | 35k（p25 15k / p75 65k，样本 25） | **62k CNY/月**（p25 49k / p75 94k，样本 14） |
| 中位经验 | 2 年 | 3 年 |
| 头部公司 | 字节跳动、腾讯、MiniMax、Moonshot | RBC、TikTok、John Deere、OpenAI、TD Bank |
| 主要行业 | internet / finance / healthcare | internet / consulting / finance |
| 关键技能 | data_analysis (4) / llm (3) / sql (1) | sql (15) / python (14) / data_analysis (3) |

**国内有意思的点**：大模型公司（字节豆包 / Moonshot / MiniMax / 智谱）**也在大量招数据岗**。比如「豆包 AI 大模型数据分析-火山方舟 MaaS」「Data Analyst - LLM agentic AI」 — 这是新出现的 niche：**用大模型评测 + 训练数据策展**。

**海外的差异**：62k 中位高于国内一倍，但**对 SQL / Python 要求也明显高**（top required skill SQL 15 / Python 14，远超国内）。如果你国内数据岗只会做仪表盘，**海外面试一句「sliding window 怎么实现」就刷掉**。

## 怎么开始

**第一步：吃透 SQL**。这一关不过别想做数据岗。**LeetCode Database 题库刷 100+ 题 + SQLBolt 互动教程过一遍**。3-6 个月扎实学习。

**第二步：用 Python + 业务数据集做 2-3 个分析项目**：

- Kaggle 上找一个商业数据集（电商 / 用户行为 / 金融）
- 提出 3-5 个业务问题 → 用 SQL/Pandas 查询 → 用 matplotlib 画图 → 写 1 页洞察总结
- **重点不是技术炫技，是「能讲清楚业务问题 + 用数据回答」**

**第三步：加 LLM 评测能力**。这是 AI 时代数据岗的差异化：

- 用 LangSmith / Phoenix 跑 LLM-as-judge
- 学怎么设计 LLM 评测集（100-1000 条 case）
- 跑 RAG 评测 / Agent 评测（用 RAGAS / LangChain Eval）

**第四步：target 公司**：

| 优先级 | 公司类型 |
|---|---|
| ⭐⭐⭐ | 国内大模型公司数据团队（字节豆包数据 / 腾讯混元数据 / Moonshot 数据策展） |
| ⭐⭐⭐ | 海外 AI 公司中国团队（OpenAI / Anthropic / TikTok 数据岗） |
| ⭐⭐ | 互联网大厂业务数据团队（字节 / 美团 / 阿里 / 拼多多） |
| ⭐ | 金融数据团队（蚂蚁 / 招行 / 平安 / 中信 / RBC / TD Bank） |

## 不适合谁

**1. 只会做仪表盘 BI、没建过模型 / 没有业务洞察输出能力的人**。AI 公司招数据岗看「数据驱动决策」证据 — **能讲故事 + 能写 SQL + 能跑实验三件套缺一不可**。

**2. 不想写 SQL 的人**。SQL 是数据岗的入门门票 — **不愿学 SQL 别考虑这条线**。

**3. 只对纯算法感兴趣的人**。数据科学 ≠ 算法工程师。如果你想做模型训练，去看 [算法工程师](/learn/lv2/algorithm)；如果你想做 LLM 应用，去看 [AI Agent 工程师](/learn/lv2/ai-engineer)。

## 数据岗 vs 算法岗 vs AI Agent 工程师（三角对比）

| 维度 | 数据岗 | 算法岗 | AI Agent 工程师 |
|---|---|---|---|
| 核心动作 | 查数据 + 跑实验 + 出洞察 | 训模型 + 调参 | 拼应用 + 调 prompt |
| 输入 | 业务问题 | 训练目标 | 用户需求 |
| 输出 | 洞察报告 + 决策建议 | 模型权重 + 评测 | 上线产品 |
| 必备 | SQL + Python + 统计 + 业务理解 | PyTorch + 数学 + paper | LangChain + RAG + 评测 |
| 学历 | 本科够（业务理解最值钱） | 硕博明显占优 | 本科够（项目最值钱） |
| 国内中位 | 35k | 52.5k | 32.5k |

## 下一步

- 想看数据岗完整数据 → [国内数据角色页](/roles/domestic/data) / [海外数据角色页](/roles/international/data)
- 想看「用模型」那条线 → [AI Agent 工程师 Lv2 篇](/learn/lv2/ai-engineer)
- 想看「造模型」那条线 → [算法工程师 Lv2 篇](/learn/lv2/algorithm)
- 海外研究路径 → [ML Scientist Lv2 篇](/learn/lv2/ml-scientist)
