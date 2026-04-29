# Agent Hunt — 跨会话任务清单

> 最近更新：2026-04-29（#17 GitHub hiring repos collector 已上线）
> 本文档供新会话 onboarding 使用。每个任务包含「启动 prompt」（可直接复制粘贴给 Claude）+ 上下文 + ROI 评估。

## 全局上下文（每个新会话都需要的）

agent-hunt 是 AI 职业市场全景分析平台 = **数据生产端**。下游 [aijobfit](https://github.com/LLM-X-Factorer/aijobfit) 远程 fetch agent-hunt.pages.dev/data/*.json 做求职诊断 dashboard。本仓库不实现诊断功能。

### 关键技术决策（不要再 debate）
- **LLM**：OpenRouter 走 `deepseek/deepseek-v3.2-exp`（最快+质量 OK），用 `AH_LLM_MODEL` 配置。不要换 z-ai/glm-5.1（10× 慢）/ google/gemini-2.5-flash（OpenRouter 上 ToS 全失败）
- **长任务**：`run_in_background=true` + `ScheduleWakeup` 间歇 check；asyncio 任务必须 `asyncio.wait_for(..., timeout=45)` 防 inflight 卡死；LLM client 60s SDK timeout + max_retries=1
- **新 collector**：写在 `backend/scripts/collect_*.py`，复用 `import_jobs()` 入 `jobs` 表；`source` 字段标记 `platform | vendor_official | community_open`
- **衍生 JSON**：写在 `frontend/public/data/`，aijobfit 远程 fetch 消费
- **LLM 解析失败率高时**：长字段 (level / focus_tag) 至少 80 字符宽度
- **命令必须 `cd /Users/liu/Projects/agent-hunt/backend`** 才能跑 `.venv/bin/python`

### 参考代码模式
- ATS 通用适配器：`backend/scripts/collect_vendor_ats.py`（Greenhouse + Ashby）
- HN 类公开 API：`backend/scripts/collect_hn_wih.py`（Algolia API）
- SSR HTML 抓取：`backend/scripts/collect_nowcoder_posts.py`（`__INITIAL_STATE__` regex）
- LLM 批量解析：`backend/scripts/backfill_quality_labels.py`（`asyncio.wait_for` 模式）
- Salary 抓取（含 location→market 检测、bool 防御）：`backend/scripts/collect_levels_fyi.py`

### Git 约定
- 提交只 add 本任务相关文件，**不要** add `CLAUDE.md` / `docs/employee-resume/` / `.claude/` / `backend/scripts/probe_*.py`
- commit message 英文，引用 `(#X)`，1-2 句说原因
- 主分支 main，可以直接 push（已有多 commit ahead 的历史，正常）

### 工作流
1. 探查数据源（API / HTML / SSR / SPA）
2. 写 collector，先小批量（10-20）测试
3. 跑全量（后台 + ScheduleWakeup）
4. 跑相关 export 脚本刷新衍生 JSON
5. commit + push + 更新 issue 评论
6. 给我做总结

### 已确认不可达数据源（不要重复尝试）
| 数据源 | 状态 | 原因 |
|---|---|---|
| 看准爆料板 (kanzhun.com) | 死 | 平台已下线（`renderStatus: fail` / `offline: true`），firm/wage 强制跳 Boss 登录 |
| OfferShow 公开 API | 浅 | `search_salary_list` 只返回清单元数据，逐条字段在 VIP + PDF 后面 |
| 脉脉工资 (maimai.cn) | 难 | 反爬重 + 强登录，issue #15 也标「放后期」 |
| 一亩三分地 (1point3acres.com) | 浅 | 全站 CF 挑战（Playwright 8s 可过），但 fid=237 工资板积分门槛 200 / fid=145 海外面经板门槛 188，匿名只能拿到标题+公司名+~30 字预览，school/comp/offer_status 全锁。元数据不足以入 applicant_profiles 表 |

---

## 待办任务清单（按 ROI 排序）

### 🔥 P0 — 叙事手册（业务人员/招生用）

**背景**：经过 dbs-deconstruct 拆解 + Cloudflare Analytics 调研后，确认 agent-hunt 网站 = 内部工具（数据自检）+ 内部叙事手册（给就业班 3-5 个业务人员讲解市场用）。**不是面向陌生用户的产品，不投产品打磨**。但 50 个学员已报名，业务人员当前用「刘人肉传话」了解市场——必须把刘脑里的判断固化到网站上。

**架构（双轨并行）**：
```
新首页 / (重写 src/app/page.tsx)
   ↓
   ├──► 📖 叙事手册（/narrative）        ← 新增 6 页
   │       └── /narrative 目录页
   │       └── /narrative/p1 ~ /narrative/p5（每条论断 1 页）
   │
   └──► 📊 数据看板（现有 8 页保持不变）
            /skills /salary /gaps /industry /insights /report 等
```

**首页双轨入口卡片描述**：
```
📖 叙事手册                          📊 数据看板
基于 8634 条 JD 数据                 8 个交互式 dashboard
提炼出的 5 条市场判断                 技能图谱 / 薪资分析 / 行业分析
适用：业务人员讲解 / 招生展示          适用：深度查询 / 数据验证
→ 进入                                → 进入
```

**5 条论断（已挑选，每条都带数据 + 业务人员复述话术）**：

#### 论断 1 · 市场基本盘
> 「AI 招聘市场不是只有算法工程师。把 JD 拆开看，**国内传统行业（医疗/制造/汽车/金融/教育）的 AI 增强需求是互联网行业的 3.4 倍**。市面所有 AI 课程都在教程序员转 AI 程序员，没人教传统行业怎么用 AI——这是市场最大的认知错位。」

数据出处：
- 国内 AI 增强 jobs 939 / 国内 AI 原生 jobs 1372（`SELECT market, role_type, COUNT(*) FROM jobs WHERE parse_status='parsed' AND role_type IS NOT NULL GROUP BY 1, 2`）
- 国内传统行业 AI 增强：manufacturing 148 + automotive 108 + healthcare 87 + media 85 + finance 84 + education 59 + consulting 48 + retail 47 = 666
- 国内 internet 行业 AI 增强：197
- 比值：666 / 197 = 3.4×

#### 论断 2 · 反直觉（薪资）
> 「**互联网公司给『懂 AI 的非算法岗』开 25k；医疗/制造/金融开 30k；能源开 48k**。学员心里默认『互联网=高薪』，结果在 AI 增强方向反向走——传统行业反而能给 20% 溢价。」

数据出处：行业薪资中位数（CNY 月薪）
- energy 48k (n=6 小样本) / healthcare / manufacturing / finance 30k / telecom 27.5k / internet 25k / media 12.5k
- 查询：`SELECT industry, COUNT(*), PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (salary_min+salary_max)/2.0) FROM jobs WHERE parse_status='parsed' AND role_type='ai_augmented_traditional' AND market='domestic' AND salary_min IS NOT NULL GROUP BY 1 HAVING COUNT(*) >= 5 ORDER BY 3 DESC`

#### 论断 3 · 新岗位品类（最重的一条）
> 「OpenAI 和 Anthropic 工程师招聘里，**约 20% 是『Forward Deployed / Applied / Solutions / Implementation Engineer』——把 LLM 落地到客户业务的桥梁工程师**。OpenAI 一家就有 136 个这种岗位。国内课程市场对这个岗位**零覆盖**——不是教算法、也不是教产品，是技术+客户沟通+解决方案三合一。这是早期蓝海。」

数据出处：海外 vendor_official title 模式分析
- OpenAI: FDE 40 + Solutions 18 + Applied 6 + Deploy/Impl 48 + CS 24 = 136 / 652 = 20.9%
- Anthropic: 7 + 0 + 39 + 17 + 14 = 77 / 451 = 17.1%
- 合计：213 个客户端工程师岗位
- 查询：`SELECT platform_id, COUNT(*) FILTER(WHERE title ~* 'forward deployed') AS fde, COUNT(*) FILTER(WHERE title ~* '(solutions engineer|solution architect)') AS sol_eng, COUNT(*) FILTER(WHERE title ~* 'applied'), COUNT(*) FILTER(WHERE title ~* '(deployment|implementation|onboard)'), COUNT(*) FILTER(WHERE title ~* '(success|customer)') FROM jobs WHERE parse_status='parsed' AND platform_id LIKE 'vendor_%' GROUP BY 1`

#### 论断 4 · 跨市场套利
> 「学员要不要出海？看薪资差：**AI 原生海外是国内 4 倍，AI 增强海外是国内 4.6 倍**。出海做 AI 增强反而比出海做 AI 原生套利空间更大——传统行业 + AI + 海外是三重叠加。」

数据出处：cross-market 中位数（CNY 月薪）
- 国内 native 32.5k / 海外 native 128.6k → 3.96×
- 国内 augmented 23k / 海外 augmented 105.7k → 4.59×
- 查询：`SELECT market, role_type, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (salary_min+salary_max)/2.0) FROM jobs WHERE parse_status='parsed' AND role_type IS NOT NULL AND salary_min IS NOT NULL GROUP BY 1, 2`

#### 论断 5 · 预期管理
> 「学员看 LinkedIn 发现海外岗位多，建议先打 30% 折扣。**海外 AI 招聘里同公司同岗位重复发布是国内的 3 倍**——Deloitte 一个 Full Stack Engineer 标题挂了 19 次，Meta 同样的 PM 标题 17 次。岗位数量不等于实际 hiring slot。」

数据出处：ghost listing 集中度
- 海外 ghost clusters (variant_count >= 5) 29 / 4576 total = 0.6%
- 国内 ghost clusters 5 / 2435 total = 0.2%
- 比值：0.6 / 0.2 = 3×
- 现有 export：`frontend/public/data/jobs-quality-signals.json` 已含 `top_ghost_listings`（commit 1566293）

**每页结构（5 个 narrative 页通用模板）**：

```
首屏:
[60 字论断作为大标题]
[关键数字超大字号，如 "3.4×"]
[一句对比："国内传统行业 AI 增强需求 = 互联网的 3.4×"]

中段:
- 关键数据图（柱状/饼图，从 export JSON 读，复用现有 frontend/src/components/ 里的 chart）
- 支撑数据列表（如论断 1 的 12 个行业 jobs 排行）

底部:
📋 业务人员一句话：[复制按钮 → 60 字版本]
📊 数据来源：8634 jobs / 5672 已 labeled / [数据采集时间窗]
🔗 [深度查看（链接到对应数据看板页）]
```

**实施步骤**：
1. 改 `src/app/page.tsx` 为双轨入口（看现有 page 用什么 component lib）
2. 创建 `src/app/narrative/page.tsx`（5 论断目录 + 简短描述）
3. 创建 `src/app/narrative/p1/page.tsx` ~ `p5/page.tsx`（每页一个论断）
4. 复用现有 `frontend/src/components/InsightCard` / chart 组件（避免造轮子）
5. 数据已就绪：
   - 论断 1: `roles-augmented-by-profession.json` + `industry/*.json`
   - 论断 2: 需要 backend 跑一个 `export_industry_salary.py`（国内 augmented_traditional × industry × salary 中位数）。**这是新 export 脚本要写的**
   - 论断 3: 需要 backend 跑一个 `export_vendor_title_breakdown.py` 把 OpenAI/Anthropic 的 title 分类导出。**也是新脚本**
   - 论断 4: 已有 `roles-real-salary.json`（cross-market）+ market 字段
   - 论断 5: `jobs-quality-signals.json` 已含 `top_ghost_listings`
6. `npm run build` + `npx wrangler pages deploy out --project-name agent-hunt`

**新 export 脚本（论断 2 + 3 需要的，如果选择从 backend 导出而不是前端硬编码）**：
- `backend/scripts/export_industry_salary.py` — 国内 ai_augmented_traditional × 12 行业 × 薪资中位数 → `frontend/public/data/industry-augmented-salary.json`
- `backend/scripts/export_vendor_title_breakdown.py` — vendor_official × title pattern (FDE / applied / engineer / research) → `frontend/public/data/vendor-title-breakdown.json`

**启动 prompt（下次会话直接复制）**：
> 继续做 agent-hunt 项目（数据生产端，下游是 aijobfit）。
>
> 【当前任务】实施 P0 任务：叙事手册（双轨架构）。直接读 `docs/agent-hunt/next-tasks.md` 第一节"P0 — 叙事手册"，里面有完整的 5 条论断 + 数据出处 + 实施步骤 + 文件路径。
>
> 【关键背景】网站 = 内部叙事手册（给就业班业务人员），不是面向用户的产品。已确认双轨：新增 /narrative 5 页 + 现有 8 页保持不变。新首页做选择入口。
>
> 【新增 export 脚本】可能需要 export_industry_salary.py + export_vendor_title_breakdown.py（看选择前端硬编码 or 后端导出）。
>
> 【上下文】docs/agent-hunt/next-tasks.md 有完整工作流。LLM 走 OpenRouter（注意 max_tokens 必须显式传，commit 2983fcb 修复）。

---

### #12 后续 — 国内 11 家 LLM 厂商官网【P2】

**ROI**：⭐⭐ — 重活，每家单独写。智谱/Moonshot/百川/MiniMax 是 AI native 用户最关心的雇主

**目标**：抓 11 家国内 LLM 厂商的官方招聘页：智谱 / Moonshot / 百川 / MiniMax / 字节 / 阿里 / 腾讯 / 百度 / 商汤 / 阶跃星辰 / 零一万物。

**入表**：`jobs` 表，`source="vendor_official"`，`platform_id="vendor_<slug>"`（如 `vendor_zhipuai`、`vendor_moonshot`）

**实施策略**：
- 每家先单独 spike 一下用什么招聘系统
- 能用 Greenhouse / Ashby / Lever 就直接复用 `collect_vendor_ats.py`
- 自建系统的（多数）单独写 Playwright headless 脚本
- 字节/阿里/腾讯/百度有自家招聘官网（job.bytedance.com / talent.alibaba.com / careers.tencent.com / talent.baidu.com），数据量大但反爬重
- 智谱/Moonshot/百川/MiniMax/阶跃/零一万物等创业公司多用第三方 ATS，可能轻松

**启动 prompt**：
> 我们继续做 agent-hunt 项目（数据生产端，下游是 aijobfit 求职诊断）。
>
> 【当前 issue】要做 issue #12 后续 — 国内 11 家 LLM 厂商官网招聘（智谱 / Moonshot / 百川 / MiniMax / 字节 / 阿里 / 腾讯 / 百度 / 商汤 / 阶跃星辰 / 零一万物）。
>
> 【入表】jobs 表，`source="vendor_official"`，`platform_id="vendor_<slug>"`。海外 5 家（OpenAI / Anthropic / xAI / Cohere / DeepMind 共 1532 条）已通过 `collect_vendor_ats.py` 完成。
>
> 【实施策略】每家先单独探查招聘系统：
> - 能用 Greenhouse / Ashby / Lever 就复用 collect_vendor_ats.py（建议先把 4 家创业公司：智谱/Moonshot/百川/MiniMax 探完，可能有现成 ATS）
> - 自建系统的单独写 Playwright headless（4 家大厂 + 商汤等）
>
> 【参考】backend/scripts/collect_vendor_ats.py（Greenhouse + Ashby 通用适配）+ backend/app/collectors/boss_zhipin.py（Playwright 模式）。
>
> 【上下文】docs/agent-hunt/next-tasks.md 有完整工作流。建议先做 4 家创业公司（轻），再决定大厂是否要做（重）。

---

### #10 — AI 原生 vs AI 增强型岗位标签【P0】

**ROI**：⭐⭐⭐ — 不需要新数据源，重新跑 LLM 给现有 5980 条 JD 加标签

**目标**：在 `jobs` 表加 `role_type` 字段（`ai_native | ai_augmented | ai_adjacent`），让 aijobfit 能区分「纯 AI 工程师」和「会用 AI 的传统岗位」。

**实施**：
- 看 migration 005 已加 `role_type_and_graduate_fields`，schema 可能已有 — 先确认
- 如果 schema 已有，写一个 LLM 批量打标脚本（参考 `backfill_quality_labels.py`）
- prompt 设计：给 JD 全文，输出 `ai_native`（核心是 AI/ML 技术，如 算法工程师/AI 应用工程师）/`ai_augmented`（传统岗位 + 用 AI 工具，如 用 Copilot 的全栈工程师）/`ai_adjacent`（围绕 AI 但非技术，如 AI PM / AI 销售）

**启动 prompt**：
> 我们继续做 agent-hunt 项目（数据生产端，下游是 aijobfit 求职诊断）。
>
> 【当前 issue】要做 issue #10 P0 — AI 原生 vs AI 增强型岗位标签。给 5980 条 JD 加 `role_type` ∈ {ai_native, ai_augmented, ai_adjacent}。
>
> 【实施】
> 1. 先看 migration 005 的 `role_type_and_graduate_fields` schema 是否已就绪，没就绪先加 migration
> 2. 写 `backend/scripts/backfill_role_type.py`，参考 `backfill_quality_labels.py` 的 asyncio.wait_for 批量模式
> 3. prompt 设计：ai_native（核心 AI 技术）/ ai_augmented（传统岗位 + 用 AI 工具）/ ai_adjacent（围绕 AI 但非技术）
> 4. 跑完后跑 export_market_data.py 刷新衍生 JSON（可能需要给 export 加 role_type 维度）
>
> 【上下文】docs/agent-hunt/next-tasks.md 有完整约定。LLM 走 OpenRouter deepseek-v3.2-exp。

---

### #16 — 岗位真伪信号【P1】

**ROI**：⭐⭐ — 需要时间序列数据，依赖 #13 月度快照基础设施

**目标**：检测幽灵岗（同一 JD 反复发布、长期挂着不关）。

**实施**：
- 依赖 `snapshots` 表（migration 003 已有）
- 跑定时任务对比每月 jobs 状态：哪些 JD ID 重复出现 / 哪些挂超 N 个月没招到
- 输出 `quality-signals.json` 的 ghost_score 字段（已有 quality_signals 基础设施）

**启动 prompt**：
> 我们继续做 agent-hunt 项目（数据生产端，下游是 aijobfit 求职诊断）。
>
> 【当前 issue】要做 issue #16 P1 — 岗位真伪信号（幽灵岗预警）。
>
> 【实施】
> 1. 依赖 #13 月度快照，先确认 snapshots 表数据情况（可能还没积累足够）
> 2. 检测信号：同一 JD 反复发布（按公司+title 模糊匹配）/ 长期挂着不关（>3 月）
> 3. 输出 `quality-signals.json`（已有 export_quality_signals.py，看 ghost_score 字段是否需要新增）
>
> 【上下文】docs/agent-hunt/next-tasks.md 有完整约定。如果月度快照积累不够（<3 个月），先做 #13 的定时任务把雪球滚起来。

---

### #11 — 应届生 / 校招专项数据切片【P1】

**ROI**：⭐⭐⭐ — 已有 `export_graduate_friendly.py`，可能只需补几个数据维度

**启动 prompt**：
> 我们继续做 agent-hunt 项目（数据生产端，下游是 aijobfit 求职诊断）。
>
> 【当前 issue】要做 issue #11 P1 — 应届生/校招专项数据切片。
>
> 【现状】已有 `export_graduate_friendly.py`，先看输出 JSON 看 aijobfit 还缺什么。
>
> 【可能要做】
> - 应届/校招岗位识别（基于 JD 关键词 + experience 字段）
> - 与 nowcoder applicant_profiles 关联（同公司/同 role 的 offer 数 vs JD 数）
> - 学历门槛分布、城市分布、海投数/中签率
>
> 【上下文】docs/agent-hunt/next-tasks.md 有完整约定。

---

## 维护性任务（无 issue）

- **skill_aliases.json 扩展**：定期跑 `GET /skills/unmatched` 看哪些原始技能没被映射，补充
- **Chrome 扩展完善**：`extension/` 目录下的 4 平台内容脚本，按需更新
- **数据重新部署**：v0.8 数据未推到 agent-hunt.pages.dev。流程：
  ```bash
  cd backend && .venv/bin/python scripts/export_market_data.py
  .venv/bin/python scripts/export_real_salary.py
  # ... 其他 export
  cd ../frontend && npm run build && npx wrangler pages deploy out --project-name agent-hunt
  ```

---

## 已完成（最近）

- **2026-04-29 大会话** — 7 个 commit 推到 main，533 条 vendor_official 国内数据 + 5672/8238 jobs 已 LLM-labeled + ghost listing 信号 + graduate-friendly 加城市分布 + LLM max_tokens bug 修复 + Cloudflare Pages 重新部署。详见 commits `7a853ea bd5ec98 e85d305 1566293 f6ffa0e 06ca06d 2983fcb`
- **2026-04-29 战略调研** — 用 dbs-deconstruct 拆 agent-hunt 网站定位；CF Analytics 调研确认它不是面向用户产品；最终定位 = 内部叙事手册（业务人员/招生）+ 数据自检；已挑出 5 条核心论断（详见上面 P0 任务）
- **#12 后续** 国内 LLM 4 家创业公司 — 智谱 + Moonshot（Moka HR） + MiniMax + 百川（飞书招聘）共 533 条入库（commits e85d305 + bd5ec98）
- **#13** 月度快照定时任务 — `app/tasks/celery_app.py` + `app/tasks/snapshots.py` 配 Celery beat（每月 1 号 03:00 UTC 跑 `run_monthly_snapshot`），包装现有 `snapshot_monthly.py` + `export_trends.py`。部署任选 Celery（`celery -A app.tasks.celery_app worker --beat -l info`）或 system cron。当前 snapshot 表 242 skill / 43 role / 51 industry 行（覆盖 2026-03、2026-04 两月，新月会自动累加）
- **#14 1point3acres spike** — 全站 CF 挑战可过（Playwright 8s），但 fid=237 工资板积分门槛 200 / fid=145 海外面经板门槛 188，匿名拿不到 candidate 画像字段。归入「不可达」清单
- **#17 后续** GitHub hiring repos collector — `collect_github_hiring.py` 抓 SimplifyJobs/New-Grad-Positions + Summer2026-Internships + vanshb03/Summer2025-Internships 三个仓库 listings.json，AI 相关筛选后 2089 条入库（platform_id=community_github_hiring）。注意：**OpenRouter 信用余额耗尽（HTTP 402）**，仅 120/2119 LLM-parsed，剩 1999 条等充值后跑 `POST /jobs/parse/batch` 即可
- **#15** levels.fyi CN 大厂扩展（commit 3fd5bfe）— 1392 salary reports
- **#9 / 部分 #10 / 部分 #11** 行业 × 岗位 2D + 增强职业 + graduate-friendly（commit 9884f47）
- **#14 部分** nowcoder applicant profiles（commit 28f70f5）— 718 条
- **#15 部分** levels.fyi 海外 AI 公司 collector（commit d100ade）
- **#12 部分 / #17 部分** vendor ATS（OpenAI/Anthropic/xAI/Cohere/DeepMind 1532 条）+ HN WIH（1365 条）（commits b5f0453 + d6b9a5e）
