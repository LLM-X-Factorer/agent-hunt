# Agent Hunt

> 用数据告诉你，AI 岗位到底需要什么 — 国内外全平台覆盖，跨市场 × 跨行业对比分析。

**在线体验：https://agent-hunt.pages.dev**

## 这是什么

Agent Hunt 采集国内外主流招聘平台的 AI 相关岗位 JD，通过 Gemini API 进行结构化解析（含行业分类），生成**技能图谱**、**跨市场对比**、**行业 AI 渗透分析**和**个性化学习路径**。

不靠猜，靠数据。不看单一市场，看全球。不看单一行业，看全景。

## 为什么需要这个

AI 正在渗透每一个行业，但：
- 国内和国际市场对 AI 岗位的定义差异巨大
- 传统行业（金融、医疗、制造、汽车）的 AI 交叉岗位正在快速增长，但信息分散
- 求职者不知道该学什么，不知道哪个行业的 AI 机会最大

Agent Hunt 解决的问题：**用真实 JD 数据，消除信息差**。

## 核心功能

### 多平台数据采集
从国内外 10+ 招聘平台采集 AI Agent 相关 JD，统一解析为标准化格式。

| 市场 | 平台 | 优先级 |
|---|---|---|
| 国内 | Boss直聘、猎聘 | Tier 1 |
| 国际 | LinkedIn、Indeed | Tier 1 |
| 国内 | 拉勾、脉脉 | Tier 2 |
| 国际 | Wellfound、Glassdoor | Tier 2 |
| 远程 | RemoteOK、We Work Remotely | Tier 3 |

### AI 驱动的 JD 解析
- Gemini API 驱动的中英双语 JD 结构化解析
- 自动提取：技能要求、薪资范围、经验门槛、工作模式
- 多语言技能归一化（大模型 = LLM、朗链 = LangChain）

### 跨市场对比分析（核心差异化）
- **技能差异**：国内 vs 国际，哪些技能是共通的？哪些是各自独有的？
- **薪资对标**：同等级岗位在不同市场的薪资对比（含汇率换算）
- **岗位定义**：国内的"全栈型" vs 国际的"专精型"
- **Remote 机会**：不同市场的远程工作比例

### 技能图谱
- 高频技能排行（按平台 / 按市场）
- 技能关联网络（哪些技能经常一起出现）
- 技能趋势追踪

### 个性化学习路径
- 输入你的现有技能
- 选择目标市场（国内 / 国际 / 全球）
- 生成技能差距分析 + 推荐学习顺序 + 资源链接

## 国内就业市场分析

> 基于 1513 条国内 JD 的岗位聚类分析。数据来源：Boss直聘、猎聘、拉勾。
> 按 job title 关键词聚类为 14 种典型角色，覆盖率 82%。

### 国内岗位全景

| 角色 | 岗位数 | 薪资中位数 | P25-P75 | 经验中位数 | 主要行业 |
|------|:-----:|:---------:|:-------:|:--------:|---------|
| AI/LLM 工程师 | 350 | ¥32,500 | ¥20k-50k | 3 年 | 互联网 · 制造 · 汽车 |
| AI 产品经理 | 233 | ¥32,500 | ¥22.5k-45k | 3 年 | 互联网 · 制造 · 金融 |
| 算法工程师/研究员 | 86 | ¥50,000 | ¥30k-65k | 3 年 | 金融 · 互联网 · 医疗 |
| AI 管理/战略 | 84 | ¥56,250 | ¥37.5k-85k | 5 年 | 教育 · 医疗 · 互联网 |
| AI 运营/训练师 | 83 | ¥23,000 | ¥15k-32.5k | 3 年 | 互联网 · 零售 · 金融 |
| 自动驾驶/智能座舱 | 83 | ¥26,250 | ¥18.5k-40k | 5 年 | 汽车 · 互联网 · 制造 |
| 智能制造/工业AI | 82 | ¥39,000 | ¥22.5k-60k | 5 年 | 制造 · 互联网 · 汽车 |
| AI 销售/商务 | 71 | ¥22,500 | ¥13.5k-40k | 3 年 | 互联网 · 医疗 · 制造 |
| AI 转型/咨询 | 64 | ¥35,000 | ¥12.5k-55k | 5 年 | 咨询 · 制造 · 零售 |
| AI 教育 | 30 | ¥14,750 | ¥8k-30k | 1 年 | 教育 · 互联网 · 政府 |
| 数据分析/数据科学 | 24 | ¥30,000 | ¥12.5k-65k | 1 年 | 金融 · 互联网 · 医疗 |
| AI 风控/合规 | 18 | ¥22,500 | ¥12.5k-45k | 3 年 | 金融 · 互联网 · 咨询 |

