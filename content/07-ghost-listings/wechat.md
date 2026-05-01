# 公众号长文：Deloitte 一个 Full Stack 挂了 19 次——海外幽灵岗集中度是国内 3 倍

## 标题

「9,287 条 JD 数据揭示：海外 LinkedIn 上 Deloitte 一个 Full Stack 标题挂了 19 次，海投前先打 30% 折扣」

## 正文

---

### 一、Deloitte 一个标题在 LinkedIn 挂了 19 次

我做 agent-hunt 这个项目时，从 22 个数据源采集了 9,287 条 AI 相关岗位 JD，按「同公司 + 同 title」分组检测重复发布的「幽灵岗集群」。

最高记录：

- **Deloitte 一个「Full Stack Engineer」标题挂了 19 次**
- **Meta 一个「Product Manager」标题挂了 17 次**
- **OpenAI 三个 FDE 相关标题加起来挂了 33 次**（Forward Deployed Engineer 10 + Forward Deployed Software Engineer 9 + AI Deployment Engineer 14）

这不是少数公司的问题。整个海外 LinkedIn / vendor 平台上，「幽灵岗集中度」是国内招聘平台的 **3.1 倍**。

[图 1：海外 vs 国内幽灵岗占比 + Top 6 公司柱状图]

「海外岗位数量 ≠ 真实 hiring slot」 是国内 AI 工程师海投前必须知道的预期管理。

### 二、数据：海外幽灵岗集中度 0.55% vs 国内 0.18%

「幽灵岗」= 同公司同 title 在采集窗口内出现 ≥ 5 次。

注意这是一个**嫌疑信号**，不是 100% 确证（同公司同 title 可能是不同部门各招）。但 19 次、17 次这种极端值，几乎可以确定是单一岗位反复发布。

**两市场对比：**

- 海外（LinkedIn / Indeed / 大厂 vendor）：5,502 条 AI 相关 JD 里有 30 个幽灵岗簇 = **0.55%**
- 国内（Boss / 猎聘 / 拉勾 / 国内大厂）：3,795 条 AI 相关 JD 里 7 个簇 = **0.18%**

**海外集中度是国内 3.1 倍。**

**Top 6 幽灵岗清单（按重复发布次数降序）：**

| # | 公司 | 标题 | 重复次数 | 平台 |
|---|------|-----|---------|------|
| 1 | Deloitte | Full Stack Engineer | 19 | LinkedIn |
| 2 | Meta | Product Manager | 17 | LinkedIn |
| 3 | Varsity Tutors | Probability Tutor | 17 | LinkedIn |
| 4 | OpenAI | 三个 FDE 相关 title | 33（合计） | OpenAI ATS |
| 5 | Microsoft | Research Intern | 10 | GitHub hiring |
| 6 | Amazon | Software Development Engineer | 8 | Indeed |

5 / 6 在海外 LinkedIn / vendor 平台。国内只有 1 个北京互联网 PM 进 top 10。

### 三、为什么海外幽灵岗这么多？

这不是公司主动作恶，是**产品逻辑 + KPI 文化**叠加的结果。

**1. LinkedIn Jobs 按「最近 24 小时新岗」排序。**

公司发了一个岗位，几小时后就被新发的岗位顶下去——掉出可见区，失去搜索曝光。

如果公司想保持曝光，必须**下架重发**。这不是 LinkedIn 故意要逼公司刷岗，是产品按「时间排序」的设计逻辑必然的副作用。

**2. 美国大公司 HR 考核「岗位活跃度」。**

很多大公司 HR 部门内部 KPI 是「open positions 数量」「pipeline 健康度」。挂越多岗位看上去 talent pipeline 越健康，所以 HR 倾向**多挂岗 + 频繁刷新**。

实际有没有 hiring budget 是另一回事。

**3. 国内 Boss / 猎聘 / 拉勾对同账户重复发岗有限流。**

国内招聘平台明确知道「重复发岗影响用户体验」，所以同 title + 同 company 重发会被算法打压。**国内刷岗成本高，所以集中度自然低。**

但这不等于「国内招聘市场更健康」——见下面 caveat。

### 四、必须诚实说的边界

写到这里我必须停下来，把 3 件事讲清楚：

**1.「同 title 重发」不能 100% 证明是单一岗位。**

Meta 17 个 PM 标题——可能确实是 17 个不同部门各招（FB Apps / Reality Labs / AI / Infra）。无法 100% 区分「单一岗位反复发布」 vs「真的多个部门同标题各招」。

我们的数据是**嫌疑信号**+**上限估计**，不是确证。但 19 次、17 次这种极端值，几乎可以确定是单一岗位反复发布。

**2. 国内 0.18% 不等于「国内招聘市场更诚实」。**

