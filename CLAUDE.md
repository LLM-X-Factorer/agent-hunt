# Agent Hunt — Development Guide

## Project Overview
AI 职业市场全景分析平台。采集国内外招聘平台 JD，通过 Gemini API 解析（含行业分类），生成技能图谱、跨市场对比、行业 AI 渗透分析和个性化学习路径。

## Quick Start
```bash
cp .env.example .env          # 填入 Gemini API Key
docker compose up -d           # PostgreSQL 16 (pgvector) + Redis 7
cd backend && uv venv --python 3.11 .venv && uv pip install -e ".[dev]"
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload  # http://localhost:8000/docs
```

## Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0 (async + asyncpg), Alembic, Celery
- **AI**: Gemini API (gemini-2.5-flash) via `google-genai` SDK
- **DB**: PostgreSQL 16 + pgvector, Redis 7
- **Lint/Test**: ruff, pytest + pytest-asyncio

## Project Structure
```
backend/
  app/
    api/v1/          # REST endpoints (jobs, platforms, skills, analysis)
    collectors/      # Data collectors for live JD platforms (strategy + registry)
    models/          # Job, Platform, Skill, Snapshot, SalaryReport, ApplicantProfile
    schemas/         # Pydantic request/response schemas
    services/        # jd_parser, seed, skill_extractor, cross_market, market_analyzer, learning_path
    tasks/           # Celery async tasks
    config.py        # pydantic-settings, env prefix: AH_
    database.py      # Async engine + session factory
    main.py          # FastAPI app with lifespan (auto seeds on startup)
  alembic/versions/  # 001 initial → 008 add_job_source (8 migrations)
  scripts/
    collect_*.py     # Standalone collectors (vendor_ats, hn_wih, nowcoder_posts, levels_fyi)
    export_*.py      # Frontend JSON exporters (market_data, real_salary, trends, roles_by_industry, augmented_by_profession, graduate_friendly, quality_signals, applicant_profiles)
    analyze_roles.py # Role clustering (DOMESTIC_ROLES + INTERNATIONAL_ROLES taxonomies)
    backfill_quality_labels.py  # asyncio.wait_for batch LLM pattern
  tests/
frontend/            # Next.js 16 + Tailwind + shadcn/ui + Recharts
  src/app/           # Pages (dashboard, skills, salary, gaps, industry, insights)
  public/data/       # Pre-exported static JSON (incl. roles-real-salary.json, roles-by-industry.json, etc.)
data/                # Seed data (platforms, skills, aliases, search_keywords) + cookies
docs/
  README.md          # 文档索引
  agent-hunt/
    domestic-scraping-strategy.md
    next-tasks.md    # ← 跨会话任务清单 + 启动 prompt（4 待办 issue）
  employment-course/ # 就业班产品设计 v1.0（产品总纲/竞品/诊断报告模板/招生页）
  legacy/            # 旧课程归档
content/             # 自媒体内容（按选题组织：thread/xiaohongshu/wechat + assets）
```

## Key Patterns
- **Config**: pydantic-settings with `AH_` env prefix
- **DB sessions**: async generator via `get_db()` dependency
- **Seed data**: auto-loaded on startup via lifespan hook
- **Dedup**: `(platform_id, platform_job_id)` unique constraint on jobs
- **JD parsing**: Gemini API with structured JSON output, bilingual prompt (zh/en)
- **Salary normalization**: all converted to RMB monthly
- **Collectors**: BaseCollector ABC + CollectorRegistry (strategy + registry pattern)
  - Register via `register()` in `collectors/registry.py`
  - Auto-imported in `collectors/__init__.py`
  - JobSpy wraps LinkedIn/Indeed/Glassdoor into the same interface
  - Liepin: Playwright headless, no login needed, `.job-card-pc-container` selector
  - Boss直聘/拉勾: need Cookie file (`data/boss_cookies.json` / `data/lagou_cookies.json`)
  - Cookie export: `python scripts/export_cookies.py <platform_id>`
- **Analysis**: Python in-memory aggregation (data < 1000 rows, no need for complex SQL)
  - Skill normalization: `skill_aliases.json` lookup, updates Skill.domestic/international_count
  - Must `POST /skills/normalize` after new data before analysis endpoints are accurate
  - Industry analysis: `/analysis/industry/overview`, `/analysis/industry/salary`
- **Batch collection**: `data/search_keywords.json` defines keyword matrix, `scripts/batch_collect.py` automates

## Database Models
- **platforms** — 招聘平台元数据 (id is string slug like "boss_zhipin", "vendor_openai", "community_hn_wih")
- **jobs** — JD 原始文本 + LLM 解析后字段（含 `industry`、`source` ∈ {platform, vendor_official, community_open}）
- **skills** — 技能分类，JSONB aliases 支持多语言别名
- **snapshots** — 月度数据快照（migration 003，#13 时间序列基础设施）
- **salary_reports** — 真实到手薪酬爆料（独立于 JD asking，#15）。`source` ∈ {levels_fyi, ...}，`(source, source_record_id)` 唯一约束。`market` 字段基于 location 含中国城市自动归 domestic
- **applicant_profiles** — 求职者侧画像（#14 supply side），nowcoder 718 个

## Code Style
- ruff, line-length 100, target Python 3.11
- pytest asyncio_mode = "auto"

## Frontend
- Next.js 16 + Tailwind + shadcn/ui + Recharts
- 静态导出 (`output: "export"`) 部署到 Cloudflare Pages
- 无后端依赖：所有数据预导出为 `frontend/public/data/*.json`
- 数据更新流程：
  1. 后端导出 API 数据到 `frontend/public/data/`
  2. `python scripts/generate_insights.py` 生成 AI 洞察
  3. `cd frontend && npm run build`
  4. `npx wrangler pages deploy out --project-name agent-hunt`