### 国内核心角色技能画像

#### 1. AI/LLM 工程师（350 岗，国内最大需求）

> 典型 title：LLM/AI Agent 开发工程师、AI Agent 平台研发工程师、AI 全栈开发工程师

| 必备技能 (Required) | 出现次数 | 加分技能 (Preferred) |
|-------------------|:------:|-------------------|
| LLM | 110 | Semantic Kernel |
| Agent Architecture | 54 | MCP |
| Python | 24 | Reinforcement Learning |
| RAG | 18 | |
| Java | 14 | |
| LangChain | 10 | |
| Go | 8 | |
| Prompt Engineering | 8 | |
| Multimodal AI | 8 | |
| SQL | 7 | |

- **薪资**：¥20k-50k（中位数 ¥32,500）
- **学历**：本科 68% / 硕士 19% / 不限 13%
- **画像**：LLM + Agent + RAG 三件套为核心，Python 是底层必备，Java/Go 用于工程化落地。这是国内 AI 岗位的"标准答案"。

#### 2. 算法工程师/研究员（86 岗，薪资最高的技术岗）

> 典型 title：AI 推荐算法工程师、算法专家-金融大模型、机器人多模态大模型算法工程师

| 必备技能 (Required) | 出现次数 | 加分技能 (Preferred) |
|-------------------|:------:|-------------------|
| LLM | 19 | Generative AI |
| Machine Learning | 4 | |
| Data Analysis | 3 | |
| Python | 3 | |
| Deep Learning | 2 | |
| SQL | 2 | |

- **薪资**：¥30k-65k（中位数 ¥50,000）— 比 AI 工程师高 54%
- **学历**：硕士 45% / 本科 38% / 博士 9% — 学历门槛最高
- **画像**：偏研究型，需要 ML/DL 基础功底。金融和医疗是主要雇主，对数学和统计能力有隐性要求。

#### 3. AI 产品经理（233 岗，第二大需求）

> 典型 title：AI 产品经理、AIGC 产品经理、智能客服产品经理、AI Agent 产品经理

| 必备技能 (Required) | 出现次数 | 加分技能 (Preferred) |
|-------------------|:------:|-------------------|
| LLM | 15 | RAG |
| Agent Architecture | 9 | Knowledge Graph |
| Computer Vision | 2 | |
| Function Calling | 1 | |

- **薪资**：¥22.5k-45k（中位数 ¥32,500）
- **学历**：本科 83% / 不限 12%
- **画像**：技能要求远低于工程岗，核心是理解 LLM 和 Agent 的能力边界。技术深度不是重点，产品思维和行业认知才是。

#### 4. AI 运营/训练师（83 岗，入门门槛最低）

> 典型 title：AIGC 产品运营、智能客服训练师、AI 运营经理

- **薪资**：¥15k-32.5k（中位数 ¥23,000）
- **学历**：本科 77% / 不限 20%
- **画像**：Prompt 编写、数据标注、效果优化。不需要编程能力，适合非技术背景入门 AI 行业。

#### 5. AI 管理/战略（84 岗，薪资天花板最高）

- **薪资**：¥37.5k-85k（中位数 ¥56,250）
- **经验**：5 年起步
- **画像**：需要行业经验 + AI 认知的复合能力，纯技术背景不够，需要管理和商业判断力。

#### 6. 行业交叉岗位

| 角色 | 岗位数 | 薪资中位数 | 核心差异 |
|------|:-----:|:---------:|---------|
| 自动驾驶/智能座舱 | 83 | ¥26,250 | 嵌入式 + 测试为主，AI 技能要求反而不高 |
| 智能制造/工业AI | 82 | ¥39,000 | 薪资高于预期，需要工业领域知识 |
| AI 风控/合规 | 18 | ¥22,500 | SQL + Python + 数据分析三件套，金融行业特色 |
| 医疗AI | 9 | ¥10,000 | 薪资偏低，但处于早期阶段 |

