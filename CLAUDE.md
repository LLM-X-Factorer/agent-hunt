# Agent Hunt — Development Guide

## Project Overview
AI 职业市场全景分析平台。采集国内外招聘平台 JD，用 LLM 解析（含行业 / role_type / 原职业分类），生成跨市场对比 / 行业 AI 渗透 / 角色聚类 / 5 条市场判断叙事。是 aijobfit 求职诊断 dashboard 的数据生产端。

## Quick Start
```bash
cp .env.example .env          # 填入 AH_OPENROUTER_API_KEY
# Option A: cloud DB (生产口径) — 在 .env 设 AH_DATABASE_URL_OVERRIDE=postgresql://...
# Option B: 本地 docker dev
docker compose up -d           # PostgreSQL 16 (pgvector) + Redis 7
cd backend && uv venv --python 3.11 .venv && uv pip install -e ".[dev]"
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload  # http://localhost:8000/docs
```

## Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0 (async + asyncpg), Alembic, Celery
- **LLM**: OpenRouter `deepseek/deepseek-v3.2-exp`（默认）via `openai` SDK 兼容协议。详细决策见 memory `project_architecture.md`
- **DB**: Supabase Postgres 17（生产）/ PostgreSQL 16 docker-compose（本地 dev）— 配置项 `AH_DATABASE_URL_OVERRIDE` 切换
- **CI/CD**: GitHub Actions（`.github/workflows/weekly-refresh.yml` 周日 02:00 UTC export+deploy；`collect-data.yml` 手动触发数据采集）
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
  alembic/versions/  # 001 → 009 (add_major_requirement 是最新)
  data/
    role_descriptions.json       # 27 条手写角色描述（v0.11 加，喂 export_role_profiles）
    profession_descriptions.json # 8 条手写传统职业（v0.12 B2 加，喂 export_profession_profiles）
  scripts/
    collect_*.py     # 数据采集 (vendor_ats / vendor_tencent / vendor_bytedance / hn_wih / nowcoder_posts / levels_fyi / github_hiring / moka / feishu)
    export_*.py      # 衍生 JSON 生成 (api_snapshots / market_data / real_salary / trends / roles_by_industry / roles_by_city / role_profiles / profession_profiles / augmented_by_profession / graduate_friendly / quality_signals / applicant_profiles / industry_salary / vendor_title_breakdown / narrative_stats / narrative_examples)
    analyze_roles.py # 角色聚类 (DOMESTIC_ROLES + INTERNATIONAL_ROLES taxonomies)
    backfill_*.py    # asyncio.wait_for 批量 LLM 模式
    generate_insights.py / generate_report.py — LLM 生成中文洞察文本（成本敏感时改手写）
  tests/
frontend/            # Next.js 16 + Tailwind + shadcn/ui + Recharts
  src/app/
    page.tsx         # 五轨入口首页（叙事 / 岗位 / 职业 / 课本 / 看板）
    narrative/       # 叙事手册 6 页（目录页 + p1-p5）— 业务人员用
    roles/           # 岗位画像列表 (v0.11) + [market]/[roleId] 详情 SSG 27 路径
    professions/     # 传统职业 (v0.12 B2) + [id] 详情 SSG 8 路径
    learn/           # 三层课本 (v0.12 B3+C) — [level] 列表 + [level]/[slug] 文章页（marked + gray-matter）
    skills/ salary/ gaps/ industry/ insights/ report/  # 数据看板（旧）— 深度查询
  src/components/
    narrative-layout.tsx + narrative-bits.tsx  # 论断页通用结构
  src/lib/roles.ts   # RoleProfile 类型 + Market label / fmtSalaryK helper
  src/lib/learn.ts   # 课本 frontmatter 扫描 + 邻接计算 (v0.12 B3)
  public/data/       # 预导出静态 JSON（35+ 个，aijobfit 远程 fetch；含 role-profiles.json + profession-profiles.json）
content/
  learn/             # 课本内容（v0.12 B3+C）— lv1/*.md (5 入门) + lv2/*.md (16 职业百科) + lv3/*.md (7 转岗路径)
  {序号}-{选题}/     # 自媒体内容（thread / xiaohongshu / wechat + assets）
