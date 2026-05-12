---
title: Prompt 工程师 / AI 训练师 — 这职业到底是干啥的
order: 16
summary: 这是 AI 时代分化最严重的岗位 — 同一个 title 下面塞了 3 种完全不同的活：高端 Prompt Engineer（$300k+，OpenAI / Anthropic 极少数）/ 中端 AI 训练师（15-30k，国内大模型公司）/ 低端 LLM 数据标注（8-15k 零工）。要选对哪一档，否则白干。
reading_minutes: 7
linked_roles:
  - { market: domestic, role_id: education_ai }
  - { market: domestic, role_id: ai_engineer }
---

# Prompt 工程师 / AI 训练师 — 这职业到底是干啥的

把 AI 训练师想成**动物园的驯兽师**。

不是「养动物」（那是饲养员） — 是**教动物做特定的事**：让海豚跳圈、让狗坐下、让大象画画。

**Prompt 工程师做的就是「教 AI 做特定的事」** — 让 GPT-4 写法律意见书 / 让 Claude 做客服 / 让国内大模型按你想要的格式输出。

**但有个问题**：这个比喻看起来很美好，**真实的 Prompt 工程师岗位市场分化非常严重**。看名字以为是「玩 AI 拿高薪」 — 实际上同一个标题下面塞了 3 种完全不同的工作，**薪资能差 5-10 倍**。

## ⚠️ 这条线最大的坑：3 种「Prompt 工程师」差异巨大

| 类型 | 真实工作内容 | 月薪 | 岗位数量 | 难度 |
|---|---|---|---|---|
| **高端 Prompt Engineer** | 在 OpenAI / Anthropic 设计模型行为规范、做 RLHF 数据策略、写公司级 prompt 库 | **$200-400k/年（120-250k CNY/月）** | 全球极少（每家公司 5-20 人） | 极高（PhD / 顶尖 ML 背景） |
| **中端 AI 训练师 / 应用 prompt** | 在国内大模型公司 / AI 应用公司，写产品级 prompt、做评测、调 Agent 工作流 | **15-30k** | 国内大概几百条 | 中（懂 LLM + 业务） |
| **低端 LLM 数据标注 / 训练专家** | 给 LLM 公司做领域数据标注（xAI 招的「Finance Expert」「Accounting Expert」「Medical Expert」） | **8-15k** | 国内大量（xAI / Anthropic / Cohere 在招） | 低（懂领域知识，**没职业 progression**） |

**这是 AI 时代最容易踩坑的岗位**。看到 OpenAI 招「Prompt Engineer」开 30 万美元的新闻就以为自己也能拿，**结果投了一圈发现国内的「AI 训练师」是月薪 12k 的数据标注外包**。

## 三档岗位分别长什么样

### 高端 Prompt Engineer（OpenAI / Anthropic / Google DeepMind）

agent-hunt 没有专门 cluster — 这些岗位散落在 ml_scientist / ml_engineer / 其他簇里。

**真实长相**：
- title: 「Member of Technical Staff, Model Behavior」「Research Engineer, Prompt Strategy」
- 工作：设计公司级 prompt 库 / 做 RLHF 数据策略 / 训练 instruction-following 数据集 / 给客户调企业级 prompt
- 要求：CS / ML PhD or 顶尖硕士 + 强 ML 背景 + 在 OpenAI / Anthropic / 头部 AI 公司 referral
- **数量极少**：全球可能只有几百个真正的「Prompt Engineer」岗位

**普通人想入这条线 = 想入 Research Scientist 那条线**，需要 4-6 年 PhD 投入。

### 中端 AI 训练师 / 应用 Prompt 工程师（国内大模型公司）

agent-hunt 国内 ai_engineer 簇有这类岗位（prompt_engineering 在 required_skills 出现 9 次）+ education_ai 簇有 30 条「AI 教育讲师 / AI 训练师」类岗位。

**真实长相**：
- title: 「AI 训练师」「Prompt 工程师」「LLM 应用工程师」「智能体训练师」
- 工作：写产品级 prompt（客服 / 写作 / 翻译 / 代码助手）+ 跑评测集 + 调 Agent 工作流 + 和算法 / 工程师配合迭代
- 要求：本科 + 懂 LLM 基础 + 1-2 年 prompt 调优经验
- 薪资范围（基于 agent-hunt education_ai 簇）：**median 14.75k，p75 30k**，少数顶档能到 40-50k

**这条线在国内大模型公司（智谱 / MiniMax / Moonshot / 百川 / 字节豆包）+ AI 应用公司（Coze / Dify / 飞书 AI）真实在招**，但**数量比 AI Agent 工程师少一档** — 多数公司更愿意招会写代码的工程师（让工程师自己写 prompt），而不是单独招 prompt 工程师。

### 低端 LLM 数据标注（xAI / Anthropic / Cohere）

这是**国内最多的「Prompt Engineer / AI 训练师」岗位**。agent-hunt 在多个传统职业 + AI 簇里都抓到这类样本。