### 国内市场核心发现

1. **AI 工程师和产品经理占据半壁江山**（350 + 233 = 583 岗，占 39%），这两个方向是最稳妥的选择
2. **算法岗薪资溢价 54%**（中位数 ¥50k vs AI 工程师 ¥32.5k），但学历门槛最高（45% 要求硕士）
3. **非技术岗位机会充足**：产品经理（233）、运营（83）、销售（71）、转型咨询（64）加起来占 30%
4. **行业决定技能方向**：金融偏数据分析 + SQL，汽车偏嵌入式，制造偏工业 AI，不要只看"互联网 AI"
5. **薪资分化严重**：管理层中位数 ¥56k vs 运营/教育中位数 ¥14-23k，同样是 AI 行业差距 3 倍

---

## 海外就业市场分析

> 基于 507 条海外 JD 的岗位聚类分析。数据来源：LinkedIn、Indeed。
> 按 job title 关键词聚类为 11 种典型角色，覆盖率 84%。

### 海外岗位全景

| 角色 | 岗位数 | 月薪中位数(¥) | P25-P75 | 经验中位数 | 主要行业 |
|------|:-----:|:------------:|:-------:|:--------:|---------|
| ML/AI Engineer | 75 | ¥100,286 | ¥88k-125k | 4 年 | 互联网 · 金融 · 传媒 |
| Software Engineer | 63 | ¥97,702 | ¥84k-111k | 5 年 | 互联网 · 咨询 · 制造 |
| ML Scientist / Researcher | 61 | ¥117,812 | ¥91k-143k | 3 年 | 互联网 · 医疗 · 汽车 |
| Product Manager | 56 | ¥118,896 | ¥105k-125k | 5 年 | 互联网 · 医疗 · 金融 |
| Engineering Leadership | 55 | ¥135,905 | ¥112k-173k | 10 年 | 医疗 · 互联网 · 金融 |
| Autonomous Vehicles | 20 | ¥38,364 | ¥35k-44k | 3 年 | 汽车 |
| Finance / Operations | 17 | ¥85,803 | ¥86k-114k | 6 年 | 医疗 · 金融 · 互联网 |
| Solutions Architect | 14 | ¥99,681 | ¥94k-111k | 6 年 | 互联网 · 汽车 · 制造 |
| AI Sales / BD | 11 | ¥137,500 | ¥104k-146k | 7 年 | 互联网 · 医疗 |
| Intern / New Grad | 10 | ¥58,424 | ¥44k-64k | 0 年 | 制造 · 汽车 · 金融 |
| Data Scientist / Analyst | 9 | ¥113,281 | ¥82k-142k | 6 年 | 互联网 · 咨询 · 医疗 |

### 海外核心角色技能画像

#### 1. ML/AI Engineer（75 岗，海外最大 AI 技术岗）

> 典型 title：AI Engineer、AI/ML Engineer、Python AI/ML Developer、Senior ML Engineer

| 必备技能 (Required) | 出现次数 | 加分技能 (Preferred) |
|-------------------|:------:|-------------------|
| Python | 44 | Multimodal AI |
| LLM | 27 | |
| Machine Learning | 19 | |
| Prompt Engineering | 17 | |
| SQL | 16 | |
| PyTorch | 15 | |

- **薪资**：¥88k-125k（中位数 ¥100,286）
- **学历**：本科 40% / 不限 15% / 不指定 31%
- **vs 国内 AI 工程师**：海外要求 Python(59%) + ML(25%) + PyTorch(20%) 作为基础，国内只看 LLM + Agent。技术栈更深、更广。

#### 2. ML Scientist / Researcher（61 岗，薪资最高的技术岗）

> 典型 title：Applied Scientist、Machine Learning Researcher、Senior Applied Science Manager

| 必备技能 (Required) | 出现次数 | 加分技能 (Preferred) |
|-------------------|:------:|-------------------|
| Python | 37 | React |
| Machine Learning | 22 | TypeScript |
| SQL | 18 | Next.js |
| Deep Learning | 17 | DevOps |
| LLM | 13 | |
| C++ | 11 | |