data/                # Seed data (platforms, skills, aliases, search_keywords) + cookies
docs/
  README.md          # 文档索引
  agent-hunt/
    domestic-scraping-strategy.md
    next-tasks.md    # 跨会话任务清单 + 启动 prompt
    v012-*-handoff.md  # 各阶段交接 prompt（B1 / B2 / C）
  employment-course/ # 就业班产品设计 v1.0
  operations/        # 运营 / 业务方文档（v0.11.2 加）— 产品手册-运营版.md + 网站使用-图文版.md + screenshots/ + pdf/
scripts/
  build-docs-pdf.sh  # pandoc + Chrome headless 中文 PDF 流程（同时生成两份运营文档 PDF）
  docs-pdf.css       # PDF 样式表（A4 + 中文字体 + 蓝色 accent）
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
.venv/bin/python scripts/export_role_profiles.py        # role-profiles.json (聚合 + 手写描述, /roles 页消费)
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
- **五轨架构**（v0.12 C 完结，2026-05-13）：
  - 📖 **叙事手册** `/narrative` —— 6 页（目录 + p1~p5），业务人员讲解 / 招生用。每页 = 论断 + 关键数字 + 图表 + 真实 JD 例子 + 业务话术 + 适用边界
  - 🧭 **岗位画像** `/roles` —— 27 角色簇（domestic 15 + intl 12）按 market tab 切。详情页 SSG 预渲染 27 路径，含 hero stats / narrative / Required vs Preferred 技能 bar / 适合谁 vs 不适合 / vs_neighbor 邻居对比 / 学历 / 工作模式 / 行业 / 薪资分位 / sample titles / 硬性要求（学历 + 高频专业 + 高频职责，v0.12 B1）
  - 🧱 **传统职业** `/professions` —— 8 个传统职业（工程线 4 + 商科 2 + 服务 2）。详情页 SSG 预渲染 8 路径。每条含 one_liner / description / responsibilities / pathway_summary / who_should_pivot / who_shouldnt_pivot + `ai_pivot_targets` 真链接 → /roles
  - 📚 **三层课本** `/learn` —— Lv1 入门 (5) + Lv2 职业百科 (16：AI 岗 5 + 传统职业 8 + AI 岗补 3) + Lv3 转岗路径 (7) = **28 篇**。markdown + gray-matter frontmatter，marked 渲染
  - 📊 **数据看板** —— 7 页（报告 / 技能图谱 / 薪资分析 / 市场差异 / 行业分析 / 岗位画像 insights / 总览）。深度查询 / 数据验证用
- 角色聚类数据：`roles-domestic.json`（15 角色）、`roles-international.json`（12 角色）、`role-profiles.json`（合并 + 手写描述，27 条）、`roles-by-city.json`（每角色 × 城市 tier × p25/p50/p75）
- 手写角色描述源：`backend/data/role_descriptions.json`（27 条 × 6 字段：role_description / core_skills / vs_neighbor / narrative / who_fits / who_doesnt）。每条手写不用 LLM。**注意 narrative 开头的「N 条」数字会随数据变动过时**，每次重大数据 reparse 后跑 `python3 scripts/sync_narrative_numbers.py`（或手动 regex 替换，见 commit 7fd24e3 例子）。`other` 簇标注「混合簇 · 下一轮 P2 拆细」
- 手写传统职业描述源：`backend/data/profession_descriptions.json`（8 条 × 7 字段）
- 课本内容源：`content/learn/{lv1,lv2,lv3}/*.md`，写作约定见 `docs/agent-hunt/v012-c-handoff.md`

## Current Status

**数据规模（2026-05-13，v0.12 C）**：
- **Jobs**: ~9,690 总（含 ByteDance +3170 后；具体 export 时机会有 lag，最新数看 `frontend/public/data/full-stats.json` 或 memory `project_status.md`）
  - by source: `platform` 3083（Boss / Liepin / Lagou / LinkedIn / Indeed）· `vendor_official` ~6300（OpenAI 651 / Anthropic 451 / xAI 230 / Cohere 115 / DeepMind 82 / 国内 4 家创业 533 / 腾讯 1049 / **ByteDance 3170**）· `community_open` 3486（HN Who is Hiring 1365 + GitHub hiring 2121）
  - by market: 国内 ~6,956 parsed（含 Tencent + ByteDance）/ 海外 ~5,476
  - median salary: 国内 27.5k / 海外 72.5k CNY/月（汇率换算后）
- **SalaryReports**: 1392（全部 levels.fyi；international 1147 / domestic 245）
- **ApplicantProfiles**: 718（全部 nowcoder）
- **Skills**: 71 · **Industries**: 13 · **Platforms**: 23（含 vendor_bytedance）· **Migrations**: 009