**真实长相**：
- title: 「Finance Expert - Fixed Income」「Accounting Expert - Technical Accounting」「Medical Expert」「Legal Expert」
- 工作：在标注平台上给 LLM 做领域问答数据 — 你写一个金融 / 会计 / 医疗问题 + 你写「好答案」+ 你评估模型生成的答案
- 要求：本科 + 领域专业背景 + 英语流利
- 薪资：**$10-25/小时（8000-15000 月薪）**，按时计费，无 base + 提成
- 工作形式：**承包 / 兼职 / 短期合同**（3-6 个月），项目结束即终止
- **职业 progression：几乎为 0**

**这是 AI 时代职业陷阱**：表面上是「AI 公司在招你」，实际上是**给 AI 模型当人肉训练数据生产者**。简历上写 6 个月「xAI Finance Expert」对未来跳槽不加分。

## 真实数据：education_ai 簇（最接近中端 AI 训练师）

agent-hunt 国内 `education_ai` 簇 **30 条岗位** — 最接近「中端 AI 训练师」的画像：

| 指标 | 数据 |
|---|---|
| 国内岗位数 | 30 |
| 中位月薪 | **14.75k**（p25 8k / p75 30k） |
| 中位经验 | 1 年（**门槛最低**） |
| 学历分布 | 任意 15 / 本科 9 / 硕士 6（学历卡得宽） |
| 主要行业 | education（20）、internet、government |
| 头部公司 | 国内 AI 教育公司 + 政府教育数字化项目 |

sample titles：「AI 高级人工智能教育讲师」「人工智能教育推广员」「智能教育产品交付与服务经理」「市场经理 - AI+教育」。

**注意中位 14.75k 是国内所有 AI 岗里中位最低的一类** — 反映这条线**虽然热但供过于求、定价偏低**。

## 怎么开始（如果你真的想做这条线）

**第一件事：先想清楚你要哪一档**。3 档完全是 3 个不同的职业。

### 如果想做高端 Prompt Engineer（OpenAI / Anthropic）

**诚实建议**：这条线和 Research Scientist 是同一条 — 看 [ML Scientist Lv2 篇](/learn/lv2/ml-scientist) 那里的路径。**12 周课程班拿不到这种岗位**。

### 如果想做中端 AI 训练师 / Prompt 工程师

**第一步**：吃透 1 个 LLM（ChatGPT / Claude / 智谱 GLM / 文心一言）— 用 6 个月成为「玩 prompt 玩到极致」的人。

**第二步**：做 5-10 个真实业务场景的 prompt 项目（客服 / 写作 / 翻译 / 代码助手），**写技术博客 + 上传 GitHub**。

**第三步**：用 Coze / Dify 做 2-3 个 Agent demo（不要只是 prompt，要有工具调用 + RAG）。

**第四步**：target 国内大模型公司应用团队 + AI 教育 / 内容 / 客服领域公司。

**重要：实际上这条线对会写代码的人有强偏好** — **建议同时学一点 Python**，然后投 [AI Agent 工程师](/learn/lv2/ai-engineer) 岗位（中位 32.5k，比纯 prompt 训练师高一倍）。

### 如果想做 LLM 数据标注（不推荐做长期）

诚实建议：**避开**。这条线**对未来跳槽不加分**，月薪上限 1.5 万左右没有 progression。如果你急需要钱可以做 3 个月过渡，但不要把这当成「转 AI」。

## 不适合谁（每一档都列）

**1. 误以为「玩 prompt 就能拿高薪」的人**。高端 Prompt Engineer 岗位极少 + 学历卡得严，**普通人投了基本沉**。

**2. 完全不会写代码 + 想做 AI 训练师的人**。国内大模型公司更愿意招会写代码的工程师（让工程师自己写 prompt）— **不会代码 + 单做 prompt 的人会被边缘化**。

**3. 抵触领域知识 + 想做泛 prompt 工程师的人**。中端 prompt 训练师必须有一个领域专长（教育 / 金融 / 医疗 / 客服）— **「我会写通用 prompt」不是简历亮点**。

## 这条线的本质判断

**如果让我给一个建议**：

- 想拿高薪 + 有 ML 背景 → 做 [ML Scientist](/learn/lv2/ml-scientist) 或 [算法工程师](/learn/lv2/algorithm)
- 想拿中等 + 工程背景 → 做 [AI Agent 工程师](/learn/lv2/ai-engineer)（中位 32.5k，比 AI 训练师高一倍）
- 想拿中等 + 教育 / 内容背景 → 做 AI 产品 / 内容 / 训练师，但**心理预期月薪 15-30k**
- **完全不要做 LLM 数据标注作为长期职业**

「Prompt Engineer」这个 title 在 AI 行业的真实定位是**辅助岗** — 不是核心生产端。**核心生产端是工程师 + 算法 / 研究员**。

## 下一步

- 想做技术含量更高的 AI 应用岗 → [AI Agent 工程师 Lv2 篇](/learn/lv2/ai-engineer)
- 想了解 AI 教育这条线（最容易入但天花板低）→ [国内 AI 教育角色页](/roles/domestic/education_ai)
- 想看高端 ML Scientist 这条线 → [ML Scientist Lv2 篇](/learn/lv2/ml-scientist)
- 教师背景想转 AI 教育 → [教师 Lv2 篇](/learn/lv2/teacher) + [教师 → AI Education Lv3 篇](/learn/lv3/teacher-to-ai-education)