- **薪资**：¥91k-143k（中位数 ¥117,812）
- **学历**：硕士 34% / 本科 23% / 博士 20% — 学历要求最高
- **画像**：需要扎实的 ML/DL 理论 + Python + C++ 工程能力。Amazon "Applied Scientist" 系列是典型代表。

#### 3. Software Engineer（63 岗，技能要求最全面）

> 典型 title：Full Stack Engineer、Software Development Engineer、Senior Software Engineer

| 必备技能 (Required) | 出现次数 | 加分技能 (Preferred) |
|-------------------|:------:|-------------------|
| Python | 35 | Kubernetes |
| Java | 35 | Docker |
| C# | 28 | Anthropic API |
| AWS | 25 | |
| SQL | 24 | |
| React | 23 | |

- **薪资**：¥84k-111k（中位数 ¥97,702）
- **画像**：不是纯 AI 岗，而是需要 AI 能力的全栈工程师。多语言（Python + Java + C#）+ 云平台（AWS）+ 前端（React）全要会。

#### 4. Product Manager（56 岗，薪资超过多数工程岗）

> 典型 title：Product Manager、Senior Product Manager、Product Operations Manager

| 必备技能 (Required) | 出现次数 | 加分技能 (Preferred) |
|-------------------|:------:|-------------------|
| Data Analysis | 22 | Python |
| Generative AI | 8 | Java |
| LLM | 7 | Microservices |
| Prompt Engineering | 4 | Kubernetes |
| RAG | 3 | |

- **薪资**：¥105k-125k（中位数 ¥118,896）— 比 ML Engineer 还高
- **vs 国内 AI PM**：海外 PM 核心要求是 Data Analysis（22 次），国内 PM 核心是理解 LLM（15 次）。海外 PM 更偏数据驱动，国内 PM 更偏技术理解。

#### 5. Solutions Architect（14 岗，Agent 框架要求最全面）

> 典型 title：Solutions Architect、Customer Engineer、Principal AI/ML Architect

| 必备技能 (Required) | 出现次数 |
|-------------------|:------:|
| RAG | 5 |
| JavaScript | 5 |
| AWS | 4 |
| LangGraph | 4 |
| CrewAI | 4 |
| AutoGen | 4 |

- **画像**：唯一一个同时要求 LangGraph + CrewAI + AutoGen 三大 Agent 框架的角色。需要能将 AI 能力整合到企业架构中。

#### 6. Intern / New Grad（10 岗，入门参考）

| 必备技能 (Required) | 加分技能 (Preferred) |
|-------------------|-------------------|
| Python(5)、SQL(3)、C++(2) | Git(2)、TensorFlow(2)、Azure(1) |

- **薪资**：¥44k-64k（中位数 ¥58,424）— 应届即可拿到国内资深工程师的水平
- **画像**：Python + SQL 是起步线，ML 基础 + 一个 DL 框架是加分项

### 海外市场核心发现

1. **ML Scientist 薪资最高**（中位数 ¥117k），但学历门槛也最高（54% 硕士/博士）
2. **Product Manager 薪资超过工程师**（¥119k vs ML Engineer ¥100k），Data Analysis 是 PM 的第一技能
3. **Software Engineer ≠ AI Engineer**：SDE 需要多语言（Python + Java + C#）+ 云 + 前端，是"会 AI 的全栈"而非"专做 AI"
4. **海外应届薪资 ¥58k**，约等于国内 AI 管理层中位数（¥56k）
5. **Solutions Architect 是 Agent 生态的集大成者**：同时要求 3 个 Agent 框架 + 云平台 + 全栈能力
6. **AI Sales 薪资 ¥137k**，仅次于 Engineering Leadership，非技术路线的天花板

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) · Celery |
| 前端 | Next.js 16 · Tailwind · shadcn/ui · Recharts · Cloudflare Pages |
| AI | Gemini API (gemini-2.5-flash) · pgvector · 多语言技能归一化 |
| 数据采集 | Playwright · Chrome Extension · 策略模式 + 注册表模式 |
| 基础设施 | PostgreSQL 16 · Redis 7 · Docker Compose |

