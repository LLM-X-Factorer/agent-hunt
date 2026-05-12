---
title: 蛋糕列描述：required vs preferred 是什么
order: 4
summary: 一份 JD 就是一块订单蛋糕 — required 是「必须做出来的蛋糕主体」，preferred 是「希望有的装饰」。看错这两个，要么投太晚要么投不出去。
reading_minutes: 6
linked_roles:
  - { market: domestic, role_id: ai_engineer }
---

# 蛋糕列描述：required vs preferred 是什么

想象你去蛋糕店订一个生日蛋糕。

你给老板的描述是：

> 「我要一个 8 寸巧克力蛋糕，必须用真奶油，必须写名字 — 如果能再加点草莓装饰更好，能用可可粉撒字也行。」

这里面有**两类要求**：
- 必须做到的（8 寸 / 巧克力 / 真奶油 / 写名字）
- 锦上添花的（草莓装饰 / 可可粉撒字）

如果老板不会做巧克力，**这单他直接拒**；
如果老板会做巧克力但没草莓，**他可以接 + 跟你商量「我用蓝莓换吗」**。

**JD 里的 required（硬性要求）和 preferred（加分项）就是这个逻辑。**

## 在 JD 里怎么辨认

中文 JD 里通常分两个 section：

```
任职要求 / 岗位要求：    ← 这是 required
  1. 本科及以上学历...
  2. 熟练掌握 Python 和 PyTorch...
  3. 3 年以上 LLM 相关经验...

加分项 / 优先项：        ← 这是 preferred
  1. 有 Agent 框架项目经验
  2. 熟悉 RAG 系统
  3. 有大型企业 ToB 经验
```

英文 JD 里更明显：

```
Requirements:           ← required
Preferred Qualifications: 或 Nice to Have:  ← preferred
```

**有时候 JD 不分两块，所有条款都列在「任职要求」里**。这时候要看语气词区分：

| 语气 | 类型 | 例子 |
|---|---|---|
| 必须 / 掌握 / 精通 / 至少 X 年 | required | 「必须熟练 Python」 |
| 熟悉 / 了解 / 优先 / 有 X 经验佳 | preferred | 「熟悉 LangChain 优先」 |
| 加分 / 优势 / nice to have | preferred | 「有论文加分」 |

## 谁能投：80% required hit 法则

简单决策规则：

```
你能 hit required 列表里 80% 的条款 → 可投
你能 hit required 50-80% → 看 preferred 加分多不多
你能 hit required < 50% → 别投，浪费简历配额
```

**preferred 不达标完全没关系**。preferred 是公司给「理想候选人」画的像，但找不到理想候选人时，他们会降级要 required 都 hit 上的人。

## 一个反例：preferred 看起来很吓人

我给你看一段真实的 OpenAI Account Executive JD：

**Required**：
- 5+ years sales experience
- Track record selling complex products

**Preferred**：
- Experience selling AI/ML products
- Familiar with developer tools market
- PhD or technical degree

不少销售看到「博士学位 + AI/ML 销售经验 + dev tools」就以为自己被卡了，**直接不投**。

但 preferred 全部不 hit 的销售依然能拿这个 offer — 只要你 5 年销售经验过硬、能讲清楚怎么卖复杂产品。OpenAI 没找到完美候选人的话，会很乐意要这种 90% hit required 的人。

## 一个正例：required 不达标硬投

反过来 — 你能 hit 80% required + 1-2 个特别强的 preferred，也可以试投。

例子：JD 写「3 年 ML 经验 + Python + PyTorch」，你只 2 年经验（差 1 年 required），但你有**「在 Kaggle 拿过 3 次金牌」**这个 preferred — 简历看到的人 100% 会给你面试。

**preferred 里的「特别项目 / 论文 / 竞赛 / 公开模型」**比 required 里的「年限」权重高得多。

## 别犯的 3 个错

**1. 不要被 preferred 唬住而不投。** 80% required hit 就投，preferred 缺 50% 都没关系。

**2. 不要把 preferred 当 required 学。** 学习时间稀缺。**先把目标岗位 required 列表里你缺的补齐**，再考虑 preferred 提升竞争力。

**3. 不要忽视语气词。** 「了解 LangChain」≠「熟练 LangChain」。前者是 preferred 不会也能投；后者是 required，不熟练写到简历会面试穿帮。

## 实战：你的目标岗位 required 是什么

去 [岗位画像](/roles) 找你想做的角色，每个角色页都有「技能画像 — Required（在 JD 中作为硬性要求）vs Preferred（加分项）」的柱状图。**条款是按 JD 里出现次数排序的**，所以越靠前 = 越「真硬」。

例子：[AI/LLM 工程师](/roles/domestic/ai_engineer) 角色页里看到 Required 第 1 名是「大语言模型 (LLM)」出现 312 次 — 这就是这条线最硬的要求，简历里没体现这点基本面试都拿不到。

## 下一步

- 读完 Lv1 想看自己具体职业 → [传统职业](/professions)
- 读完 Lv1 想看具体 AI 岗 → [岗位画像](/roles)
- 国内外 JD 写法完全不同？看 → [Lv1-05](/learn/lv1/domestic-vs-overseas)
