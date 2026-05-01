# X Thread：海外 17% 是桥梁工程师，国内课程零覆盖

> 数据基线：v0.11（2026-05）—— 5 家 LLM 厂商官方 ATS / OpenAI 651 + Anthropic 451 + xAI 230 + Cohere 115 + DeepMind 82
> 对应 narrative p3 桥梁工程师：https://agent-hunt.pages.dev/narrative/p3

---

## Thread（7 条）

### 1/7（钩子）

OpenAI 招聘里有 110 个工程师不是写代码的——

是「派去客户公司驻场、把 LLM 落地到业务里」的桥梁角色。月薪 ¥10-12 万，5 年+ 经验。

Anthropic 同样招 61 个。**国内 LLM 课程零覆盖。**🧵

### 2/7（核心数字）

「桥梁工程师」= 把 LLM 落地到客户业务的工程师。

5 类 title 里命中其一：
· Forward Deployed Engineer
· Solutions Engineer / Architect
· Applied Engineer
· Deployment / Implementation Engineer
· Customer / Technical Success Engineer

5 家 LLM 厂商招聘里：

· OpenAI 651 条 / 110 条命中 = **16.9%**
· Anthropic 451 条 / 61 条命中 = **13.5%**
· xAI / Cohere / DeepMind 比例较低但都有

[附图 1：5 家 vendor 客户端工程师占比柱状图]

### 3/7（最直白的例子）

📍 Anthropic 「Forward Deployed Engineer, Federal Civilian」 → ¥101-116k / 月

要求：
· 5 年+ Software Engineering 经验
· LLM / Python / Prompt Engineering / Agent Development
· Customer-facing 经验
· US Federal Agency 经验
· （加分项：Security Clearance、Government IT Systems）

不是写论文的研究员，也不是只画线框图的 PM。
**是工程师 + 客户沟通 + 解决方案三合一。**

### 4/7（机制：Palantir 已经验证 20 年）

为什么 LLM 厂商需要这种岗？

客户公司（医院 / 银行 / 政府）买了 OpenAI / Anthropic 的 API，但自己没有 ML 团队会用——

于是 vendor 派工程师驻场：
1. 评估业务场景
2. 设计 Agent / RAG 方案
3. 在客户系统里实际部署
4. 持续优化

这 4 步全都需要工程师能直接和客户业务方对话。

**这不是新发明——Palantir 已经验证 20 年。OpenAI 现在大量招 FDE 就是抄 Palantir 的剧本。**

### 5/7（适用边界，避免被反驳）

注意 2 件事：

1. **这是高门槛资深岗**。要求「5+ 年 SWE / MLE 经验 + 客户沟通 + 解决方案构建」——不是入门级，不是「学完明天就能去」。这条赛道适合作为 3-5 年职业方向感知，不是明天转行
2. **国内几乎没有这种岗**。智谱 / Moonshot / 百川 / MiniMax 招聘里几乎零编制——中国 to-B 客户期待「免费部署 / 售前送服务」，没付费意愿支撑 vendor 派人驻场。**这条 narrative 主要适用于有出海规划的人**

### 6/7（如果你是这些人）

桥梁工程师 ≠ 算法工程师。

适合这条路的人画像：

· **5+ 年 SWE / MLE 经验** 的资深工程师，不想再只写纯代码
· **有客户对接 / 售前 / 解决方案** 经验的技术人，想做更有杠杆的工作
· **想出海的国内 AI 工程师**，且能进入面客角色的人（这是天然差异化路径）

LLM 厂商在抄 Palantir 的剧本——现在加入还在窗口期。等 1-2 年所有 SaaS 都开始抄这模式后，竞争会激烈起来。

### 7/7（收尾 + 引流）

数据：5 家 LLM 厂商官方 ATS（OpenAI / Anthropic / xAI / Cohere / DeepMind）共 1,532 条 vendor_official 岗位 title 正则分类。

完整数据 + 5 条市场判断 → agent-hunt.pages.dev/narrative/p3

评论你的 SWE / MLE 经验年数 + 是否有客户对接经验。

我用 agent-hunt 数据给你一份：

· OpenAI / Anthropic / xAI / Cohere / DeepMind 五家里，对口的 FDE / Solutions Engineer 具体岗位（带 source URL）
· 月薪范围（¥CNY 月化）
· 你需要补的 3 项（基于你的经验缺口）

前 30 个免费。

---

## 发布清单

- [ ] 图 1（5 家 vendor 客户端工程师占比柱状图）附在第 2 条
- [ ] 图 2（Anthropic Federal FDE JD 卡片）附在第 3 条
- [ ] 发布时间：工作日上午 9-10 点
- [ ] 评论区补一条方法论：「桥梁工程师 5 类 title 正则匹配规则在 backend/scripts/export_vendor_title_breakdown.py 里」
- [ ] 24h 后看反馈，如果第 4 条「Palantir 已验证 20 年」最有共鸣，小红书可以做 Palantir 模式深度拆解

## 注意事项

- 不要说「学完明天就能去 OpenAI 当 FDE」——5 年门槛硬性，避免承诺误导
- 不要把「~17%」吹成「OpenAI 大部分人是 FDE」——OpenAI 651 条里仍是 core 研发为主（541 条）
- 不要在国内市场角度过度推这条——国内 LLM 厂商几乎零编制，主要适用于出海人群
- 业务话术对应 narrative p3 的 copyText：「OpenAI 和 Anthropic 招聘里，约 17% 是『Forward Deployed / Solutions / Applied / Implementation Engineer』——把 LLM 落地到客户业务的桥梁工程师」
