# Agent Hunt — Development Guide

## Project Overview
AI 职业市场全景分析平台。采集国内外招聘平台 JD，用 LLM 解析（含行业 / role_type / 原职业分类），生成跨市场对比 / 行业 AI 渗透 / 角色聚类 / 5 条市场判断叙事。是 aijobfit 求职诊断 dashboard 的数据生产端。

## Quick Start
```bash
cp .env.example .env          # 填入 AH_OPENROUTER_API_KEY
docker compose up -d           # PostgreSQL 16 (pgvector) + Redis 7
cd backend && uv venv --python 3.11 .venv && uv pip install -e ".[dev]"
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload  # http://localhost:8000/docs
```

## Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0 (async + asyncpg), Alembic, Celery
- **LLM**: OpenRouter `deepseek/deepseek-v3.2-exp`（默认）via `openai` SDK 兼容协议。详细决策见 memory `project_architecture.md`
- **DB**: PostgreSQL 16 + pgvector, Redis 7
- **Lint/Test**: ruff, pytest + pytest-asyncio

## Project Structure
```
backend/
  app/
    api/v1/          # REST endpoints (jobs, platforms, skills, analysis)
    collectors/      # Data collectors for live JD platforms (strategy + registry)
    models/          # Job (含 salary_mid_cny_monthly 防呆属性), Platform, Skill, Snapshot, SalaryReport, ApplicantProfile
    schemas/         # Pydantic request/response schemas
    services/        # jd_parser, seed, skill_extractor, cross_market, market_analyzer, currency, cities, learning_path
    tasks/           # Celery async tasks (snapshots monthly cron)
    config.py        # pydantic-settings, env prefix: AH_
    database.py      # Async engine + session factory
    main.py          # FastAPI app with lifespan (auto seeds on startup)
  alembic/versions/  # 001 → 008 (add_job_source 是最新)
  scripts/
    collect_*.py     # 数据采集 (vendor_ats / hn_wih / nowcoder_posts / levels_fyi / github_hiring / moka / feishu)
    export_*.py      # 衍生 JSON 生成 (api_snapshots / market_data / real_salary / trends / roles_by_industry / roles_by_city / augmented_by_profession / graduate_friendly / quality_signals / applicant_profiles / industry_salary / vendor_title_breakdown / narrative_stats / narrative_examples)
    analyze_roles.py # 角色聚类 (DOMESTIC_ROLES + INTERNATIONAL_ROLES taxonomies)
    backfill_*.py    # asyncio.wait_for 批量 LLM 模式
    generate_insights.py / generate_report.py — LLM 生成中文洞察文本（成本敏感时改手写）
  tests/
frontend/            # Next.js 16 + Tailwind + shadcn/ui + Recharts
  src/app/
    page.tsx         # 双轨入口首页
    narrative/       # 叙事手册 6 页（目录页 + p1-p5）— 业务人员用
    skills/ salary/ gaps/ industry/ insights/ report/  # 数据看板（旧）— 深度查询
  src/components/
    narrative-layout.tsx + narrative-bits.tsx  # 论断页通用结构
  public/data/       # 预导出静态 JSON（30+ 个，aijobfit 远程 fetch）
data/                # Seed data (platforms, skills, aliases, search_keywords) + cookies
docs/
  README.md          # 文档索引
  agent-hunt/
    domestic-scraping-strategy.md
    next-tasks.md    # 跨会话任务清单 + 启动 prompt
  employment-course/ # 就业班产品设计 v1.0
content/             # 自媒体内容 (thread / xiaohongshu / wechat + assets)
```

## Key Patterns

### 通用约定
- **Config**: pydantic-settings with `AH_` env prefix
- **DB sessions**: async generator via `get_db()` dependency
- **Seed data**: auto-loaded on startup via lifespan hook
- **Dedup**: `(platform_id, platform_job_id)` unique constraint on jobs
- **JD parsing**: OpenRouter LLM with structured JSON output, 双语 prompt
- **Code Style**: ruff line-length 100, pytest asyncio_mode = "auto"

### 薪资聚合（重要防呆）
**任何跨市场聚合 salary 必须用 `Job.salary_mid_cny_monthly` 属性**，不要直接 `(salary_min + salary_max) // 2`。该属性会做：① 海外 USD/EUR/GBP 等年薪 → CNY 月薪汇率换算（基于 `app/services/currency.py`）；② 国内 CNY 年薪离群值（>200k）÷12 月化。直接裸算会让 USD/年 被误读为 CNY/月，把跨市场 ratio 夸大 1.7×。

### 数据采集
- **Collectors**: BaseCollector ABC + CollectorRegistry (strategy + registry pattern)
  - JobSpy wraps LinkedIn/Indeed/Glassdoor 进同一接口
  - Liepin: Playwright headless, 不需要 login
  - Boss直聘 / 拉勾: 需要 Cookie 文件（`data/<platform>_cookies.json`）
  - Cookie export: `python scripts/export_cookies.py <platform_id>`
