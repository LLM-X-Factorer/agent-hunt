# Agent Hunt — 跨会话任务清单

> 最近更新：2026-04-30（v0.10 Supabase + GitHub Actions 已上线）
> 本文档供新会话 onboarding 使用。每个任务包含「启动 prompt」（可直接复制粘贴给 Claude）+ 上下文 + ROI 评估。

## 全局上下文（每个新会话都需要的）

agent-hunt 是 AI 职业市场全景分析平台 = **数据生产端**。下游 [aijobfit](https://github.com/LLM-X-Factorer/aijobfit) 远程 fetch agent-hunt.pages.dev/data/*.json 做求职诊断 dashboard。本仓库不实现诊断功能。

agent-hunt 网站本身（agent-hunt.pages.dev）= 内部叙事手册（业务人员讲解市场用，5 条论断 + 真实 JD 例子）+ 数据自检工具。**不是面向陌生用户的产品，不投产品打磨**。

### 关键技术决策（不要再 debate）
- **数据库**：生产 = Supabase Postgres 17（ap-southeast-2），本地 dev = docker-compose 16。`AH_DATABASE_URL_OVERRIDE` 环境变量切换。详见 memory `architecture_supabase.md`
- **CI/CD**：GitHub Actions `weekly-refresh.yml`（cron 周日 02:00 UTC，仅 export+deploy）+ `collect-data.yml`（手动触发数据采集）。**不要在 weekly cron 里加 collect step** —— 跨 region 慢，会卡 timeout
- **LLM**：OpenRouter 走 `deepseek/deepseek-v3.2-exp`（最快+质量 OK），用 `AH_LLM_MODEL` 配置。不要换 z-ai/glm-5.1（10× 慢 + 贵）/ google/gemini-2.5-flash（OpenRouter 上 ToS 全失败）
- **薪资聚合**：必须用 `Job.salary_mid_cny_monthly` 属性，不要直接 `(salary_min + salary_max) // 2`。详见 memory `architecture_currency_normalization.md`
- **长任务**：`run_in_background=true` + `ScheduleWakeup` 间歇 check；asyncio 任务必须 `asyncio.wait_for(..., timeout=45)` 防 inflight 卡死；LLM client 60s SDK timeout + max_retries=1
- **新 collector**：写在 `backend/scripts/collect_*.py`，复用 `import_jobs()` 入 `jobs` 表；`source` 字段标记 `platform | vendor_official | community_open`
- **衍生 JSON**：写在 `frontend/public/data/`，aijobfit 远程 fetch 消费
- **LLM 解析失败率高时**：长字段（level / focus_tag）至少 80 字符宽度
- **命令必须 `cd /Users/liu/Projects/agent-hunt/backend`** 才能跑 `.venv/bin/python`

### 参考代码模式
- ATS 通用适配器：`backend/scripts/collect_vendor_ats.py`（Greenhouse + Ashby）
- 公开 JSON API（无反爬）：`backend/scripts/collect_vendor_tencent.py`（`careers.tencent.com`）+ `backend/scripts/collect_hn_wih.py`（Algolia API）
- SSR HTML 抓取：`backend/scripts/collect_nowcoder_posts.py`（`__INITIAL_STATE__` regex）
- LLM 批量解析：`backend/scripts/backfill_quality_labels.py`（`asyncio.wait_for` 模式）
- 结构化 raw_content 解析（无 LLM 成本）：`backend/scripts/backfill_tencent_metadata.py`
- Rule-based role_type 标签：`backend/scripts/backfill_role_type_rules.py`（vendor 公司白名单 + title 正则）
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

`insights.json` / `report.json` 切回 LLM 自动生成（v0.9 是 Claude 手写）。每次 ~5 美金，可选。

剩余 NULL role_type ~480 条经多轮 rule-based + manual SQL 处理后基本是真支撑岗（HR/财务/法务等），LLM 跑也大概率打 null。**不需要再 LLM 解析**。

**启动 prompt**：
> agent-hunt 项目，OpenRouter 余额已充值。跑 `generate_insights.py` + `generate_report.py` 让 LLM 重写 `insights.json` / `report.json` 文本字段。验证数字与最新 narrative-stats.json 一致后 commit + push（GitHub Actions weekly-refresh 自动 deploy）。

---

### 🟢 P2 — 国内剩 6 家大厂 LLM 厂商

**ROI**：⭐⭐ — 重活，每家单独写 Playwright

剩 6 家：字节 / 阿里 / 百度 / 商汤 / 阶跃 / 零一万物（**腾讯 v0.10 已完成**：`collect_vendor_tencent.py` 公开 JSON API + 1,049 条入库）。

剩下这 6 家多用自建招聘系统：
- 字节 `jobs.bytedance.com` — POST + token-gated，需 Playwright
- 阿里 `careers.alibaba.com` — 403 需 cookie/referer
- 百度 `talent.baidu.com` — SSR Next.js
- 商汤 / 阶跃 / 零一 — URL 不明 / SPA / 404，需重新探查

**前置**：先确认业务有需求（学员问起这些厂在不在数据里）才做。

**入表**：`jobs` 表，`source="vendor_official"`，`platform_id="vendor_<slug>"`

**启动 prompt**：
> agent-hunt 项目，做 issue #12 后续 — 国内剩 6 家大厂 LLM 厂商（字节 / 阿里 / 百度 / 商汤 / 阶跃 / 零一万物）。腾讯模式（`collect_vendor_tencent.py` 公开 API）能复用就复用，不能就 Playwright per-vendor。参考 `collect_vendor_tencent.py` + `backend/app/collectors/boss_zhipin.py`。

---

### 🟢 P2 — 维护性任务

- **skill_aliases.json 扩展**：定期跑 `GET /skills/unmatched` 看哪些原始技能没被映射，补充
- **Chrome 扩展完善**：`extension/` 目录下的 4 平台内容脚本，按需更新
- **Celery 定时采集**：`app/tasks/celery_app.py` 已配 beat（每月 1 号 03:00 UTC 跑 `run_monthly_snapshot`）。云端化后 worker 可跑在 Railway / Fly.io / Cloud Run，但目前优先级低
- **Supabase region 迁 us-west**：当前 ap-southeast-2，跨 region GitHub Actions runner 有延迟（collect 受影响）。如果 collect 用 GitHub Actions 跑得多了，考虑迁

---

## 已完成（最近）

### v0.10（2026-04-30 晚）
- **云端化** —— PostgreSQL 迁 Supabase（ap-southeast-2，free tier 28MB/500MB）。`config.py` 加 `AH_DATABASE_URL_OVERRIDE` 字段切换本地/云。本地 docker-compose 仍是 dev 环境
- **GitHub Actions 自动化** —— `weekly-refresh.yml`（cron 周日 02:00 UTC export+deploy，3min 跑完）+ `collect-data.yml`（用户手动 trigger 可选 hn/github/tencent/all）
- **腾讯 vendor collector** —— `careers.tencent.com` 公开 JSON API，1,049 条 AI 岗入库（domestic 1024 + intl 25），全 rule-based labeled（`backfill_tencent_metadata.py` + 加 `vendor_tencent` 到 AI_NATIVE_VENDOR_PLATFORMS）
- **完整 role_type backfill** —— labeled 5,673 → 8,550（69% → 92%）。多轮 rule-based + 7 manual SQL patches + 23 string-'null' 清理
- **删 ops/launchd** —— 替代为 GitHub Actions

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