- Gemini 生成的 AI 洞察（InsightCard 组件）放在每个页面顶部
- 8 个页面：总览、洞察报告、技能图谱、薪资分析、市场差异、行业分析、岗位画像（含学习路径）
- 角色聚类数据：`roles-domestic.json`（14 角色）、`roles-international.json`（11 角色）

## Current Status

**数据规模（2026-04-29）**：
- **Jobs**: 5980 总 / 5591 parsed
  - by source: `platform` 3083 (Boss/Liepin/Lagou/LinkedIn/Indeed) · `vendor_official` 1532 (OpenAI 653 / Anthropic 452 / xAI 230 / Cohere 115 / DeepMind 82) · `community_open` 1365 (HN Who is Hiring)
- **SalaryReports**: 1392（全部 levels.fyi；international 1147 / domestic 245）
- **ApplicantProfiles**: 718（全部 nowcoder）
- **Skills**: 71 · **Industries**: 13 · **Platforms**: 16 · **Migrations**: 8

**已部署**：前端 8 页 v0.7 数据在 agent-hunt.pages.dev（v0.8 数据待重新部署）

### v0.8 进展（2026-04-29）
- **#9/#10 行业 × 岗位 2D 切片** — `export_roles_by_industry.py` + `export_augmented_by_profession.py` + `export_graduate_friendly.py` 上线
- **#12 Vendor 官方 ATS 适配器** — `collect_vendor_ats.py` 抓 OpenAI/Anthropic/xAI/Cohere/DeepMind 共 1532 条（Greenhouse + Ashby 通用适配）
- **#14 Supply-side 求职者画像** — `collect_nowcoder_posts.py` + `applicant_profiles` 表 + `export_applicant_profiles.py`，已采 718 条
- **#15 真实薪资 (pivot)** — 看准爆料板已 platform-offline → 改用 levels.fyi。`collect_levels_fyi.py` 扩展 13 家 CN 大厂 slug + location-based market 检测，`SalaryReport` 表 + `export_real_salary.py` 输出 `roles-real-salary.json`（real vs JD asking gap）
- **#17 隐藏渠道** — `collect_hn_wih.py` 抓 HN「Who is Hiring」月度帖子（Algolia API），1365 条入库

### Phase 7 待办（详见 `docs/agent-hunt/next-tasks.md`）
- **#17 后续** — GitHub hiring repos（awesome-jobs / monthly-hiring-threads，零反爬）
- **#14 后续** — 一亩三分地 offer 板（海外 + 留学背景，与 nowcoder 互补）
- **#12 后续** — 国内 11 家 LLM 厂商官网（智谱/Moonshot/百川/MiniMax/字节/阿里/腾讯/百度/商汤/阶跃星辰/零一万物，多用自建系统需 Playwright）
- **#10/#11/#13/#16** — AI 原生 vs AI 增强标签 / 校招专项切片 / 月度快照定时任务 / 岗位真伪信号
- 基础设施：skill_aliases 持续扩展、Chrome 扩展完善、Celery 定时采集

### 已确认不可达数据源（不要再尝试）
- **看准爆料板**（kanzhun.com）— 平台已下线（`renderStatus: fail` / `offline: true`），firm/wage 详情页强制跳 Boss 登录。Boss/Kanzhun 整合后 PC 薪资查询线全砍
- **OfferShow 公开 API**（offershow.cn）— `search_salary_list` 仅返回校招清单元数据（公司+届数+PDF链接），逐条字段在 VIP + PDF 后面，ROI 太差
- **脉脉工资**（maimai.cn）— 反爬重 + 强登录，issue #15 提到「放后期」，至今未做

## 就业班产品设计（已完成 v1.0）
完整产品设计文档在 `docs/employment-course/`，11 节产品总纲覆盖 4 主线矩阵 / 12 周陪跑 / 透明数据机制 / 30×3800 商业模型。设计阶段全部锁定，落地物料（产品总纲/竞品扫描/诊断报告模板/招生页）已交付。

## Spin-off: aijobfit
AI 求职定位诊断 dashboard 已 spin off 为独立项目，并已上线 https://aijobfit.llmxfactor.cloud：
- 位置：`/Users/liu/Projects/aijobfit/`（与本项目同级）
- GitHub：https://github.com/LLM-X-Factorer/aijobfit
- 关系：本项目（agent-hunt）= 数据生产方；aijobfit = 数据消费方（远程 fetch agent-hunt.pages.dev/data/*.json）
- **产品定位已 pivot（2026-04-22）**：从原计划 9.9 元付费 → **永久免费 + 加微信漏斗**。漏斗：免费诊断 → 看前 3 节 → 撞遮罩 → 加小助理微信 → 拿激活码 `AIJOB-2026` 解锁后 4 节。商业化（1V1 / 社群 / 课程 / 就业班）在产品外独立运营，与 aijobfit 仓库解耦
- **不要在本仓库实现诊断相关功能**，去 aijobfit 项目做。设计文档（`docs/employment-course/`）作为权威来源留在本项目

## Content（自媒体内容）
- 目录：`content/{序号}-{选题slug}/`，每个选题下有 `thread.md`（X）、`xiaohongshu.md`、`wechat.md`、`assets/`
- 数据洞察驱动内容，工具是内容的售后（不单独推广工具）
- 发布顺序：X thread 先发试水 → 小红书图文 → 公众号长文
- 引流闭环：评论区「留下技能栈」→ 免费 AI 求职定位诊断（aijobfit）→ 撞遮罩 → 加小助理微信
- 选题队列见 `content/README.md`