- **Vendor ATS 通用适配**：`collect_vendor_ats.py`（Greenhouse + Ashby）
- **公开 API 模式**：HN（Algolia）/ GitHub hiring（listings.json）零反爬
- **Batch keyword 采集**：`data/search_keywords.json` 定义矩阵，`scripts/batch_collect.py` 自动化

### 衍生数据导出流程
```bash
cd backend
.venv/bin/python scripts/export_api_snapshots.py        # 12 个 API-mirror JSON
.venv/bin/python scripts/export_market_data.py          # industry/cooccurrence × {dom, intl}
.venv/bin/python scripts/analyze_roles.py               # roles-{domestic,international}.json
.venv/bin/python scripts/export_real_salary.py          # roles-real-salary.json (含 levels.fyi)
.venv/bin/python scripts/export_roles_by_city.py        # 角色 × 城市 tier × 薪资分布
.venv/bin/python scripts/export_narrative_stats.py      # 5 论断核心数字
.venv/bin/python scripts/export_narrative_examples.py   # 真实 JD 例子
# ... 其他 export_*.py 按需
cd ../frontend && npm run build && npx wrangler pages deploy out --project-name agent-hunt
```

注意：`generate_insights.py` / `generate_report.py` 默认调 LLM（成本约 $5/全量）。OpenRouter 余额紧张时直接手写 `insights.json` / `report.json` 文本字段（schema：`dashboard/skills/salary/gaps_insight` + `overview/industry_deep_dive/career_guide/trends/key_findings`）。

### 分析逻辑
- **In-memory aggregation**：数据 < 10000 行，全部 Python 内存聚合，不用复杂 SQL
- **Skill normalization**：`skill_aliases.json` lookup，更新 Skill.domestic/international_count。新数据后跑 `POST /skills/normalize` 才能让 analysis endpoints 准确

## Database Models
- **platforms** — 招聘平台元数据（id is string slug like "boss_zhipin", "vendor_openai", "community_hn_wih"）
- **jobs** — JD 原始文本 + LLM 解析后字段（含 `industry`、`role_type` ∈ {ai_native, ai_augmented_traditional, null}、`source` ∈ {platform, vendor_official, community_open}、`base_profession` 仅 ai_augmented 时填）
- **skills** — 技能分类，JSONB aliases 支持多语言别名
- **snapshots** — 月度数据快照（migration 003）
- **salary_reports** — 真实到手薪酬爆料（独立于 JD asking）。`source` ∈ {levels_fyi, ...}，`(source, source_record_id)` 唯一约束
- **applicant_profiles** — 求职者侧画像，nowcoder 718 个

## Frontend
- Next.js 16 + Tailwind + shadcn/ui + Recharts，静态导出（`output: "export"`）→ Cloudflare Pages
- **双轨架构**（v0.9）：
  - 📖 **叙事手册** `/narrative` —— 6 页（目录 + p1~p5），业务人员讲解 / 招生用。每页 = 论断 + 关键数字 + 图表 + 真实 JD 例子 + 业务话术 + 适用边界
  - 📊 **数据看板** —— 8 页（总览 / 报告 / 技能图谱 / 薪资分析 / 市场差异 / 行业分析 / 岗位画像）。深度查询 / 数据验证用
- 角色聚类数据：`roles-domestic.json`（14 角色）、`roles-international.json`（11 角色）、`roles-by-city.json`（每角色 × 城市 tier × p25/p50/p75）

## Current Status

**数据规模（2026-04-30）**：
- **Jobs**: 8634 总 / 8238 parsed / 5673 LLM-labeled with role_type
  - by source: `platform` 3083（Boss / Liepin / Lagou / LinkedIn / Indeed）· `vendor_official` 2065（OpenAI 651 / Anthropic 451 / xAI 230 / Cohere 115 / DeepMind 82 / 国内 4 家创业公司 533）· `community_open` 3486（HN Who is Hiring 1365 + GitHub hiring 2121）
  - by market: 国内 2762 / 海外 5476
  - median salary: 国内 27.5k / 海外 72.5k CNY/月（汇率换算后）
- **SalaryReports**: 1392（全部 levels.fyi；international 1147 / domestic 245）
- **ApplicantProfiles**: 718（全部 nowcoder）
- **Skills**: 71 · **Industries**: 13 · **Platforms**: 17 · **Migrations**: 8

**已部署**：v0.9 叙事手册 + 修正薪资数据已上线 https://agent-hunt.pages.dev