## 项目结构

```
agent-hunt/
├── backend/                    # FastAPI 后端（已实现）
│   ├── app/
│   │   ├── api/v1/             # REST API 路由（jobs, platforms, skills, analysis）
│   │   ├── collectors/         # 多平台数据采集器（策略模式 + 注册表）
│   │   ├── models/             # SQLAlchemy 数据模型（Job, Platform, Skill）
│   │   ├── schemas/            # Pydantic 请求/响应 schema
│   │   ├── services/           # 业务逻辑（JD解析、技能提取、跨市场分析）
│   │   ├── tasks/              # Celery 异步任务
│   │   ├── config.py           # pydantic-settings 配置（AH_ 前缀）
│   │   ├── database.py         # 异步数据库引擎（asyncpg）
│   │   └── main.py             # FastAPI 入口（启动时自动加载种子数据）
│   ├── alembic/                # 数据库迁移
│   ├── tests/                  # pytest + pytest-asyncio
│   └── pyproject.toml
├── frontend/                   # Next.js 前端（已部署到 Cloudflare Pages）
│   ├── src/app/                # 页面（总览、技能图谱、薪资分析、市场差异、岗位画像）
│   ├── src/components/         # UI 组件（shadcn/ui + InsightCard）
│   ├── src/lib/                # API 客户端 + 标签映射
│   └── public/data/            # 预导出的静态 JSON 数据
├── extension/                  # Chrome 浏览器插件（已实现 4 平台内容脚本）
│   ├── content_scripts/        # 各平台 JD 提取脚本
│   └── popup/                  # 插件弹窗 UI
├── data/                       # 种子数据 + 配置
│   ├── seed_platforms.json     # 10 个平台元数据
│   ├── seed_skills.json        # 68 个 AI 技能（中英双语别名）
│   ├── skill_aliases.json      # 技能同义词映射表（210+ 条）
│   └── search_keywords.json    # 跨行业采集关键词矩阵（50+ 关键词）
├── content/                    # 自媒体内容（数据洞察驱动）
│   ├── README.md               # 选题队列 + 发布流程
│   └── {序号}-{选题}/           # 每个选题：thread.md / xiaohongshu.md / wechat.md / assets/
├── docs/                       # 文档（按主题分类）
│   ├── README.md                          # 文档索引
│   ├── agent-hunt/                        # 平台技术文档
│   │   └── domestic-scraping-strategy.md  # 国内平台爬虫技术方案
│   ├── employment-course/                 # 就业班产品设计 v1.0（已完成）
│   │   ├── 00-产品设计-v1.md              # 产品总纲（11 节）
│   │   ├── 01-竞品扫描-2026-04-21.md
│   │   ├── 02-9.9诊断报告模板.md
│   │   └── 03-首期招生页.md
│   └── legacy/                            # 旧课程归档
├── docker-compose.yml          # PostgreSQL 16 (pgvector) + Redis 7
└── .env.example
```

## 数据模型

三个核心表：

- **platforms** — 招聘平台元数据（市场、Tier、采集难度、数据质量等）
- **jobs** — JD 数据（原始文本 + LLM 解析后的结构化字段），通过 `(platform_id, platform_job_id)` 联合唯一约束去重
- **skills** — 技能分类（含 JSONB 多语言别名、按市场统计计数）

## 快速开始

```bash
git clone <repo-url>
cd agent-hunt

# 1. 启动基础设施
cp .env.example .env          # 填入 Gemini API Key
docker compose up -d

# 2. 安装后端依赖
cd backend && uv venv --python 3.11 .venv && uv pip install -e ".[dev]"

# 3. 运行数据库迁移
.venv/bin/alembic upgrade head

# 4. 启动后端（自动加载种子平台和技能数据）
.venv/bin/uvicorn app.main:app --reload

# 5. 前端（可选，已部署到 Cloudflare Pages）
cd ../frontend && npm install && npm run dev
```

启动后访问 http://localhost:8000/docs 查看 Swagger API 文档。

### API 端点