**已部署**：v0.12 C 上线 https://agent-hunt.pages.dev（五轨：narrative 5 论断 + roles 27 角色 + professions 8 传统职业 + learn 28 篇课本 + 数据看板）

### v0.12 C 进展（2026-05-13）— /learn 内容齐全 + narrative 数字回填

- **`/learn` 28 篇全部交付**（issue #39，超目标 20）—— Lv1 入门 5 + Lv2 职业百科 16（AI 岗 5：ai-engineer / algorithm / product-manager / ml-scientist + 数据 / applied-scientist / sales-bd / prompt-engineer；传统职业 8：teacher / electrical / mechanical / civil / chemical / accountant / finance / sales）+ Lv3 转岗路径 7（teacher / electrical / mechanical / accountant / finance / sales / engineer → AI 角色）
- **写作约定**（值得未来 sessions 用）：① 每篇用不同生活类比开头（菜市场 / 拖拉机 / 发电厂 / 装电 / 老电工 / 老木匠 / 守桥老师傅 / 翻译家 / 外交官 / 驯兽师…）；② 必带「不适合谁」reality check；③ 数字必须从 `frontend/public/data/*.json` 拉，sample 量公开标注；④ **诚实劝退**比「welcoming + 可以转」价值大（prompt-engineer 篇警示 LLM 标注员陷阱、finance-to-quant 篇标 12 周成功率 30%）
- **role_descriptions.json 数字回填**（commit 7fd24e3）—— 9 处国内角色 narrative 开头「N 条」是 pre-ByteDance 数字，已回填到 post-ByteDance（ai_engineer 734→1538 / algorithm 328→1054 / product_manager 439→849 / operations 197→475 / sales_bd 152→176 / leadership 144→170 / data 82→164 / risk_compliance 32→55 / other 1347→2121）。仅改开头数字保留余下手写内容
- **内链审计零 404** —— 28 篇文章 51 个唯一内链全部 200

### v0.12 B3 进展（2026-05-13）— /learn 课本骨架 (#38 close, commit 4455d04)

- **第五轨 `/learn` 骨架**（数据契约 + 路由 + CSS）：`content/learn/{lv1,lv2,lv3}/*.md` 用 gray-matter frontmatter（title / order / summary / reading_minutes / linked_roles / linked_professions）+ `frontend/src/lib/learn.ts` 文件扫描 + 邻接计算
- **3 个 SSG 路由**：`/learn` 目录（3 卡）+ `/learn/[level]` 列表 + `/learn/[level]/[slug]` 文章页（marked 渲染 + 面包屑 + linked_roles/professions footer + 上一篇/下一篇）
- **`.learn-prose` 长文 CSS** 不依赖 @tailwindcss/typography

### v0.12 B2 进展（2026-05-13）— /professions 上线 (#37 close, commit 750200a)

- **第四轨 `/professions`** —— 回答业务方「我是 X 怎么转 AI」。8 个传统职业（工程线 4：电气 / 机械 / 土木 / 化工 + 商科 2：会计 / 金融 + 服务 2：教师 / 销售）
- **A1 半数据 ship 方案**（#37 原计划 blocked by #34，但 Boss/Liepin 反爬升级走不通）—— 用现有 2096 条 `ai_augmented_traditional` JD by `base_profession` 反向聚合，sample 量分层 disclaimer：strong ≥30 / medium 10-29 / weak 5-9（红 banner）/ none < 5（baseline 完全 suppress）
- **样本分布**：sales 100 / finance 68 / teacher 45 / mechanical 28 / accountant 18 / electrical 6 / civil 1 / chemical 1
- **数据洞察 cross-link**：teacher → education_ai ×13 (48%) / finance → algorithm ×16 (24%) / sales → sales_bd ×43 (43%) / mechanical → autonomous ×9。每个都是 Link 到 `/roles/[market]/[role_id]` 的真链接

### v0.12 B1+ 进展（2026-05-12）— ByteDance + 硬性要求 (#36 close)

