---
title: ML Scientist / Research Scientist — 这职业到底是干啥的（海外）
order: 5
summary: ML Scientist 是「发论文 / 训新模型 / 推 SOTA」的研究岗，不是工程岗。海外 790 条岗位，中位 88k CNY/月，p75 154k，是数据集里中位最高的几条线之一。PhD + 顶会论文是硬通货。
reading_minutes: 7
linked_roles:
  - { market: international, role_id: ml_scientist }
---

# ML Scientist — 这职业到底是干啥的

如果说算法工程师是「造发电机的」，**ML Scientist 就是「研究发电原理 + 发明新发电方式的人」**。

发电机能造出来，背后是 200 年物理学积累。每年都有一小部分科学家在实验室里搞「新一代发电方式」（核聚变 / 量子能源），他们做的事 90% 是失败，但只要 10 年出一个突破，整个发电工业升级一代。

**ML Scientist 做的就是这件事 — 在 OpenAI / Anthropic / DeepMind / Meta FAIR 这种地方，研究下一代 LLM 怎么训、新的 RL 方法怎么用、多模态怎么对齐**。

## ML Scientist 做什么（具体）

公司说：「我们的下一代模型要解决 long-context 退化问题。」

ML Scientist 做法：

1. **读 paper**：扫一遍 long-context 这个子方向最近 2 年的 30-50 篇论文，找现有方法的缺陷
2. **提一个新方法**：「我猜如果在 attention 里加个 XX 机制，长上下文 retrieval 准确率能涨」
3. **小规模验证**：在 1B 参数的小模型上跑 ablation 实验，证明这个方法在受控环境下有效
4. **大规模训练**：跟工程团队合作，在 100B+ 参数的真实模型上跑训练，看效果是否 scale
5. **写论文 + 投顶会**：NeurIPS / ICML / ACL — 这是「研究成果交付物」
6. **回到第 1 步**：1 个研究方向跑下来 6-18 个月，**90% 是失败的，但 10% 的成功改变行业**

这是一份**研究工作**，输出是论文 / 模型权重 / benchmark，不是产品。

## 三套硬核能力

**1. 论文阅读 + 复现 + 提新方法。** 看到一篇新 paper，能在 1-2 周内复现核心结果 + 找到论文的局限 + 想出改进方向。**这是博士训练 5 年才打磨出来的能力**，不是「学个课」就能有。

**2. 数学（线代 / 概率 / 优化）+ 实验设计。** 不只是会调超参，是知道为什么这个超参对这类任务有效。**懂泰勒展开 / SGD 收敛性 / 梯度爆炸的物理原因**。看一眼 loss 曲线就能猜到是什么问题。

**3. 大规模训练的工程能力（不是「会用 PyTorch」）。** 训练 100B 参数模型涉及：3D 并行、ZeRO 优化、混合精度、checkpoint 容错、TPU/GPU 调度。**ML Scientist 不需要全栈懂，但要能和工程团队的人对话**。

## ML Scientist 的真实数据

Agent Hunt 抓到海外 **790 条 ML Scientist / Research Scientist 岗位**，是海外数据集里第二大非 other 簇：

| 指标 | 数据 |
|---|---|
| 海外岗位数 | 790 |
| 中位月薪 | **88k CNY/月**（约 $148k/年） |
| p25 / p75 | 64.9k / **154k CNY/月** |
| 顶尖薪资 | 顶尖 lab 的 staff scientist 实际打到 200k+ CNY/月（超过 $30 万/年）不少见 |
| 中位经验要求 | 5 年 |
| 头部公司 | OpenAI、Microsoft、Anthropic、ByteDance、TikTok |
| 学历分布 | PhD 69 / 硕士 38 / 本科 78（看似本科多，**实际 senior 岗 PhD 几乎占绝对多数**） |
| 最高频技能 | Python (125) / Machine Learning (88) / LLM (64) / SQL (50) / PyTorch (48) / RL (27) |

