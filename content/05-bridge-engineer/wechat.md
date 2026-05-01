# 公众号长文：OpenAI 招的 110 个工程师不是写代码的——LLM 厂商在抄 Palantir 的剧本

## 标题

「OpenAI 招的 110 个工程师不是写代码的——LLM 厂商在抄 Palantir 的剧本，但中文圈零覆盖」

## 正文

---

### 一、一个被中文圈严重低估的赛道

我做 agent-hunt 这个项目时，从 5 家 LLM 厂商的官方招聘页（OpenAI / Anthropic / xAI / Cohere / DeepMind）抓了 1,532 条 JD。

按 title 正则分类的时候，发现一个反认知的结构——

**OpenAI 651 条岗位里，110 个不是核心研发，也不是 PM。**

是「派去客户公司驻场、把 LLM 落地到业务里」的桥梁角色：Forward Deployed Engineer / Solutions Engineer / Applied Engineer / Deployment Engineer / Customer Technical Success。

**占 OpenAI 全部岗位的 16.9%。Anthropic 451 条里 61 条同类，占 13.5%。**

[图 1：5 家 vendor 客户端工程师占比柱状图]

这种岗位中文圈基本没人讲。打开任何一个 AI 培训机构的课程目录，你看到的全是「LangChain / Agent / 大模型微调 / Prompt Engineering」——面向「想转 AI 算法工程师」的人。

但市场上真实存在的、月薪 10-12 万、5+ 年门槛的资深岗位，在国内课程里完全没覆盖。

### 二、Anthropic 这条 JD 长什么样

3 条来自 OpenAI / Anthropic 官方 ATS 的真实 JD 都很一致。最直白的一条是 Anthropic 的：

**「Forward Deployed Engineer, Federal Civilian」**

- 公司：Anthropic（San Francisco / New York / Washington DC）
- 薪资：US$169,166-193,333／年 ≈ **¥101-116k／月**
- 经验：5 年+ Software Engineering
- 工作模式：Hybrid

要求：

- LLM / Python / Software Engineering / Production Application Development
- Prompt Engineering / Agent Development
- Customer-facing 经验
- US Federal Civilian Agency 经验
- 加分项：Security Clearance、TypeScript、Java、Government IT Systems

职责（直接引用 JD）：

- Build production applications with Claude models within customer systems
- Deliver technical artifacts like MCP servers, sub-agents, and agent skills
- Provide white glove deployment support for Anthropic products in federal government environments

[图 2：Anthropic Federal FDE JD 卡片]

注意三件事：

**1. 不是写论文的研究员**——要求是「在客户系统里 build production applications」。

**2. 不是只画线框图的 PM**——要交付 MCP servers / sub-agents / agent skills 这种技术 artifacts。

**3. 是工程师 + 客户沟通 + 解决方案三合一**——「white glove deployment support」这个词组本身就揭示了角色性质。

这种岗位在国内 LLM 厂商招聘里几乎找不到对应。

### 三、为什么 LLM 厂商需要这种岗？

这不是 OpenAI / Anthropic 突发奇想发明的角色。这是**抄 Palantir 已经验证了 20 年的剧本**。

**Palantir 的模式：** Palantir 给政府 / 大企业卖数据分析平台，但客户买回去自己用不起来——业务太复杂、ML 模型需要定制、跟客户内部系统整合需要专家。Palantir 的解决办法是派工程师驻场到客户公司，工程师不是研发产品，是把 Palantir 的产品在客户业务里落地。

这个角色在 Palantir 内部叫 Forward Deployed Engineer，是 Palantir 收入的核心增长引擎——卖软件 license 1,000 万美金，但 FDE 团队跟着进场，每年再卖 2,000 万的 implementation service。

**LLM 厂商现在在抄这个剧本。**

客户公司（医院 / 银行 / 政府）买了 OpenAI 的 API，但自己没有 ML 团队会用——不知道哪些业务场景适合用 LLM，不知道怎么设计 prompt，不知道怎么做 evaluation，不知道怎么处理数据治理。

于是 vendor 派 FDE 驻场，做 4 件事：

1. **评估业务场景** — 哪些业务可以用 LLM，哪些不行
2. **设计 Agent / RAG 方案** — 用哪个模型 / 怎么编排 / 怎么 retrieval
3. **在客户系统里实际部署** — MCP servers / sub-agents / agent skills，集成到客户的 IT 体系
4. **持续优化** — eval / monitoring / 迭代

这 4 步全都需要工程师能直接和客户业务方对话。**所以这不是研究员的活，也不是 PM 的活，是新一代 Palantir-style FDE 的活。**

### 四、为什么这个赛道值得关注

**1. OpenAI / Anthropic 还在大量招聘窗口期。**