```
GET  /health                              — 健康检查

# Jobs
POST /api/v1/jobs/import                  — 导入单条 JD
POST /api/v1/jobs/import/batch            — 批量导入（最多 100 条）
POST /api/v1/jobs/collect                 — 触发平台采集（采集 → 导入 → 自动解析）
POST /api/v1/jobs/parse/batch             — 批量 Gemini 解析
GET  /api/v1/jobs                         — 职位列表（分页 + 筛选）
GET  /api/v1/jobs/{id}                    — 职位详情
POST /api/v1/jobs/{id}/parse              — 单条解析

# Skills
GET  /api/v1/skills                       — 技能列表（含国内/国际计数）
POST /api/v1/skills/normalize             — 触发技能归一化（采集新数据后运行）
GET  /api/v1/skills/unmatched             — 未匹配的原始技能（用于扩展 aliases）

# Analysis
GET  /api/v1/analysis/salary/distribution — 薪资分布直方图
GET  /api/v1/analysis/salary/by-skill     — 各技能关联薪资
GET  /api/v1/analysis/salary/by-experience — 按经验分段薪资
GET  /api/v1/analysis/salary/by-platform  — 按平台薪资
GET  /api/v1/analysis/cross-market/overview   — 国内 vs 国际总览
GET  /api/v1/analysis/cross-market/skills     — 各市场 Top 技能
GET  /api/v1/analysis/cross-market/skill-gaps — 技能需求差异排名
GET  /api/v1/analysis/cooccurrence            — 技能共现分析
GET  /api/v1/analysis/industry/overview       — 行业 AI 渗透总览
GET  /api/v1/analysis/industry/salary         — 各行业 AI 岗位薪资

# Platforms
GET  /api/v1/platforms                    — 平台列表
GET  /api/v1/platforms/{id}               — 平台详情
```

## 数据采集策略

数据采集是本项目的**核心硬需求**。经过调研，各平台均无官方 API 直接提供 JD 批量检索，必须通过多种技术手段攻克。

> 详细技术方案见 [docs/domestic-scraping-strategy.md](docs/domestic-scraping-strategy.md)

### 国内平台（必须攻克）

国内平台是数据源的重中之重，采用**多路并进、逐层升级**策略：

```
Layer 0: 手动导入 JSON（保底）
Layer 1: Chrome 浏览器插件（浏览时自动提取）
Layer 2: Playwright 浏览器自动化（模拟真人操作）
Layer 3: API 逆向 + 请求模拟（高效批量）
Layer 4: 移动端 API 抓包（反爬可能更弱）
```

