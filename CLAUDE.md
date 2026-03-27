# Agent Hunt — Development Guide

## Project Overview
AI Agent 工程师岗位数据分析平台。采集国内外招聘平台 JD，通过 Gemini API 解析，生成技能图谱和跨市场对比。

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
    services/        # Business logic (jd_parser, seed, skill_extractor, cross_market)
    tasks/           # Celery async tasks
    config.py        # pydantic-settings, env prefix: AH_
    database.py      # Async engine + session factory
    main.py          # FastAPI app with lifespan (auto seeds on startup)
  alembic/           # DB migrations
  tests/
data/                # Seed data (platforms, skills, aliases)
extension/           # Chrome extension (placeholder)
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

## Database Models
- **platforms** — 招聘平台元数据 (id is string slug like "boss-zhipin")
- **jobs** — JD 原始文本 + LLM 解析后结构化字段
- **skills** — 技能分类，JSONB aliases 支持多语言别名

## Code Style
- ruff, line-length 100, target Python 3.11
- pytest asyncio_mode = "auto"

## Current Status
Phase 1 + 2 完成。5 平台采集器跑通，334 条 JD 解析完成。跨市场分析引擎已实现（技能归一化、薪资分析、国内外对比、技能共现）。下一步 Phase 3 前端可视化。