- **`/roles/[id]` 加「硬性要求」section** —— 学历 + 高频专业 + 高频职责 三块。`major_requirement` 字段 alembic 009 + 9286 条 backfill
- **`role_type` enum 加 `non_ai_traditional`**（A3 #35）—— 区分纯非 AI 岗（不计入 AI 角色簇）
- **ByteDance vendor collector** —— `careers.bytedance.com` 公开 API + CDP re-enrich，国内 JD 3786 → 6956 parsed (+84%)
- **关键阻塞已查明 #34** —— Boss/Liepin 反爬升级到「浏览器指纹 + 行为检测」双层，CDP attach 撑不过 ~20 条 sequential detail，Liepin 触发 SMS。**大规模采集事实上不可行**，需重新设计

### v0.11.2 进展（2026-05-01）— 运营文档交付

- **`docs/operations/` 新目录** —— 给运营 / 业务方读的产品文档。模仿 aijobfit 的 `docs/产品手册-运营版.md` + `docs/用户流程-图文版.md` 双文档结构
- **`产品手册-运营版.md`**（11 页 PDF）—— 一句话定位（不是面向用户的产品 / 是内部叙事手册 + 数据自检工具）+ 数据来源 + 三轨用法 + 5 论断逐条解读（含话术 + 反例提醒）+ 27 角色清单 + 7 看板用法 + 典型场景 + 11 条常见误用
- **`网站使用-图文版.md`**（31 页 PDF · 16 张 1280px desktop 截图）—— 每个页面长什么样 + 怎么读 + 速查表
- **PDF 构建链** —— `scripts/build-docs-pdf.sh` + `scripts/docs-pdf.css`（pandoc + Chrome headless + A4 中文 CSS），从 aijobfit 抄过来调整路径。两份 PDF 同时生成
- **截图采集** —— Playwright MCP 拍线上 https://agent-hunt.pages.dev，16 张 fullPage 1280×900 desktop 截图存 `docs/operations/screenshots/`
- **关键差异 vs aijobfit 文档** —— 反复强调"Agent Hunt 不是面向求职者的产品"，没有漏斗 / 激活码 / 加微信内容；学员要诊断引到 aijobfit

### v0.11 进展（2026-05-01）
- **岗位画像 `/roles`（issue #18 P0 完结）** —— 三轨架构升级。手写 27 条角色描述（`backend/data/role_descriptions.json`：role_description / core_skills / vs_neighbor / narrative / who_fits / who_doesnt 六字段），不用 LLM。新建 `backend/scripts/export_role_profiles.py` 纯文件 merge → `frontend/public/data/role-profiles.json`，加进 `weekly-refresh.yml` export 链
- **列表 + 详情双层** —— 列表页国内/海外按钮切换（`useState` + Tailwind，**未用** Base UI Tabs primitive，原因：Base UI 没 CSS transition 时不 unmount inactive panel，会两组卡片叠在一起）；详情页 server component + `generateStaticParams` 预渲染 27 路径，Recharts 客户端子组件渲 Required vs Preferred bar
- **首页第三轨入口** —— 双轨入口卡升级到三轨：叙事手册 + 按岗位探索 + 数据看板。顶 nav 新增 `/roles`
- **narrative 数字校对** —— 全部 27 条 narrative 中的数字 vs 实际 role aggregate 数据交叉校验，修了 6 处口径不一致（ai_engineer / product_manager 把全国中位当成岗位中位；sde / ml_scientist / ml_engineer 用了模糊 "65k+"；intl autonomous 取整精度）

