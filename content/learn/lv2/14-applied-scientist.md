---
title: Applied Scientist — 这职业到底是干啥的（海外）
order: 14
summary: Applied Scientist 是「研究 ↔ 业务」之间的桥梁 — 不发顶会 paper 也不写产品代码，把 ML 方法用到具体业务（广告 / 支付 / 推荐 / 风控）。海外 ml_scientist 簇里的「业务向研究」子类，median 88k / p75 154k CNY/月，比纯 Research Scientist 稍开放一点。
reading_minutes: 7
linked_roles:
  - { market: international, role_id: ml_scientist }
  - { market: international, role_id: ml_engineer }
---

# Applied Scientist — 这职业到底是干啥的

把研究和工程想成两座山：

- **左边山顶**：Research Scientist — 发顶会论文 / 推 SOTA / 算法理论突破
- **右边山顶**：ML Engineer — 上线服务 / 跑 pipeline / 工程优化

两座山之间有一座桥。**Applied Scientist 就是这座桥** — **把研究端的方法（新模型 / 新算法 / 新评测）翻译成业务可落地的解决方案**。

不是发 paper，也不是写部署 yaml。**Applied Scientist 做的是「这套 ML 方法怎么在我们公司的广告 / 支付 / 推荐 / 风控业务里产生 1000 万美元收益」**。

## Applied Scientist 和 Research Scientist 的区别

这两个 title **经常混用** — agent-hunt 数据里两者都在 `ml_scientist` 簇下（海外 790 条岗位）。但实际工作内容差异明显：

| 维度 | Research Scientist | Applied Scientist |
|---|---|---|
| **核心交付** | 论文 / 新方法 / 模型权重 | 业务指标提升 / 系统性收益 |
| **客户** | 学术界 / 公司内部 research team | 公司业务部门（广告 / 支付 / 推荐 / 风控） |
| **节奏** | 6-18 月研究周期 | 季度 / 半年级业务迭代 |
| **PhD 占比** | ~90% | ~70%（硕士可入门） |
| **paper 重要性** | 顶会 1-3 篇起步 | 有 paper 是加分但不必要 |
| **典型 title** | Research Scientist, NLP / Generative AI Research | Senior ML Scientist, Payments / Ads / Search |
| **典型公司** | OpenAI Research / Google Brain / DeepMind / Anthropic Research | Amazon Ads / Microsoft / TikTok / Meta Ads / Stripe |

**这两座山之间的边界经常模糊** — OpenAI 的 Applied Researcher 可能既发 paper 也优化 ChatGPT 业务指标。但**面试时一定要问清楚岗位偏哪边** — 偏 Research 的岗位会有 paper bar，偏 Applied 的岗位会有业务 metric bar。

## Applied Scientist 做什么（具体）

一个具体例子：电商公司想用 LLM 改进商品推荐。

Applied Scientist 做法：

1. **问题定义**：和业务方对齐 — 是改进点击率？转化率？长期 LTV？避免推荐过去看过的？
2. **现状分析**：跑 A/B 实验 baseline — 当前推荐算法的 CTR / CVR / 多样性 / 时延
3. **方法选型**：扫一遍最近的论文 + 工业界 blog，挑 2-3 个候选方法（比如「semantic embedding 召回」+「LLM rerank」）
4. **小规模验证**：在历史日志上做离线实验，看 NDCG / Recall 是否能涨
5. **上线 + A/B**：和 ML Engineer 配合上小流量 A/B（1-5%），观察业务指标
6. **报告 + 推广**：写 paper-quality 内部报告 + 在公司技术大会讲 + 推广到其他业务线

**这是一份「让公司每年多赚几千万美元」的工作**，输出不是 GitHub 模型权重，是**生产 A/B 实验结果 + 内部技术文档**。

## 三套硬核能力

**1. 业务领域知识 + 数据敏感度**。Applied Scientist 必须懂业务 — 广告系统的 eCPM / pCTR / pCVR 怎么算、推荐系统的多样性怎么衡量、风控的精召权衡。**没有业务直觉，光会算法是不够的**。

**2. ML 全栈（数据 → 模型 → 评测）**。和 Research Scientist 不同，Applied Scientist 不能「只关心新方法」 — 数据 pipeline / 特征工程 / 离线评测 / 在线 A/B 全要 hold 住。**PhD 但只懂理论不懂数据 pipeline 的人在这条线上反而不如硕士**。

**3. 论文阅读 + 内部技术写作**。能读懂顶会 paper、能复现、能改造成业务可用方案；同时能用业务方听得懂的语言写报告（不能只用数学公式）。**这是研究端 + 业务端双语翻译的核心能力**。