171 个岗位（OpenAI 110 + Anthropic 61）集中在两家。Google / Microsoft 也在做但还没这么开放招聘。等 1-2 年所有 SaaS 都开始抄这个模式后，竞争会激烈起来。

**2. 高薪资水平 + 高门槛形成稳定护城河。**

Anthropic Federal FDE 月薪 ¥101-116k 不是 outlier。这类岗位月薪普遍 10-15 万级，因为要求是「资深 SWE/MLE + 客户沟通 + 解决方案构建」三合一，符合的人极少。

**3. 中文圈零覆盖意味着早期机会窗口。**

打开任何 AI 培训机构课程目录，你看到的全是面向「转 AI 算法工程师」的内容。FDE / Solutions Engineer 这条赛道在中文圈基本没有 mentor 也没有教程，但市场需求已经存在。这是最经典的「市场已经有，但供给端没成型」的窗口。

### 五、必须诚实说的边界

**1. 这是高门槛资深岗，不是入门级。**

明确要求「5+ 年 SWE / MLE 经验 + 客户沟通 + 解决方案构建」。不是「学完明天就能去 OpenAI 当 FDE」。这条 narrative 适合作为 3-5 年职业方向感知教学，不是明天就能转行的承诺。

如果你目前 0-3 年经验，应该先攒够 SWE/MLE 实力，再考虑这条线。

**2. 国内 LLM 厂商几乎没有这种岗。**

智谱 / Moonshot / 百川 / MiniMax 招聘里几乎零 FDE / Solutions Engineer 编制。**这条 narrative 主要适用于有出海规划的学员。**

为什么国内没有？因为国内 to-B 商业模式不同——中国客户买 SaaS 期待「免费部署 / 售前送服务」，没付费意愿支撑 vendor 派人驻场+独立计费。这是商业文化差异，不是技术问题。

如果你只在国内市场求职，这条赛道的机会不存在。

### 六、对你意味着什么

**如果你是 5+ 年 SWE / MLE，受不了纯代码岗：** 看 FDE / Solutions Engineer 方向。客户对接 + 技术深度 + 解决方案构建是这条线的差异化能力，比纯算法岗更稀缺。

**如果你是有客户对接 / 售前 / 解决方案经验的技术人：** 看 Solutions Engineer / Solutions Architect 方向。你的客户沟通能力 + 工程能力是 LLM 厂商现在最稀缺的复合型——别再只做售前演示，可以转做交付侧的实际部署。

**如果你是想出海的国内 AI 工程师，且能进入面客角色：** FDE 是天然差异化路径。比纯算法工程师转海外更有竞争力——海外算法工程师本地供给充分，但 FDE 不仅要会代码，还要美式商业文化下的客户沟通能力，门槛更高也更稀缺。

**如果你只在国内市场求职：** 这条赛道不是为你准备的。继续做国内的 AI 原生岗（互联网 + 大模型创业公司有 2,316 条 AI 原生岗）更稳。

### 七、行动

桥梁工程师 ≠ 算法工程师。

LLM 厂商在抄 Palantir 的剧本——现在加入还在窗口期。

完整 5 家 vendor 招聘数据 + 27 个角色画像 + 5 条市场判断：[agent-hunt.pages.dev](https://agent-hunt.pages.dev)

如果你想知道自己的 SWE/MLE 经验对应到 5 家 vendor 哪些具体岗位上，留言你的经验年数 + 是否有客户对接经验。

我会用 agent-hunt 数据给你一份：

- OpenAI / Anthropic / xAI / Cohere / DeepMind 五家里，对口的 FDE / Solutions Engineer 具体岗位（带 source URL）
- 月薪范围（¥CNY 月化）
- 你需要补的 3 项（基于你的经验缺口）

前 30 个免费。

---

*数据来源：agent-hunt 项目，5 家 LLM 厂商官方 ATS（OpenAI / Anthropic / xAI / Cohere / DeepMind）共 1,532 条 vendor_official 岗位。「桥梁工程师」5 类 title 正则匹配规则在 backend/scripts/export_vendor_title_breakdown.py。完整数据 + 真实 JD 例子（含 source URL）见 narrative-examples.json。分析代码开源：github.com/LLM-X-Factorer/agent-hunt*

---

## 发布清单

- [ ] 插入图 1（5 家 vendor 客户端工程师占比柱状图）在第一节
- [ ] 插入图 2（Anthropic Federal FDE JD 卡片）在第二节
- [ ] 发布时间：工作日晚 8-9 点
- [ ] 阅读原文 → agent-hunt.pages.dev/narrative/p3
- [ ] 留言区置顶：「评论你的 SWE/MLE 经验年数 + 是否有客户对接经验，前 30 个免费给一份『5 家 vendor 对口岗位（带 source URL）+ 月薪 + 缺什么 3 项』」