### v0.10 进展（2026-04-30）
- **云端化** —— 数据库迁 Supabase Postgres 17（ap-southeast-2），本地 docker-compose 仍是 dev 环境。`config.py` 加 `AH_DATABASE_URL_OVERRIDE` 字段一行切换
- **GitHub Actions 周更** —— `weekly-refresh.yml` 每周日 02:00 UTC export+deploy（read-only，3min 跑完）；`collect-data.yml` 用户手动触发可选 hn / github / tencent / all
- **腾讯 vendor collector** —— `careers.tencent.com` 公开 JSON API，1,049 条 AI 岗（domestic 1024 + intl 25），8 个关键词去重。`backfill_tencent_metadata.py` 解析 raw_content 自填 location/market/industry/experience（无 LLM 成本）
- **完整 role_type backfill** —— 累计 rule-based 处理 2,873 条原 NULL：扩展 vendor 公司白名单（智谱/MiniMax/Moonshot/百川 + 腾讯 added later）+ AI vendor product regex（MaaS/GLM/大模型/推理）+ NON_AI_ENGINEERING 反向规则。labeled fraction 从 69% 提升到 92%。Manual SQL 修 7 条 corner case
- **AI native 公司白名单** —— `is_ai_native_company()` + `AI_NATIVE_VENDOR_PLATFORMS` 跳过 ai_augmented 误判（智谱 「量化算法」 = model quantization 不是金融量化）

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
- **观察期** —— 等 aijobfit 业务方 + 就业班业务人员实际跑过 v0.12 五轨（含 /professions 8 传统职业 + /learn 28 篇课本）后看数据消费有没有新缺口；业务方读完 /learn 反馈 OK 再 close #39
- **issue #18 P1**（业务方场景延伸）—— 跨角色对比视图（`/roles/compare?a=algorithm&b=ai_engineer`）+ 每角色 `business_narrative`（如何从传统职业转 / 难度 / 缺什么技能）与就业班课程衔接。**前置：业务方实际用 P0 + /learn 反馈后再决定要不要补**
- **issue #18 P2**（数据质量）—— `other` 混合簇拆细：domestic 2121 + intl 1443 当前是「未匹配」剩余。下一轮 LLM 聚类时扩 `DOMESTIC_ROLES` / `INTERNATIONAL_ROLES` taxonomy
- **OpenRouter 余额恢复后** —— `insights.json` / `report.json` 可切回 LLM 自动生成（v0.9-0.12 是手写）
- **#12 国内剩 5 家大厂** —— 阿里 / 百度 / 商汤 / 阶跃 / 零一万物。腾讯（公开 API）+ 字节（公开 API + CDP re-enrich）已完成，其余多为 SPA 反爬重，需 Playwright per-vendor。**前置：业务有需求才做**
- **基础设施** —— skill_aliases 持续扩展、Chrome 扩展完善、跨 region DB 慢可考虑 Supabase region 迁 us-west（如果 cron 时间敏感）
- **#34 Boss/Liepin 大规模采集** —— 反爬升级到浏览器指纹 + 行为检测双层，事实上不可行。需要重新设计采集策略（如订阅式付费源 / 招聘网站合作 / 公开 ATS 接入）

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

## Content（两类，都在 content/ 下）

### 自媒体内容 `content/{序号}-{选题slug}/`
- 每个选题下有 `thread.md` / `xiaohongshu.md` / `xhs-cards.md` / `wechat.md` / `assets/` / `xhs-output/`
- **状态（2026-05-01）**：7 篇全部交付完成 — 0 期引流 2 篇（#01 35 岁危机 / #02 国内外两种语言）+ 主线 5 篇（#03-#07，对应 narrative `/narrative/p1~p5`）。所有 thread 经 `/dbs-content` + `/dbs-hook` skill 同标准审核
- 7 篇引流话术全部差异化（避免连读重复）：年限 / 想去市场 / AI 用法 / 期望薪资 / SWE+客户经验 / 想去城市 / 目标公司清单 — 详见 `content/README.md`
- 数据洞察驱动内容，工具是内容的售后（不单独推广工具）
- 发布顺序：X thread 先发试水（工作日 9-10AM）→ 24h → 小红书图文（午 12-13）→ 公众号长文（晚 8-9）
- 引流闭环：评论留具体信息（按各篇主题）→ aijobfit 免费诊断 → 撞遮罩 → 加小助理微信 → 激活码 `AIJOB-2026`
- 待办：用户发布 #1 #2（issue #1 #2 仍 open）。**发布前不写新内容**，看反馈再决定 8+ 篇方向
- 工作流详见 `content/README.md`（含 8 步标准化创作流程：拉数据 → thread v1 → /dbs-content 审核 → v2 → 同步 markdown → 图 → md2red → commit）

### 课本内容 `content/learn/{lv1,lv2,lv3}/*.md`（v0.12 B3+C）
- **状态（2026-05-13）**：28 篇全部交付（Lv1 5 + Lv2 16 + Lv3 7），超目标 20。等业务方读完反馈 OK 再 close #39
- 每篇 frontmatter：title / order / summary / reading_minutes / linked_roles（如有）/ linked_professions（如有）
- 写作约定：每篇用不同生活类比开头 + 必带「不适合谁」reality check + 真实数据带 sample 量 + 诚实劝退（不只 welcoming）
- **不需要图 / 不需要 components**，只 .md，frontend SSG 自动渲染 `/learn/[level]/[slug]`
- 详细写作 spec 见 `docs/agent-hunt/v012-c-handoff.md`
