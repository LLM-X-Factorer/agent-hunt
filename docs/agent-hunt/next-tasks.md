# Agent Hunt — 跨会话任务清单

> 最近更新：2026-04-30（v0.9 叙事手册 + currency fix 已上线）
> 本文档供新会话 onboarding 使用。每个任务包含「启动 prompt」（可直接复制粘贴给 Claude）+ 上下文 + ROI 评估。

## 全局上下文（每个新会话都需要的）

agent-hunt 是 AI 职业市场全景分析平台 = **数据生产端**。下游 [aijobfit](https://github.com/LLM-X-Factorer/aijobfit) 远程 fetch agent-hunt.pages.dev/data/*.json 做求职诊断 dashboard。本仓库不实现诊断功能。

agent-hunt 网站本身（agent-hunt.pages.dev）= 内部叙事手册（业务人员讲解市场用，5 条论断 + 真实 JD 例子）+ 数据自检工具。**不是面向陌生用户的产品，不投产品打磨**。

### 关键技术决策（不要再 debate）
- **LLM**：OpenRouter 走 `deepseek/deepseek-v3.2-exp`（最快+质量 OK），用 `AH_LLM_MODEL` 配置。不要换 z-ai/glm-5.1（10× 慢 + 贵）/ google/gemini-2.5-flash（OpenRouter 上 ToS 全失败）
- **薪资聚合**：必须用 `Job.salary_mid_cny_monthly` 属性，不要直接 `(salary_min + salary_max) // 2`。直接裸算会让海外 USD/年 被误读为 CNY/月，跨市场 ratio 夸大 1.7×。属性会自动调 `app/services/currency.py` 做汇率换算
- **长任务**：`run_in_background=true` + `ScheduleWakeup` 间歇 check；asyncio 任务必须 `asyncio.wait_for(..., timeout=45)` 防 inflight 卡死；LLM client 60s SDK timeout + max_retries=1
- **新 collector**：写在 `backend/scripts/collect_*.py`，复用 `import_jobs()` 入 `jobs` 表；`source` 字段标记 `platform | vendor_official | community_open`
- **衍生 JSON**：写在 `frontend/public/data/`，aijobfit 远程 fetch 消费
- **LLM 解析失败率高时**：长字段（level / focus_tag）至少 80 字符宽度
- **命令必须 `cd /Users/liu/Projects/agent-hunt/backend`** 才能跑 `.venv/bin/python`

### 参考代码模式
- ATS 通用适配器：`backend/scripts/collect_vendor_ats.py`（Greenhouse + Ashby）
- HN 类公开 API：`backend/scripts/collect_hn_wih.py`（Algolia API）
- SSR HTML 抓取：`backend/scripts/collect_nowcoder_posts.py`（`__INITIAL_STATE__` regex）
- LLM 批量解析：`backend/scripts/backfill_quality_labels.py`（`asyncio.wait_for` 模式）
- Salary 抓取（含 location→market 检测、bool 防御）：`backend/scripts/collect_levels_fyi.py`
- 城市 tier 分类：`backend/app/services/cities.py`
- 汇率换算：`backend/app/services/currency.py` + `Job.salary_mid_cny_monthly` 属性

### Git 约定
- 提交只 add 本任务相关文件，**不要** add `CLAUDE.md` / `docs/employee-resume/` / `.claude/` / `backend/scripts/probe_*.py`
- commit message 英文，引用 `(#X)` 或 v 标签，1-2 句说原因
- 主分支 main，可以直接 push

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
| 脉脉工资 (maimai.cn) | 难 | 反爬重 + 强登录 |
| 一亩三分地 (1point3acres.com) | 浅 | 全站 CF 挑战（Playwright 8s 可过），但 fid=237 工资板积分门槛 200 / fid=145 海外面经板门槛 188，匿名只能拿到标题+公司名+~30 字预览，school/comp/offer_status 全锁 |

---

## 待办任务清单（按 ROI 排序）

### 🟡 观察期 — 等 aijobfit 业务反馈

aijobfit 端 8 项改造（4 P0 + 4 P1/P2）正在做（业务方反馈 6 条核心问题：推荐脱离行业 / 报告章节没切片 / 预期薪资达成概率 / 流程倒置 / 城市差异 / 数据过时）。

agent-hunt 这边等业务方实际跑过 4 个验收 case 后再决定是否补数据：
- 「电气工程师 + 教育行业」不应推 AI 销售
- 「教育 + 产品经理」市场全景应只展示教育行业 PM 数据
- 填预期 35k 应该看到「约 X% 岗位能开到」
- JD 总数应显示 8000+ 不是 2370

**可能反向需要的数据**（等触发再做）：
- 行业 × 角色 × 城市 4D 切片（如果业务方说「医疗 + AI 增强 + 上海薪资」要单独看）
- 海外 vendor 国内办公室分布（如果说「OpenAI 在中国招吗」）

---

### 🟢 P1 — OpenRouter 余额恢复后

剩 1999 条 GitHub hiring JD 卡在 LLM 余额耗尽（HTTP 402）。充值后跑：
```bash
cd backend
.venv/bin/python scripts/parse_pending.py  # 或 POST /jobs/parse/batch
```
跑完后 labeled_jobs 从 5673 涨到 ~7600，narrative 数字会更扎实。

同时可以让 `generate_insights.py` + `generate_report.py` 切回 LLM 自动生成（v0.9 是手写）。每次 5 美金，不算贵。

**启动 prompt**：
> agent-hunt 项目，OpenRouter 余额已充值。先跑 `POST /jobs/parse/batch` 把 1999 条 GitHub hiring 解析掉（参考 `backfill_quality_labels.py` 的 asyncio.wait_for 模式，避免 inflight 卡死）。完成后跑 `generate_insights.py` + `generate_report.py` + `export_narrative_stats.py`，然后 build + deploy。

---

### 🟢 P2 — 国内 7 家大厂 LLM 厂商

**ROI**：⭐⭐ — 重活，每家单独写 Playwright

剩 7 家：字节 / 阿里 / 腾讯 / 百度 / 商汤 / 阶跃 / 零一万物。这些大厂多用自建招聘系统，反爬重，需要 Playwright。

**前置**：先确认业务有需求（学员问起这些厂在不在数据里）才做。

**入表**：`jobs` 表，`source="vendor_official"`，`platform_id="vendor_<slug>"`

**启动 prompt**：
> agent-hunt 项目，做 issue #12 后续 — 国内 7 家大厂 LLM 厂商招聘（字节 / 阿里 / 腾讯 / 百度 / 商汤 / 阶跃 / 零一万物）。每家先单独 spike 招聘系统，能用 Greenhouse / Ashby / Lever 复用 `collect_vendor_ats.py`，自建系统单独写 Playwright。参考 `backend/app/collectors/boss_zhipin.py`。建议先做轻的 4 家（智谱风格的创业公司）再决定大厂是否做。

---

### 🟢 P2 — 数据更新自动化

当前流程：手动 export → build → wrangler deploy。如果要做日更：
- GitHub Actions 定时 job 触发后端 export → commit JSON → trigger Cloudflare Pages rebuild
- 或者把 export 跑在 Celery worker 上（已经有 beat 跑月度快照）

**前置**：先看实际更新频率需求。两周一次手动可以接受就不做。

---

### 🟢 P2 — 维护性任务

- **skill_aliases.json 扩展**：定期跑 `GET /skills/unmatched` 看哪些原始技能没被映射，补充
- **Chrome 扩展完善**：`extension/` 目录下的 4 平台内容脚本，按需更新
- **Celery 定时采集**：`app/tasks/celery_app.py` 已配 beat（每月 1 号 03:00 UTC 跑 `run_monthly_snapshot`），缺一个 worker daemonize 流程

---

## 已完成（最近）

### v0.9（2026-04-30）
- **P0 叙事手册** —— 双轨入口首页 + `/narrative` 6 页（目录 + p1-p5）+ 通用 narrative-layout 组件 + 业务视角的方法论 / 机制 / 反例三个 box（commits 80a9c5e → c0f40d2 → 8acfad6 → 45e9d08 → 2b5140a → 9adb07b → c51cac4）
- **P0 currency normalization 防呆** —— `app/services/currency.py` + `Job.salary_mid_cny_monthly` 属性。修复 cross_market service + 7 个 export 脚本里 17 个调用点的汇率 bug
- **新数据切片** —— industry-augmented-salary / vendor-title-breakdown / narrative-stats / narrative-examples / roles-by-city
- **`export_api_snapshots.py`** —— 替代手工 curl，12 个 API-mirror JSON 从 v0.6 数据更新到当下
- **insights.json / report.json 由 Claude 手写** —— 节省 OpenRouter 5 美金，与新数字口径一致

### v0.8（2026-04-29）
- **#9/#10/#11** 行业 × 岗位 2D + augmented_by_profession + graduate_friendly（commit 9884f47）
- **#12 部分**（commit b5f0453 + d6b9a5e）OpenAI / Anthropic / xAI / Cohere / DeepMind 共 1532 条 vendor_official
- **#12 后续** 国内 4 家创业公司 — 智谱 + Moonshot（Moka HR） + MiniMax + 百川（飞书招聘）共 533 条（commits e85d305 + bd5ec98）
- **#13** 月度快照定时任务 — Celery beat 配置（每月 1 号 03:00 UTC）
- **#14 部分** nowcoder applicant profiles（commit 28f70f5）— 718 条
- **#14 1point3acres spike** — 归入「不可达」清单（CF 可过但门槛高）
- **#15** levels.fyi CN 大厂扩展（commit 3fd5bfe）— 1392 salary reports
- **#16** ghost listing 信号（commit 1566293）
- **#17** GitHub hiring repos collector（commit b5ec7a2）— SimplifyJobs/New-Grad-Positions + Summer2026-Internships + vanshb03/Summer2025-Internships，AI 相关 2089 条
- **2026-04-29 战略调研** — dbs-deconstruct 拆 agent-hunt 网站定位；CF Analytics 调研确认它是内部工具（业务人员/招生）+ 数据自检