| 平台 | 主力方案 | 反爬难度 | 关键挑战 | 已验证的开源参考 |
|---|---|---|---|---|
| **Boss直聘** | Playwright + Cookie 持久化 | 最高 | 薪资字体加密、设备指纹、登录墙 | [auto-zhipin](https://github.com/ufownl/auto-zhipin) (Playwright) |
| **猎聘** | Playwright + 页面等待 | 中高 | 动态参数、搜索需手动点击 | [job-hunting-tampermonkey](https://github.com/lastsunday/job-hunting-tampermonkey) |
| **拉勾** | Playwright / POST API 模拟 | 中 | 登录墙、Cookie 依赖 | [ECommerceCrawlers](https://github.com/DropsDevopsOrg/ECommerceCrawlers) |

### 国际平台

| 平台 | 主力方案 | 备注 |
|---|---|---|
| LinkedIn / Indeed / Glassdoor | [JobSpy](https://github.com/speedyapply/JobSpy) (Python) | 同时抓取多平台，输出 CSV |
| 补充数据 | [Adzuna API](https://developer.adzuna.com/) | 多国职位聚合 API |

### 合规原则

- 仅采集公开可访问的职位信息
- 不存储任何个人信息（HR 姓名、联系方式等）
- 数据仅用于统计分析，不原文展示他人内容
- 自动化采集设置合理延迟（3-8 秒 / 请求）
- 单次会话限量（50-100 条）

## 项目状态

积极开发中 — v0.7 已上线（数据 + 解析提速），就业班产品设计完成，衍生产品 aijobfit 已 spin off

**在线体验：https://agent-hunt.pages.dev**（v0.7 数据待重新部署）

| Phase | 内容 | 状态 |
|---|---|---|
| 1 | 数据采集管道 + 5 平台采集器（LinkedIn/Indeed/猎聘/Boss直聘/拉勾） | **已完成** ✅ |
| 2 | 跨市场分析引擎（技能归一化、薪资分析、技能共现） | **已完成** ✅ |
| 3 | 前端 7 页 + AI 洞察 + 岗位画像 + 学习路径 | **已完成** ✅ |
| 4 | 行业维度扩展（13 行业分类 + 关键词矩阵 + 行业分析页面） | **已完成** ✅ |
| 5 | AI 洞察报告 + 跨行业数据扩充（2370 条 JD） | **已完成** ✅ |
| 6 | 角色聚类分析 + 分市场独立分析 + SCI 评分模型 | **已完成** ✅ |
| 7 | 持续增强（aliases 扩展、Chrome 扩展、Celery 定时采集、用户系统） | 待开始 |
| v0.7 | JD 解析提速 8 倍（async + 并发）+ AIGC 关键词扩充 + 712 条解析完 | **已完成** ✅ |
| — | 就业班产品设计 v1.0（4 主线矩阵 + 12 周陪跑 + 30×3800 商业模型） | **已完成** ✅ |
| — | 衍生产品 [aijobfit](https://github.com/LLM-X-Factorer/aijobfit)（免费 AI 求职定位诊断 + 加微信漏斗） | **v0.1 已上线** 🚀 |
| — | 内容运营：基于数据洞察的自媒体内容（X/小红书/公众号） | **进行中** 🚀 |

### 衍生产品：AIJobFit

免费 AI 求职定位诊断工具，是本平台数据的最终用户产品形态。独立项目维护，已上线。

- **生产**：https://aijobfit.llmxfactor.cloud
- **GitHub**：[LLM-X-Factorer/aijobfit](https://github.com/LLM-X-Factorer/aijobfit)
- **架构**：Next.js 16 + 远程 fetch agent-hunt 数据
- **关系**：本项目（agent-hunt）= 数据生产方，aijobfit = 数据消费方，无代码依赖
- **产品定位（2026-04-22 pivot）**：从原计划 9.9 元付费 → **永久免费 + 加微信漏斗**。前 3 节开放，后 4 节遮罩，加小助理微信拿统一激活码 `AIJOB-2026` 解锁。商业化（1V1 / 社群 / 课程）在产品外独立运营，与 aijobfit 仓库解耦
- **v0.1 已交付**：14 角色匹配（含稀疏角色置信度惩罚 + fallback 锚点 hoist）/ 7 节报告 / 微信漏斗（遮罩 + 激活码） / 移动端断点重排 / 微信生态（方形 OG + WebView 复制链接降级 + 长按 QR 识别） / 漏斗埋点（form_submit / report_view / mask_see / code_enter_*） / 1080×1920 分享海报 / Docker + Nginx 部署 / GitHub Actions CI / 运营手册 / 真 QR 替换（aijobfit#12 已解，2026-04-28 生产端到端浏览器测试通过）
- **剩余 open issue**（全部为非代码运营任务）：微信实机全链路测试（aijobfit#13） / 漏斗埋点观察期 + 门槛调优决策（aijobfit#14）

### Phase 1 完成总结

**基础设施 ✅**
- [x] 项目骨架 + Docker Compose（PostgreSQL 16 + pgvector + Redis 7）
- [x] 数据模型（Platform / Job / Skill）+ Alembic 迁移
- [x] 种子数据（50 技能 + 100+ 别名映射 + 10 个平台元数据）
- [x] 配置管理（pydantic-settings + .env.example）
- [x] 手动导入服务（JSON 导入 + 去重）
- [x] JD 解析服务（Gemini API 中英双语结构化解析）
- [x] REST API（import / collect / list / detail / parse / batch-parse / platforms）
- [x] BaseCollector 抽象类 + CollectorRegistry 注册表
- [x] 采集 API 端点（`POST /api/v1/jobs/collect`，采集 → 导入 → 自动解析）
- [x] 批量解析端点（`POST /api/v1/jobs/parse/batch`）

**国际平台 ✅**
- [x] JobSpy 集成（LinkedIn / Indeed 采集器）— 105+ 条

**国内平台 ✅**
- [x] 猎聘 Playwright 采集器（无需登录，单页 42 条含 JD 详情）
- [x] Boss直聘 Playwright 采集器（Cookie + 薪资字体解密）
- [x] 拉勾 Playwright 采集器（Cookie + 滑块验证绕过）
- [x] Cookie 导出工具（`scripts/export_cookies.py`）
- [x] 全部 JD 已 Gemini 结构化解析（含行业分类）

### Phase 2 完成总结

**技能归一化 ✅**
- [x] SkillExtractor（`skill_aliases.json` 180+ 条映射 → 67 个标准技能）
- [x] 归一化端点 `POST /skills/normalize` + 未匹配技能查看 `GET /skills/unmatched`

**薪资分析 ✅**
- [x] 薪资分布直方图（按市场/平台筛选）
- [x] 按技能关联薪资（哪些技能薪资最高）
- [x] 按经验/平台分段薪资

**跨市场对比 ✅**
- [x] 国内 vs 国际总览（薪资、工作模式、学历、经验分布）
- [x] 各市场 Top N 技能排名
- [x] 技能需求差异排名（skill gap analysis）

**技能共现分析 ✅**
- [x] 技能共现矩阵 + Top pairs（含 Jaccard 系数归一化）

### Phase 3 完成总结

**前端 Dashboard ✅** （Next.js 16 + Tailwind + shadcn/ui + Recharts）
- [x] 5 个页面：总览、技能图谱、薪资分析、市场差异、岗位画像
- [x] 中文界面 + Cloudflare Pages 静态部署
- [x] Gemini AI 生成的市场洞察（每页顶部）
- [x] JD 样本展示（点击技能查看真实 JD 摘要）
- [x] 3 个岗位画像（国内/国际/远程）
- [x] 4 条学习路径推荐（Python 转型、前端转型、应届生、出海）
- [x] 静态数据生成脚本（`scripts/generate_insights.py`）

### Phase 4 完成总结

**行业维度扩展 ✅**
- [x] Job 模型新增 `industry` 字段 + Alembic 迁移 002
- [x] Gemini 解析自动识别 12 个行业（互联网/金融/医疗/制造/汽车/零售/教育/媒体/咨询/能源/通信/政府）
- [x] 499 条 JD 重新解析并标注行业
- [x] 行业分析 API 端点（`/analysis/industry/overview`、`/analysis/industry/salary`）
- [x] 前端行业分析页面（行业岗位分布图 + 薪资对比 + 行业卡片）
- [x] 跨行业采集关键词矩阵（`data/search_keywords.json`，50+ 关键词 × 10 分类）
- [x] 批量采集脚本（`scripts/batch_collect.py`）

### Phase 5 完成总结

**AI 洞察报告 + 数据扩充 ✅**
- [x] 跨行业关键词矩阵采集（50+ 关键词），数据从 521 → 2370 条 JD
- [x] AI 市场洞察报告（`/report` 页面，Gemini 生成 5 个章节）
  - 全景概览、行业深度分析、跨界求职指南、趋势判断、核心发现
- [x] 报告生成脚本（`scripts/generate_report.py`）
- [x] 前端 8 个页面全部上线

### Phase 6 完成总结

**角色聚类分析 + 分市场独立分析 ✅**
- [x] 岗位角色聚类（`scripts/analyze_roles.py`）：按 job title 关键词聚类为典型角色
  - 国内 14 种角色（AI/LLM 工程师、AI 产品经理、算法工程师等）
  - 海外 11 种角色（ML/AI Engineer、Software Engineer、ML Scientist 等）
- [x] 每种角色包含：必备/加分技能、薪资分布、学历/经验要求、行业分布
- [x] 分市场独立分析：国内/海外技能排名、行业矩阵、共现网络完全分开计算
- [x] SCI（Skill Criticality Index）评分模型：综合频率、薪资溢价、增长趋势的技能关键度指数
- [x] 分市场数据导出（`scripts/export_market_data.py`）
- [x] README 重构为角色维度分析，从"看技能"升级为"看角色 × 技能 × 行业"

## Contributing

欢迎贡献！特别欢迎以下方向：
- 新平台采集器的实现
- 种子 JD 数据的补充（`data/sample_jds/`）
- 技能同义词映射的完善（`data/skill_aliases.json`）

## License

MIT
