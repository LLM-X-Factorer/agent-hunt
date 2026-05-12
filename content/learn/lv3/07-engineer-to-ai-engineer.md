---
title: 软件工程师 → AI Agent 工程师 (通用转岗模板)
order: 7
summary: 12 周路径：1-4 周补 LLM 调用 + Agent 框架 + RAG，5-8 周做 1 个能上线的 Agent + RAG 项目，9-12 周投国内大模型公司 / 互联网大厂 AI 团队。这条线 ROI 最高 — 国内 1538 岗位最热 + 软件工程师转 AI 跨度最小。
reading_minutes: 10
linked_professions: []
linked_roles:
  - { market: domestic, role_id: ai_engineer }
  - { market: international, role_id: sde }
---

# 软件工程师 → AI Agent 工程师 通用转岗模板

这一篇是 Lv3 转岗系列里**最通用的一篇** — 不针对某个传统职业，而是给「已经会写代码的软件工程师 / 全栈 / 后端 / 前端 / 数据工程师」一个加 AI 技能转 AI Agent 工程师的标准路径。

**为什么这条线 ROI 最高**：

- 国内 AI Agent 工程师岗位数 **1538 条**，AI 岗里数量最多
- 中位月薪 32.5k，**比传统后端 / 全栈高 30-50%**
- 软件工程师 → AI Agent 工程师跨度最小，**不像「会计 → 量化研究员」那种 18 个月起步**
- 12 周扎实做完可以拿到 offer

## 总览：12 周路径

```
第 1-4 周：补 LLM 调用 + Prompt 工程 + RAG 基础
第 5-8 周：做 1 个能上线的 Agent + RAG 项目
第 9-12 周：投国内大模型公司 / 互联网大厂 AI 团队 / Vendor 国内 BD
```

不需要辞职，工作日晚上 + 周末 8-10h / 周，总投入约 100h。

## 第 1-4 周：补技术底子

软件工程师面试 AI Agent 工程师最大的优势是「真会写代码 + 工程经验」，最大的劣势是「没用过 LLM / 没做过 RAG / 没读过 Agent 框架源码」。这 4 周补这个差距。

**Week 1：LLM 调用 + Prompt 工程**

任选 1 个 LLM 平台（**国内推荐 OpenRouter / 智谱 GLM，海外推荐 OpenAI / Anthropic**）：

- 装 SDK：`openai` / `anthropic` / `zhipuai`
- 跑通最基础的 chat completion call
- 学 Prompt 工程：System prompt / Few-shot / Chain-of-Thought / Self-Consistency
- 学 Function Calling / Tool Use
- 跑通流式输出（streaming）+ JSON 模式

**目标**：能用 100 行代码写出一个「带工具调用 + 流式输出 + JSON 解析」的 LLM 程序。

**Week 2：RAG 全链路**

RAG（Retrieval-Augmented Generation）是 AI Agent 工程师的核心技能。学这些：

- **Embedding**：text-embedding-3 / bge-m3 / m3e — 选 1 个用熟
- **向量数据库**：Pinecone / Weaviate / Chroma / Milvus — 用 Chroma 本地起步
- **Chunking 策略**：固定长度 / 语义分块 / RecursiveCharacterTextSplitter
- **Retrieval**：top_k / MMR / Hybrid search（BM25 + 向量）
- **Reranking**：Cohere Rerank / BGE Reranker

**目标**：能用 LangChain / LlamaIndex 把一个文档集（哪怕是 PDF 用户手册）做成可问答的 RAG 系统。

**Week 3：Agent 框架**

任选 1 个框架（**不要全学**）：

| 框架 | 特点 | 推荐场景 |
|---|---|---|
| **LangChain / LangGraph** | 生态最全但 API 变化快 | 通用学习 + 海外公司 |
| **AutoGen** | 多 Agent 协作强 | 复杂工作流 |
| **CrewAI** | 简单易上手 | 快速原型 |
| **Semantic Kernel** | 微软系，企业级 | C# / .NET 背景 |
| **Coze / Dify**（no-code） | 可视化拖拽 | 不写代码的 PoC |

