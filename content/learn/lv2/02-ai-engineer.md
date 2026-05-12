---
title: AI Agent 工程师 — 这职业到底是干啥的
order: 2
summary: AI Agent 工程师不是「训练大模型的人」，是「在大模型上面盖应用的人」。国内 1538 个岗位最热，中位月薪 32.5k，比国内 AI 整体高一档。
reading_minutes: 6
linked_roles:
  - { market: domestic, role_id: ai_engineer }
---

# AI Agent 工程师 — 这职业到底是干啥的

如果说大模型是发电厂，那 AI Agent 工程师就是**装空调、装灯、装电梯的工程队**。

发电厂（OpenAI、Anthropic、智谱、MiniMax）不直接给你电费收据，它们卖电（API）。装电的人才是让普通用户「按一下开关，房间就亮」的人。

**这就是 AI Agent 工程师做的事**：把现成大模型接成一个能上线给用户跑的产品流程。

## AI Agent 工程师做什么（具体）

打个比方。客户说：「我想要一个客服机器人，能查订单、能退款、能转人工。」

传统后端工程师会去写一堆 if-else + 数据库查询，三个月做完，还需要不停加规则。

AI Agent 工程师做法不一样：

1. **把大模型当大脑**：用 GPT-4 / Claude / 智谱 GLM 当推理引擎
2. **设计工具**：写几个函数（query_order、issue_refund、transfer_human），告诉大模型「这是你能用的工具」
3. **写 prompt**：告诉大模型「你是客服，根据用户输入决定调哪个工具」
4. **挂上 RAG**：把退款政策文档塞进向量数据库，让大模型查文档而不是凭记忆答
5. **加上日志评测**：每天看 100 条对话，看哪些场景模型答错了，回去改 prompt 或加工具

整个流程 2 周可以拉起 MVP。**这就是「Agent + Tool + RAG」的工程范式**。

## 三套硬核能力

**1. 熟一套 Agent 框架。** LangChain / AutoGen / 智谱的 AutoGLM / Microsoft Semantic Kernel — 至少熟一套，能从 0 拉起一个能上线的多 Agent 工作流。**面试代码题往往是「设计一个多 Agent 协作流」**，不是手撕 Transformer。

**2. RAG 全链路调通。** 知道怎么切文档（chunking）、怎么选 embedding 模型、怎么调 retrieval top_k、怎么做 reranking。**调不调得通 RAG 是 AI Agent 工程师和「只会用 ChatGPT 的人」的分水岭**。

**3. Prompt 工程 + 评测。** 不是「写了一句 prompt 跑通了」就行。要会设评测集（10-100 条 case）、跑回归、看模型在 corner case 上的退化。**这是从「玩具 demo」到「线上产品」最大的一道坎**。

## AI Agent 工程师的真实数据

Agent Hunt 抓到国内 **1538 条 AI Agent 工程师岗位**，是国内最大的 AI 岗位簇（v0.12 ByteDance 数据合并后）。

| 指标 | 数据 |
|---|---|
| 国内岗位数 | 1538 |
| 中位月薪 | 32.5k（p25 20k / p75 50k，样本 417 条） |
| 中位经验要求 | 3 年 |
| 头部公司 | 字节跳动、腾讯、MiniMax、智谱 AI、Moonshot |
| 最高频技能 | LLM (116) / Agent 架构 (60) / Python (35) / RAG (23) |

**32.5k 比国内 AI 岗位整体中位（27.5k）高一档** — 是工程实战门槛兑现溢价的位置。AI 大模型创业公司（智谱、MiniMax、Moonshot、百川）几乎全在挂这类岗，没有学历硬指标，看简历卡的就一件事：**有没有做过能上线的 Agent / RAG 项目**。

## 怎么开始

**第一步：做完一个 Agent 项目。** 用 [Coze](https://www.coze.cn/) / [Dify](https://dify.ai/) 这种 no-code 平台先做一个能跑的 Agent（客服 / 笔记助手 / 知识库问答都行）。**用 1 周时间做完一个**，写到简历里。

**第二步：换成代码版。** 同一个项目，用 LangChain 或 LlamaIndex 重写一遍。重点是体会「框架到底帮你做了什么」。这个过程 2-3 周。

**第三步：上 RAG 大菜。** 找一个真实文档集（公司文档 / 法律条款 / 医学指南），做一个 RAG 系统。学会怎么评测「答得对不对」、怎么调 chunking 和 retrieval。**这一关过了才算是 AI Agent 工程师**。

**第四步：投头部公司。** 国内优先：字节跳动 / 腾讯 / MiniMax / 智谱 / Moonshot / 百川。这几家几乎全年挂位置，不挑学校但挑项目。

## 不适合谁

**1. 完全没碰过 LLM 调用、只会传统 CRUD 后端的人**。这条线现在岗多但卡简历的「AI 项目经验」门槛清晰，没产出物投了基本沉。

**2. 想做研究 / 训模型的人**。这条线是「用模型」不是「造模型」。如果你想训自己的模型 / 发 paper，去看 [算法工程师](/roles/domestic/algorithm) 那条线。

**3. 想避开后端工程化的人**。Agent 工程师本质还是工程师 — 要写代码、要部署服务、要值班看监控。**不是「写 prompt」一个动作就能交付**。

## 下一步

- 想看 AI Agent 工程师完整数据（薪资分位 / 头部公司 / 技能频次）→ [国内 AI 工程师角色页](/roles/domestic/ai_engineer)
- 想看「用模型 vs 造模型」的区别 → [算法工程师 Lv2 篇](/learn/lv2/algorithm)
- 想看 AI 产品经理怎么和 Agent 工程师配合 → [AI 产品经理 Lv2 篇](/learn/lv2/product-manager)
