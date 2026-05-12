# v0.12 C 接力 prompt — /learn 内容写作

放在 `docs/agent-hunt/` 方便下个会话 cat 给 Claude。

---

## 给下个会话的 prompt

继续 agent-hunt v0.12 epic（[#32](https://github.com/LLM-X-Factorer/agent-hunt/issues/32)）下的 [#39 C](https://github.com/LLM-X-Factorer/agent-hunt/issues/39)：写 /learn 课本剩余文章。骨架（#38 B3）已上线，markdown + frontmatter 渲染链路全通。

**已完成（commit `d9ea15b` on main）**：
- B3 #38 close：`/learn` 三层课本骨架（marked + gray-matter，5 个 SSG 路由）
- Lv1 入门 5/5 全部完成 — 总阅读 ~32 min
- Lv2 职业百科 1/16（教师）
- Lv3 转岗路径 1/6-8（教师→AI Education）

**剩余目标**：~20 篇总数，现在 7 篇 → 还差 13 篇左右。

---

## 写作流程

每篇大约 ~10-15 min 写 + ~5 min build/部署。建议每个 session 写 **3-5 篇** 一批 commit + 部署。

### 开会话第一件事（5 分钟 prep）

```bash
cd /Users/liu/Projects/agent-hunt
cat docs/agent-hunt/v012-c-handoff.md          # 这份
ls content/learn/lv2/ content/learn/lv3/        # 看已写的
cat content/learn/lv1/01-what-is-job-market.md  # 看风格参考
cat content/learn/lv2/01-teacher.md             # Lv2 范式
cat content/learn/lv3/01-teacher-to-ai-education.md  # Lv3 范式（最难的，可以照着写）
```

### 数据引用源

写每篇要引用真实数据时拉这几个文件（避免编数字）：

| 用途 | 文件 |
|---|---|
| 跨市场 ratio / 论断核心数字 | `frontend/public/data/narrative-stats.json` |
| 27 角色画像（salary / sample_titles / required_skills / industries / companies） | `frontend/public/data/role-profiles.json` |
| 8 传统职业 AI 增强样本 + pivot targets | `frontend/public/data/profession-profiles.json` |
| 行业分布 | `frontend/public/data/industry-salary.json` |

引用例子：「教师转 AI 教育的 sample 量 45 条，48% 走 education_ai 簇」← 来自 `profession-profiles.json` → teacher entry。**不要拍脑袋写数字**。

### 写作标准（每篇都遵守）

1. **6 岁能懂**：每篇至少 1 个生活类比（菜市场 / 蛋糕 / 拖拉机替马 是已有的，别重复）+ 1 个具体场景 + 避免行业黑话
2. **800-1500 字**：太短不够干货，太长 6 岁看不下去
3. **frontmatter 必填**：title / order / summary / reading_minutes / linked_roles（如有）/ linked_professions（如有）
4. **结尾「下一步」section**：链回 /roles 或 /professions 或下一篇 Lv2/Lv3
5. **真实数据引用**：用 agent-hunt 数据，标 sample 量。例：「34 条 AI 销售岗位里，53% 标了 BD/商务」不是「大部分」
6. **每篇配 1-2 段 reality check**：哪些人不该转 / 不该投 — 不要只写「welcoming」，业务方反复强调「诚实劝退价值更大」

### Frontmatter 模板

```yaml
---
title: <职业> — 这职业到底是干啥的（Lv2）
title: <传统职业> → <AI 角色> (具体怎么转)（Lv3）
order: <1-N>
summary: <80-120 字总结>
reading_minutes: <5-8>
linked_roles:
  - { market: domestic, role_id: <id> }
  - { market: international, role_id: <id> }
linked_professions:
  - <profession_id>
---
```

---

## 待写清单（按 ROI 排序）

### 第一批（最热门，先写）— Lv2 AI 岗 4 篇

照着 `lv2/01-teacher.md` 的 6-section 结构（这职业做什么 / 三套硬核能力 / 真实数据 / 怎么开始 / 不适合谁 / 下一步）：

- [ ] `lv2/02-ai-engineer.md` — AI/LLM 工程师（国内 734 岗位最热，详见 [/roles/domestic/ai_engineer](https://agent-hunt.pages.dev/roles/domestic/ai_engineer)）
- [ ] `lv2/03-algorithm.md` — 算法工程师（国内 328 岗位）
- [ ] `lv2/04-product-manager.md` — AI 产品经理（国内 439 岗位）
- [ ] `lv2/05-ml-scientist.md` — ML Scientist / Researcher（海外 817 岗位）

### 第二批 — Lv2 传统职业 7 篇

照着教师范式，对应 `/professions` 8 个职业里的另外 7 个：

- [ ] `lv2/06-electrical.md` — 电气工程师（sample 6，弱数据，重点写转型路径）
- [ ] `lv2/07-mechanical.md` — 机械工程师（28 条，可写丰富）
- [ ] `lv2/08-civil.md` — 土木工程师（sample 1，重点写"为什么慢 + BIM 入口"）
- [ ] `lv2/09-chemical.md` — 化工工程师（sample 0，重点写"AI for Science 入口 + 头部公司清单"）
- [ ] `lv2/10-accountant.md` — 会计（18 条）
- [ ] `lv2/11-finance.md` — 金融分析师（68 条，量化路径是亮点）
- [ ] `lv2/12-sales.md` — 销售（100 条，最大样本）

### 第三批 — Lv2 AI 岗补 4 篇（如果业务方反馈需要）

- [ ] `lv2/13-data-scientist.md` — 数据分析 / 数据科学
- [ ] `lv2/14-applied-scientist.md` — Applied Scientist（海外热门）
- [ ] `lv2/15-sales-bd.md` — AI 销售 / AI 解决方案 BD（细分版）
- [ ] `lv2/16-prompt-engineer.md` — Prompt 工程师 / AI 训练师

### 第四批 — Lv3 转岗路径 5-7 篇

照着 `lv3/01-teacher-to-ai-education.md` 的 12 周路径结构（第 1-4 周 / 5-8 周 / 9-12 周 + 不要犯的 3 个错 + 12 周后你应该长什么样）。**Lv3 是 Lv2 的延伸 — 每条转岗对应 Lv2 里某个传统职业 + 目标 AI 角色**：

- [ ] `lv3/02-electrical-to-physical-ai.md` — 电气 → 具身智能 / 自动驾驶机械
- [ ] `lv3/03-mechanical-to-robotics.md` — 机械 → 机器人 / 自动驾驶
- [ ] `lv3/04-accountant-to-ai-finance.md` — 会计 → AI Finance / Audit AI
- [ ] `lv3/05-finance-to-quant.md` — 金融分析师 → 量化研究员（亮点路径，国内顶薪）
- [ ] `lv3/06-sales-to-ai-sales.md` — 销售 → AI 销售 / AI ToB BD
- [ ] `lv3/07-engineer-to-ai-engineer.md` — 软件工程师 → AI Agent 工程师（通用转岗模板）

### 第五批 — Lv1 是否再扩

Lv1 issue spec 写 4-5 篇，目前已 5 篇，**默认不再扩**。如果业务方有新概念要科普（例如「什么是行业 / 什么是职业 vs 角色」），临时加。

---

## 部署节奏

### 每批 commit 前

```bash
cd /Users/liu/Projects/agent-hunt/frontend && npm run build 2>&1 | tail -20
```

build 通过后看输出确认新文件都被 SSG（应该出现新 `/learn/lv2/<slug>` 路径）。

### 部署 + 验证

```bash
cd /Users/liu/Projects/agent-hunt/frontend && npx wrangler pages deploy out --project-name agent-hunt --commit-dirty=true
# 等 ~30 秒，跑：
for slug in <new-slugs>; do
  curl -sL -o /dev/null -w "%{http_code} /learn/lv2/$slug\n" "https://agent-hunt.pages.dev/learn/lv2/$slug"
done
```

### Commit message 模板

```
content: lv2 add 4 AI 岗 articles (#39)

- 02-ai-engineer (国内 734 岗位最热, narrative 引用 sample_titles)
- 03-algorithm
- 04-product-manager
- 05-ml-scientist (海外 ML 研究路径)

#39 progress: 5/20 → 9/20
```

### 关 issue

**写到 20 篇全齐 + 业务方读过反馈 OK 之后**再 close #39。中间不需要 close，update comment 就好。

---

## 注意事项

### 写作易犯的错

1. **太抽象**：「AI 改变了销售」← 6 岁看不懂。要写「OpenAI 招了一个 Account Executive 月薪 30 万 — 他卖的是 ChatGPT API 给企业」。
2. **数字编造**：必须从 `frontend/public/data/*.json` 拉真实数据，不能拍脑袋说「大部分 / 一半左右」。
3. **没有 reality check**：不要只写「welcoming + 可以转」，每篇至少 1 段「谁不该转 / 这条路有什么坑」。
4. **链接错 ID**：检查 `linked_roles` 的 `role_id` 是否存在于 `role-profiles.json`（27 个有效 ID 在那里）。
5. **重复类比**：菜市场 / 蛋糕 / 拖拉机替马 / 钉马蹄铁 已经用了。Lv2/Lv3 用新的（厨师 / 司机 / 工匠 / 木匠 等都 OK）。

### 不要做的

- 不要碰 `frontend/src/app/learn/` 的路由代码（已上线工作正常）
- 不要改 `frontend/src/lib/learn.ts`（除非加新 frontmatter 字段）
- 不要写 .md 之外的文件（不需要图 / 不需要 components）
- 不要 collect 新数据（#34 阻塞，不在这个 session 范围）

### 长度参考

| 类型 | 字数 | reading_minutes |
|---|---|---|
| Lv1 | 1000-1500 字 | 5-8 |
| Lv2 | 800-1300 字 | 4-7 |
| Lv3 | 1500-2500 字（含 12 周路径细节） | 8-12 |

---

## 验证（开会话前）

- [ ] `cat docs/agent-hunt/v012-c-handoff.md` 拉一遍上下文（这份）
- [ ] `git log --oneline -5` 确认 `d9ea15b` 在 main
- [ ] `cat content/learn/lv2/01-teacher.md` 看 Lv2 范式
- [ ] `cat content/learn/lv3/01-teacher-to-ai-education.md` 看 Lv3 范式
- [ ] `ls content/learn/{lv2,lv3}/` 确认已写哪些
- [ ] 跟用户确认这次写哪几篇（建议按上面 5 批的顺序）
- [ ] `cat frontend/public/data/narrative-stats.json` / `role-profiles.json` 拉真实数字