## Applied Scientist 的真实数据（海外 ml_scientist 簇）

agent-hunt 海外 `ml_scientist` 簇 **790 条岗位**，是海外第二大非 other 簇。Applied Scientist 在这个簇里大约占 30-50%（具体看 title 区分）：

| 指标 | 数据 |
|---|---|
| 总岗位数 | 790 |
| 中位月薪 | 88k CNY/月（约 $148k/年） |
| p25 / p75 | 64.9k / **154k CNY/月** |
| 中位经验 | 5 年 |
| PhD 占 | 数据集中 PhD 69 / 硕士 38 / 本科 78（Applied Scientist 岗 PhD 占比比纯 Research 低） |
| 头部公司 | OpenAI、Microsoft、Anthropic、ByteDance、TikTok |
| 主要行业 | internet（业务广告 / 推荐 / 搜索 / 支付占主流） |
| 必备技能 | Python (125) / Machine Learning (88) / LLM (64) / SQL (50) / PyTorch (48) / RL (27) |

**Applied Scientist 偏向的 sample titles**：

- 「Senior Machine Learning Scientist, **Payments**」（业务向）
- 「Research Engineer, **Economic Research**」（应用向）
- 「Research Scientist, **Gemini Information Tasks**」（业务驱动研究）
- 「Senior Applied Scientist, **Search Quality**」（典型 Applied）
- 「Research Engineer, **Virtual Collaborator** (Cowork)」（产品向）

**这条线相比纯 Research Scientist 学历更宽松、节奏更快、薪资天花板稍低但中位更稳定**。

## 怎么开始

**这条线不存在「12 周速成」**。诚实说：没有硕士学历入这条线极难。

**有路径但都不快**：

**路径 A：硕士 + 工业界实习 + 业务驱动项目**（最现实）。CS / ML 硕士，期间在 Amazon / Microsoft / TikTok / Meta / Google 做实习，毕业后直接申 Applied Scientist 岗。**这是最主流的路径，2-3 年学历投入**。

**路径 B：PhD 但偏 Applied 方向**（论文不多但项目强）。CS / ML PhD，导师选偏工业界合作方向（不一定是顶会），毕业后申 Applied Scientist 而不是 Research Scientist。**4-6 年学历投入**。

**路径 C：业务数据 / 数据科学 senior → 转 Applied Scientist**（少见但可能）。在 Amazon / Google 做 6+ 年 Data Scientist + 有 ML 上线经验，内部转 Applied Scientist。**5-8 年职业投入**。

**不推荐路径**：网课 / 在线证书 / 不出名学校的硕士 + 0 工业界经验直接投。Applied Scientist 岗位 H1B 卡得严，referral 几乎是必须。

## 不适合谁

**1. 没有硕士 / PhD 学历的人**。这条线的现实是学历卡得严。**学历不够建议看 [ML Engineer](/roles/international/ml_engineer)（工程向）或 [Data Scientist](/learn/lv2/data-scientist)（业务向）**。

**2. 只想做研究 / 写 paper 的人**。Applied Scientist 不是科研岗 — 季度 OKR 要交付业务指标。**纯研究兴趣的人去申 Research Scientist 而不是 Applied**。

**3. 抵触和业务方沟通的人**。Applied Scientist 50% 时间在和广告 / 推荐 / 风控产品经理对话。**「只想关门写代码」的人在这条线会很痛苦**。

## Applied Scientist vs ML Engineer（最常问的对比）

| 维度 | Applied Scientist | ML Engineer |
|---|---|---|
| 入场 | 硕博为主 | 本科够（强工程） |
| 核心交付 | 业务方法 + A/B 收益 | 上线系统 + pipeline 稳定 |
| 论文阅读 | 必备 | 加分 |
| 工程能力 | 中等（不需要建大型分布式系统） | 高（要 hold 住 100M QPS） |
| 节奏 | 季度级实验 | 周级 deploy |
| 中位月薪 | 88k CNY/月 | 略低，约 70k CNY/月 |

## 下一步

- 想看 ml_scientist / Applied Scientist 完整数据 → [海外 ML Scientist 角色页](/roles/international/ml_scientist)
- 想看「工程向」的 ML 岗位 → [海外 ML Engineer 角色页](/roles/international/ml_engineer)
- 想看纯研究路径 → [ML Scientist Lv2 篇](/learn/lv2/ml-scientist)
- 业务数据驱动路径 → [数据分析 / 数据科学 Lv2 篇](/learn/lv2/data-scientist)