**目标**：能用所选框架做一个 multi-agent 工作流（比如「研究员 + 写作员 + 评审员」三 Agent 协作产出研究报告）。

**Week 4：补 Eval + 评测**

这一关是 AI Agent 工程师和「只会调 API 的人」的分水岭：

- 学 LangSmith / Phoenix / Weights & Biases Traces 任选 1 个做 Agent observability
- 学 RAGAS / LangChain Evaluator 做 RAG 评测
- 学 prompt 回归测试（pytest + LLM-as-judge）

**目标**：能讲清楚「这个 Agent 在 100 条测试 case 上 success rate 87%，错的 13 条主要是 XX 类型」。

## 第 5-8 周：做 1 个能上线的项目

**Week 5：选场景 + 准备数据**

3 个推荐场景（**选 1 个，和你目标客户行业越接近越好**）：

| 场景 | 难度 | 简历价值 |
|---|---|---|
| **代码助手 Agent**（结合你公司代码库的 RAG + 工具调用） | 中 | ⭐⭐⭐⭐⭐ |
| **客服 Agent**（结合公司 FAQ + 工单系统集成 + RAG） | 中 | ⭐⭐⭐⭐ |
| **法律 / 医疗 / 金融知识库问答**（RAG + reranking + 评测） | 中 | ⭐⭐⭐⭐ |
| **多 Agent 投研工作流**（研究 + 写作 + 评审） | 高 | ⭐⭐⭐⭐⭐ |

**核心**：选一个你现在的工作 / 行业 / 公司能用上的场景，**真实 deploy 给同事用**。

**Week 6-7：做实施 + 实际部署**

完整 5 步：

1. **MVP**（Week 6 前半周）：用最少代码跑通 happy path
2. **数据准备**：清洗 + chunking + 写入向量数据库
3. **评测集**：50-100 条测试 case（手写 + GPT-4 生成）
4. **迭代**：根据评测结果调 prompt + 调 retrieval 参数 + 加 tool / agent
5. **部署**：FastAPI + Docker → 内部服务器或者 Vercel / Railway / Fly.io

**Week 8：写成项目案例 + GitHub**

包含：
- 解决的问题（业务背景 + 当前痛点）
- 系统架构图（**画清楚 Agent + Tool + RAG + Eval 四块**）
- 评测结果（success rate + 错误样本分析）
- **反思**：哪些 corner case 模型搞不定、为什么、下一版怎么改

**这是面试核心 deliverable + 代码作品**，比简历值钱 10 倍。**配 1 个 demo 视频效果更好**。

## 第 9-12 周：投简历 + 面试

**Week 9：改简历**

把原来的「N 年后端 / 全栈 / 数据工程师」升级成「N 年工程经验 + AI Agent 工程师 + 1 个真实上线项目」。
- 工程经历保留，但用「LLM 应用 / Agent 编排 / RAG 检索」这种 AI 工程语言重写
- AI side project 单独一段，附 GitHub + 架构图 + 评测数据
- 关键技能 list：LLM API / LangChain / RAG / Vector DB / Prompt Engineering / Eval

**Week 10-11：投这 4 类公司（按 priority）**

| 优先级 | 公司类型 | 推荐岗位 |
|---|---|---|
| ⭐⭐⭐ | 国内大模型创业公司 | 智谱 AI / MiniMax / Moonshot / 百川 / DeepSeek / 月之暗面 → AI Agent 工程师、LLM 应用工程师 |
| ⭐⭐⭐ | 互联网大厂 AI 团队 | 字节跳动（豆包 + Coze + AI Lab）、腾讯（混元 + AILab + 元宝）、阿里（通义 + 1688 AI）、百度（文心 + Comate）、美团（智能客服）→ AI 应用工程师 |
| ⭐⭐ | 海外公司中国团队 | OpenAI / Anthropic / Cohere / Mistral / Hugging Face → AI Engineer（英语 + 算法基础是要求） |
| ⭐ | AI 创业公司 | Coze / Dify / 飞书 AI / 钉钉 AI / 知乎直答 / 月之暗面 Kimi → AI Engineer / 全栈 AI Engineer |