### v0.9 进展（2026-04-30）
- **P0 叙事手册** —— 双轨入口首页 + 5 条论断页 + 通用 narrative-layout 组件 + business 视角的方法论 / 机制 / 反例三个 box
- **P0 currency normalization 防呆** —— 新建 `app/services/currency.py` + Job 模型加 `salary_mid_cny_monthly` 属性。修复 cross_market service 历史 bug：海外 USD/年 被误读为 CNY/月，导致 ratio 夸大 1.7×
- **新数据切片** —— `industry-augmented-salary.json`（行业 × AI 增强薪资）/ `vendor-title-breakdown.json`（桥梁工程师占比）/ `narrative-stats.json`（5 论断核心数字）/ `narrative-examples.json`（真实 JD 例子）/ `roles-by-city.json`（角色 × 城市 tier × 薪资）
- **`export_api_snapshots.py`** —— 替代之前手工 curl 留存的 12 个 API-mirror JSON（cross-market-overview / salary-by-* / skill-gaps 等），从 v0.6 数据更新到 v0.9
- **insights.json / report.json 手写** —— OpenRouter 成本敏感，由 Claude 直接手写，与新数字口径完全一致

### v0.8 进展（2026-04-29）
- **#9/#10/#11 行业 × 岗位 2D 切片** —— `export_roles_by_industry.py` + `export_augmented_by_profession.py` + `export_graduate_friendly.py`
- **#12** Vendor 官方 ATS 适配器 —— OpenAI / Anthropic / xAI / Cohere / DeepMind 共 1532 条 + 国内 4 家（智谱 / Moonshot / 百川 / MiniMax）533 条
- **#13** 月度快照定时任务 —— Celery beat 每月 1 号 03:00 UTC 跑 `run_monthly_snapshot`
- **#14** Supply-side 求职者画像 —— nowcoder 718 条
- **#15 (pivot)** 真实薪资 —— levels.fyi 1392 条（看准爆料板已下线）
- **#16** 岗位真伪信号 —— ghost listing detection（同 company+title ≥ 5 次）
- **#17** 隐藏渠道 —— HN Who is Hiring 1365 条 + GitHub hiring 2121 条

### Phase 7+ 待办（详见 `docs/agent-hunt/next-tasks.md`）
- **观察期** —— 等 aijobfit 业务方实际跑过 4 个验收 case（电气工程师 + 教育、教育 + PM、预期薪资达成概率、JD 总数同步）后看数据消费有没有新缺口
- **OpenRouter 余额恢复后** —— 跑剩 1999 条 GitHub hiring LLM 解析（不影响 narrative 数据，主要拉高 labeled_jobs 比例）+ insights/report 切回 LLM 自动生成
- **#12 后续** —— 国内 7 家大厂 LLM 厂商（字节 / 阿里 / 腾讯 / 百度 / 商汤 / 阶跃 / 零一）多用自建系统需 Playwright，ROI 低
- **基础设施** —— skill_aliases 持续扩展、Chrome 扩展完善、Celery 定时采集

### 已确认不可达数据源（不要再尝试）
- **看准爆料板**（kanzhun.com）—— 平台已下线（`renderStatus: fail`），firm/wage 强制跳 Boss 登录
- **OfferShow 公开 API**（offershow.cn）—— 只返回校招清单元数据，逐条字段在 VIP + PDF 后面
- **脉脉工资**（maimai.cn）—— 反爬重 + 强登录
- **一亩三分地**（1point3acres.com）—— CF 挑战可过但 fid=237 工资板积分门槛 200 / fid=145 海外面经板 188，匿名拿不到 candidate 画像

## 就业班产品设计（已完成 v1.0）
完整文档在 `docs/employment-course/`，11 节产品总纲覆盖 4 主线矩阵 / 12 周陪跑 / 透明数据机制 / 30×3800 商业模型。设计阶段全部锁定。

## Spin-off: aijobfit
AI 求职定位诊断 dashboard 已 spin off 为独立项目并上线 https://aijobfit.llmxfactor.cloud：
- 位置：`/Users/liu/Projects/aijobfit/`（与本项目同级）
- GitHub：https://github.com/LLM-X-Factorer/aijobfit
- 关系：本项目 = 数据生产方；aijobfit = 数据消费方（远程 fetch agent-hunt.pages.dev/data/*.json）
- **产品定位**（2026-04-22 pivot）：永久免费 + 加微信漏斗。漏斗：免费诊断 → 看前 3 节 → 撞遮罩 → 加小助理微信 → 拿激活码 `AIJOB-2026` 解锁后 4 节
- **改造 in flight**（2026-04-30）：业务方反馈 6 条问题（推荐脱离行业 / 报告章节没切片 / 预期薪资达成概率 / 流程倒置 / 城市差异 / 数据过时）→ aijobfit 端 8 项改造（4 P0 + 4 P1/P2）正在做
- **不要在本仓库实现诊断相关功能**

## Content（自媒体内容）
- 目录：`content/{序号}-{选题slug}/`，每个选题下有 `thread.md` / `xiaohongshu.md` / `wechat.md` / `assets/`
- 数据洞察驱动内容，工具是内容的售后（不单独推广工具）
- 发布顺序：X thread 先发试水 → 小红书图文 → 公众号长文
- 引流闭环：评论留技能栈 → 免费 aijobfit 诊断 → 撞遮罩 → 加小助理微信
- 选题队列见 `content/README.md`