**154k CNY/月的 p75 是海外数据集里最高的几条线之一** — 顶尖 ML Scientist 的薪资天花板甚至高于大多数 VP 级管理岗。

sample titles 反映这条线的真实长相：「Senior ML Scientist, Payments」「Research Engineer, Virtual Collaborator」「Research Scientist, Gemini Information Tasks」「Research Economist, Economic Research」— 既有大模型方向，也有 Applied Scientist（把 ML 应用到广告 / 推荐 / 风控等具体业务）。

## 怎么开始

**这条线不存在「速成」**。诚实说：如果你没有 PhD 或顶会论文，进顶尖 ML Scientist 岗位的概率约 5%。

但有路径：

**路径 A：读 PhD（最稳）**。AI / ML / CS PhD，导师选 LLM / RL / 多模态方向，4-6 年发 5-10 篇顶会，毕业后投 OpenAI / Anthropic / DeepMind。**这条线 80% 的人走这条路**。

**路径 B：硕士 + 工业界研究实习 + 论文（有概率）**。硕士读 CS/ML，期间在 OpenAI / Meta / Google / 字节 AI Lab 实习 + 发 1-2 篇顶会一作。**毕业能进 Applied Scientist 岗位（比 Research Scientist 稍低一档但还是研究岗）**。

**路径 C：开源 / Kaggle / 公开模型大神（小概率）**。Hugging Face / GitHub 上有广为人知的开源模型，写过 1k+ star 的训练 / 评测框架，参加 Kaggle 拿过 Gold。**没有学历但有「证明你能做研究」的工件**。

**不推荐的路径**：网课 + 跳过本科 / 硕士直接投。这条线 ATS 卡学历 + paper 卡得最严。

## 不适合谁

**1. 工程背景没有研究产出的人**。海外 ML Scientist 高度依赖 publication 和 referral，**没有任何「研究证明」很难拿到面试**。如果你做的是工程，看 [ML Engineer](/roles/international/ml_engineer) 那条线，门槛低很多。

**2. 想要快速看到产品上线的人**。研究节奏慢。一个项目 6-18 个月，可能最后什么都没做出来。**喜欢「这周上线」节奏的人会窒息**。

**3. 不爱写论文的人**。这条线的硬通货就是 paper。**不发 paper = 没有 promotion 凭据**。如果你享受动手做东西但讨厌写作，建议看 ML Engineer。

## ML Scientist vs ML Engineer（最常问的对比）

| 维度 | ML Scientist | ML Engineer |
|---|---|---|
| 核心交付 | 论文 / 新方法 / 模型权重 | 上线系统 / 部署 / pipeline |
| PhD 偏好 | 极强（90%+ 是 PhD） | 弱（本科硕士都可以） |
| 中位月薪 | 88k CNY/月 | 略低，约 70k CNY/月（数据集中） |
| 节奏 | 半年起的研究项目 | 周级 / 月级的工程迭代 |
| 必备 | 论文阅读 + 数学 + 实验设计 | PyTorch + 部署 + 数据 pipeline |
| 转岗难度 | 工程 → 研究 难 | 研究 → 工程 易 |

## 国内有没有 ML Scientist 这条线

有，但**少得多**。国内对应的是「LLM 算法工程师 / 研究员」，并入 [algorithm 角色](/roles/domestic/algorithm)。

国内研究岗集中在：智谱 AI、MiniMax、Moonshot、百川、字节跳动 Seed、腾讯 AI Lab、阿里达摩院、上海 AI Lab。**学历卡得比海外更严** — 本科硕士进得到 algorithm 工程岗位，进研究岗几乎只看博士 + 顶会。

## 下一步

- 想看 ML Scientist 完整数据 → [海外 ML Scientist 角色页](/roles/international/ml_scientist)
- 想看「研究 vs 工程」的工程那条线 → [ML Engineer 角色页](/roles/international/ml_engineer)
- 国内对应路径 → [算法工程师 Lv2 篇](/learn/lv2/algorithm)