**Week 12：面试 + 谈 offer**

面试常见问题：
- **「给你一个场景，怎么设计 Agent + RAG」**（最高频）→ 用你的项目架构图回答
- **「为什么用 LangChain 不用其他」**→ 讲框架对比 + 评测体系
- **「RAG 答非所问怎么 debug」**→ 讲 chunking → embedding → retrieval → reranking 四个排查层
- **「写一段代码：用 OpenAI API 实现 function calling」**→ 当场写，**这是面试基本盘**
- **「你跑过的模型评测怎么做的」**→ 用你的评测集 + LLM-as-judge 回答

谈薪：软件工程师 → AI Agent 工程师起薪范围：

- **国内大模型公司**：25-50k（3 年经验起），senior 能到 60-100k
- **互联网大厂 AI 团队**：30-60k（强工程背景），senior 70-120k
- **海外公司中国团队**：50-100k+（英语 + 强工程基础）

## 不要犯的 3 个错

**1. 不要把 4 个 Agent 框架都学一遍**。**学 1 个用透 >> 学 4 个都浅**。LangChain / AutoGen / CrewAI 学一个就够，面试官只问你最熟的那个。

**2. 不要做「玩具 demo」就停**。简历上「我做过 ChatPDF」这种 demo 项目，**已经被简历筛掉的标志**。要做能上线 + 有真实用户 + 有评测数据的项目。

**3. 不要去学训模型 / 写 attention**。AI Agent 工程师**不需要会训模型**。这条线和 [算法工程师](/learn/lv2/algorithm) 是平行线。**手撕 Transformer 是浪费 60% 时间**。

## 12 周后你应该长什么样

- LLM 调用 + Prompt 工程 + RAG + Agent 框架熟练
- 1 个 GitHub 上 + 真实上线的 Agent 项目（含架构图 + 评测）
- 一份项目案例报告（含 success rate + 错误样本分析）
- 改造后的简历 + 求职信
- 投了 20-40 家公司 + 拿到 8-12 个面试 + 3-6 个 offer

**核心是 100h 时间 + 你已有的工程基础**。这条路 95% 的软件工程师能成。

## 长期成长方向

- **第 1 年**：在大模型公司 / 大厂 AI 团队做 AI Agent 工程师，跑 3-5 个真实业务 case
- **第 2-3 年**：升 senior，主导 AI 平台 / 框架建设
- **第 3-5 年**：AI Tech Lead / Staff Engineer → 月薪 60-120k 可达
- **海外路径**：英语过硬 + 强项目 → 投 OpenAI / Anthropic / Mistral 海外岗 — 起薪 $250-450k

## 各路线的对比（这条线 vs 其他 Lv3）

| Lv3 路径 | 难度 | ROI（薪资 / 投入时间） | 12 周成功率 |
|---|---|---|---|
| **软件工程师 → AI Agent 工程师**（本篇） | 中低 | ⭐⭐⭐⭐⭐ | 95% |
| 销售 → AI 销售 | 低 | ⭐⭐⭐⭐⭐ | 90% |
| 教师 → AI 教育 PM | 低 | ⭐⭐⭐⭐ | 85% |
| 机械 → 自动驾驶 | 中 | ⭐⭐⭐⭐ | 75% |
| 电气 → 智能制造 / 自动驾驶 | 中 | ⭐⭐⭐⭐ | 70% |
| 会计 → AI Finance | 中 | ⭐⭐⭐ | 70% |
| 金融 → 量化研究员 | **极高** | ⭐⭐⭐⭐⭐（顶薪但难） | 30%（12 周拿不到顶级量化 offer，需 6-12 个月） |

## 下一步

- 想看 AI Agent 工程师完整数据（薪资分位 / 头部公司 / 高频技能）→ [国内 AI 工程师角色页](/roles/domestic/ai_engineer)
- 想看海外 SDE（英语 + 海外路径）→ [海外 SDE 角色页](/roles/international/sde)
- 想看算法工程师的平行线（造模型 vs 用模型）→ [算法工程师 Lv2 篇](/learn/lv2/algorithm)
