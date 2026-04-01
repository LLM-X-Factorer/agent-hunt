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
    collectors/      # Data collectors (strategy pattern + registry)
    models/          # SQLAlchemy models (Job, Platform, Skill)
    schemas/         # Pydantic request/response schemas
    services/        # Business logic (jd_parser, seed, skill_extractor, cross_market, market_analyzer, learning_path)
    tasks/           # Celery async tasks
    config.py        # pydantic-settings, env prefix: AH_
    database.py      # Async engine + session factory
    main.py          # FastAPI app with lifespan (auto seeds on startup)
  alembic/           # DB migrations (001_initial + 002_add_industry)
  scripts/           # Utility scripts (export_cookies, generate_insights, generate_report, batch_collect, analyze_roles, export_market_data)
  tests/
frontend/            # Next.js 16 + Tailwind + shadcn/ui + Recharts
  src/app/           # Pages (dashboard, skills, salary, gaps, industry, insights)
  public/data/       # Pre-exported static JSON data
data/                # Seed data (platforms, skills, aliases, search_keywords)
docs/                # Technical docs
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
- **platforms** — 招聘平台元数据 (id is string slug like "boss-zhipin")
- **jobs** — JD 原始文本 + LLM 解析后结构化字段（含 `industry` 行业分类）
- **skills** — 技能分类，JSONB aliases 支持多语言别名

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
Phase 1-6 完成。5 平台采集器，2370 条 JD（1542 已解析），68 个技能，13 个行业。前端 8 页已部署到 agent-hunt.pages.dev。

v0.6 新增：
- 角色聚类分析（14 国内 + 11 海外典型角色，含技能画像/薪资/学历/行业分布）
- 分市场独立分析（国内/海外技能排名、行业矩阵、共现网络完全独立）
- SCI（Skill Criticality Index）评分模型
- 新脚本：`scripts/analyze_roles.py`（角色聚类）、`scripts/export_market_data.py`（分市场数据导出）
- 新数据：`roles-domestic.json`、`roles-international.json`

Phase 7 待办：skill_aliases 扩展、Chrome 扩展完善、Celery 定时采集、（未来）用户系统