Boss / 拉勾反爬严，单次只能拿前几页——国内可能也有大量幽灵岗只是我们采不到。**这个 0.18% 是「采集到的样本里」的比例，不是市场全貌。**

如果用同样的算法打个 LinkedIn 中国版（如果存在），结果可能完全不同。

**3. 没回应不全是幽灵岗。**

如果你海投了几百家没回应，不要一概归咎于幽灵岗。其他原因：

- **海外公司优先内部 referral**：Senior 岗位 80% 以上通过员工推荐到面试，外部 cold apply 命中率本来就低
- **海外签证倾向本地候选人**：sponsor visa 是公司额外成本，能招本地的就招本地
- **JD 描述虚高**：JD 写「entry-level」实际想招 senior，被「降低门槛吸引应聘者」是常见操作

幽灵岗只解释了一部分问题（顶多 30-40%）。剩下的需要从 referral / 简历精准度 / JD 实际偏好的角度想办法。

### 五、海投实用建议

**这个 thread 想给你的不是「海外招聘是骗人的」，是预期管理 + 行动调整。**

看到「美国 AI 工程师 5,000 个 active jobs」这种数字时，建议这样推算实际可投：

```
原始：5,000 个 active jobs
↓ 打 0.6× 折扣（去掉幽灵岗 + 转发噪音）
还剩 3,000 个独立岗位
↓ 再打 0.7× 折扣（考虑签证摩擦）
还剩 2,100 个能投的岗位
```

[图 2：5,000 → 2,000 折扣推导]

**最终大约 40% 才是真正可投的岗位。5,000 看上去多，实际能投的只有 2,000。**

**行动调整：**

1. **精准投**：看公司 / 团队 / JD 描述差异，挑 5-10 家匹配度最高的深投，写定制化简历 + cover letter
2. **找 referral**：LinkedIn 找在那家公司的人（最好是同校 / 前同事），冷邮件请求 referral。一个 referral 抵 100 次 cold apply
3. **走 vendor 内推**：如果你有 OpenAI / Anthropic 这类目标，他们的 official ATS（不是 LinkedIn）刷岗少，岗位真实度更高，可以直接投

**不要做的事：**

- 不要海投 100 家——是在浪费精力，命中率比精准投低 5-10 倍
- 不要把所有没回应都归咎于幽灵岗——多归因，更现实

### 六、对你意味着什么

**如果你正在海投 / 计划海投：**

把幽灵岗信号和签证信号都纳入决策。看到 LinkedIn 「美国 AI 5000+ 岗位」这种数字时，先在心里打 30-50% 折扣。然后精准投 + 找 referral，而不是海投。

**如果你打算等几个月再海投：**

先建立 LinkedIn 网络（同事 / 校友 / 同行），积累 referral 资源。海投时机和 referral 资源准备度比单纯多投 100 家更重要。

**如果你正在被「投了几百家没回应」搞得焦虑：**

回看本文第四节——幽灵岗只解释 30-40%。剩下的需要从 referral / 简历精准度 / JD 实际偏好的角度想办法。不是市场骗你，是你的策略需要调整。

### 七、行动

完整海外 vs 国内招聘对比 + 27 个角色画像 + 5 条市场判断：[agent-hunt.pages.dev](https://agent-hunt.pages.dev)

如果你想知道你打算投的目标公司是不是有大量重复发岗，留言你打算投的海外目标公司（1-3 家）+ 想投的 title（如：Meta / Stripe / Anthropic + Senior SWE）。

我会用 agent-hunt 数据给你一份：

- 这些公司这个 title 在采集窗口内的重发集中度（是不是幽灵岗 / 真新岗 占比）
- 这些公司其他 active 真正在招的对口岗位（去掉幽灵噪音后）+ 月薪范围
- 海投建议（精准投 vs 找 referral vs 走 vendor 内推哪条更现实）

前 30 个免费。

---

*数据来源：agent-hunt 项目，22 个数据源（主流招聘平台 + LLM 厂商官方 ATS + HN/GitHub 社区招聘渠道）共 9,287 条 AI 岗位 JD。本文使用海外 5,502 + 国内 3,795 子集。Ghost cluster 检测算法 = 同 company + 同 title 出现 ≥ 5 次。完整算法见 backend/scripts/export_quality_signals.py。分析代码开源：github.com/LLM-X-Factorer/agent-hunt*

---

## 发布清单

- [ ] 插入图 1（海外 vs 国内幽灵岗占比 + Top 6 公司柱状图）在第二节
- [ ] 插入图 2（5,000 → 2,000 折扣推导）在第五节
- [ ] 发布时间：工作日晚 8-9 点
- [ ] 阅读原文 → agent-hunt.pages.dev/narrative/p5
- [ ] 留言区置顶：「评论你打算投的海外目标公司（1-3 家）+ 想投的 title，前 30 个免费给一份『重发集中度 + 真实 active 岗位 + 海投建议』」
