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

## 就业市场技能分析

> 基于 1542 条已解析 JD（国内 1213 条 · 海外 329 条），覆盖 13 个行业、5 个招聘平台。

### 国内市场技能需求 Top 15

国内 JD 高度集中在大模型应用层，LLM 一项占比超 14%，其余技能均不到 6%。

| 排名 | 技能 | 出现次数 | 占比 | 特点 |
|:---:|------|:------:|:---:|------|
| 1 | Large Language Models | 174 | 14.3% | 绝对核心，几乎所有 AI 岗必提 |
| 2 | Agent Architecture | 70 | 5.8% | 国内 Agent 热度显著高于海外占比 |
| 3 | Python | 38 | 3.1% | 国内 JD 常隐含不单列，实际刚需 |
| 4 | RAG | 22 | 1.8% | 国内落地最多的 LLM 应用模式 |
| 5 | Prompt Engineering | 20 | 1.6% | 入门门槛最低的 AI 技能 |
| 6 | Java | 19 | 1.6% | 企业级后端仍需 Java 底座 |
| 7 | Data Analysis | 18 | 1.5% | 数据驱动岗位基本功 |
| 8 | SQL | 15 | 1.2% | 同上，常与数据分析绑定 |
| 9 | LangChain | 14 | 1.2% | Agent 开发主流框架 |
| 10 | Multimodal AI | 11 | 0.9% | 多模态正在从研究走向应用 |
| 11 | AutoGen | 10 | 0.8% | 微软系 Multi-Agent 框架，国内热度高于海外 |
| 12 | Machine Learning | 9 | 0.7% | 国内 JD 更常说"算法"而非 ML |
| 13 | Go | 9 | 0.7% | 高并发后端 + 云原生场景 |
| 14 | NLP | 9 | 0.7% | 传统 NLP 正在被 LLM 吸收 |
| 15 | Function Calling | 9 | 0.7% | Agent 工具调用的关键能力 |

**国内市场关键词：LLM + Agent + RAG 三件套主导，工程化技能（云平台/MLOps/CI-CD）严重缺位。**

### 海外市场技能需求 Top 15

海外 JD 要求更全面、更具体，Python 以 40.8% 的提及率遥遥领先。

| 排名 | 技能 | 出现次数 | 占比 | 特点 |
|:---:|------|:------:|:---:|------|
| 1 | Python | 135 | 40.8% | 海外 AI 岗的"英语"，几乎必备 |
| 2 | Large Language Models | 79 | 23.9% | 核心但非唯一，不像国内那么集中 |
| 3 | Generative AI | 71 | 21.5% | 海外偏好这个术语，国内罕见 |
| 4 | SQL | 63 | 19.0% | 数据基础能力，海外显著重视 |
| 5 | Machine Learning | 60 | 18.1% | 海外仍将 ML 基础视为核心要求 |
| 6 | AWS | 60 | 18.1% | 三大云平台均为高频要求 |
| 7 | Azure | 53 | 16.0% | 企业市场 + OpenAI 合作加持 |
| 8 | Agent Architecture | 51 | 15.4% | 海外同样重视但占比更均衡 |
| 9 | Prompt Engineering | 50 | 15.1% | 提及率远高于国内 |
| 10 | Java | 50 | 15.1% | 企业级后端基础不分市场 |
| 11 | Google Cloud | 49 | 14.8% | Vertex AI 生态加持 |
| 12 | Data Analysis | 45 | 13.6% | 与 SQL 高度绑定 |
| 13 | PyTorch | 33 | 10.0% | 深度学习必备框架 |
| 14 | Git | 33 | 10.0% | 工程素养标配，国内 JD 几乎不提 |
| 15 | C++ | 32 | 9.7% | 推理优化 / 嵌入式 AI 场景 |

**海外市场关键词：Python 为王，云平台三件套（AWS/Azure/GCP）是硬门槛，ML 基础 + 工程化能力并重。**

### 国内 vs 海外核心差异

| 维度 | 国内 | 海外 |
|------|------|------|
| 技能集中度 | 极高（LLM 一家独大 14.3%） | 分散（Python 最高 40.8% 但其余也高） |
| 云平台 | 几乎不提（0.2%） | 三大云各 15%+，必备技能 |
| MLOps | 0 提及 | 8.5%，模型部署运维是标配 |
| 工程化（Git/CI-CD） | 合计 0.4% | 合计 18.5%，软件工程基本功 |
| Agent 框架 | LangChain + AutoGen + Dify（国产） | LangChain + CrewAI + LangGraph |
| ML 基础 | 0.7%（JD 里常隐含） | 18.1%（明确列为要求） |
| JD 风格 | 概括型（"熟悉大模型"） | 清单型（逐项列出技术栈） |

### 行业技能需求矩阵

各行业 Top 5 高频技能 + 该行业的差异化特征。

| 行业 | 岗位数 | 国内/海外 | Top 5 技能 | 行业特色 |
|------|:-----:|:---------:|-----------|---------|
| 互联网 | 544 | 407 / 137 | LLM · Agent · Python · Prompt · Data Analysis | AI 原生岗位最多，技能要求最全面 |
| 制造业 | 213 | 190 / 23 | LLM · Python · Computer Vision · Agent · Prompt | CV 是制造业独有的强需求（质检/产线） |
| 金融 | 145 | 119 / 26 | Python · LLM · Data Analysis · SQL · Prompt | 数据分析 + SQL 权重显著高于其他行业 |
| 咨询 | 143 | 98 / 45 | Python · SQL · Azure · Java · Go | 最不"AI 原生"，偏传统工程 + 云平台 |
| 汽车 | 138 | 118 / 20 | Python · LLM · C++ · PyTorch · ML | C++ 和 PyTorch 是汽车 AI 的独有标签 |
| 医疗 | 111 | 73 / 38 | LLM · Python · Agent · Generative AI · Prompt | 与互联网类似，Agent 渗透率高 |
| 教育 | 80 | 66 / 14 | LLM · ML · Python · Data Analysis · Generative AI | ML 基础要求高于平均 |
| 零售 | 65 | 62 / 3 | LLM · Agent · SQL · Python · RAG | RAG 是零售特色（商品知识库问答） |
| 传媒 | 31 | 18 / 13 | LLM · TensorFlow · RL · C++ · ML | 推荐系统驱动，RL + TF 独有组合 |
| 能源 | 17 | 13 / 4 | Agent · SQL · Data Analysis · Prompt · Function Calling | Agent + 数据分析为主，偏流程自动化 |
| 通信 | 15 | 14 / 1 | LLM · React · LangChain · LlamaIndex · AutoGen | 前端 + Agent 框架混合需求 |
| 政府 | 10 | 7 / 3 | LLM · ML | 样本少，以 LLM 应用为主 |

**行业洞察：**
- **跨行业通用技能**：LLM、Python、Prompt Engineering 是几乎所有行业的基础要求
- **行业差异化技能**：Computer Vision（制造）、C++/PyTorch（汽车）、RL/TensorFlow（传媒）、SQL/Data Analysis（金融/咨询）
- **蓝海行业**：制造、汽车、医疗、能源 — 岗位在增长但 AI 人才竞争远小于互联网

### 技能竞争力评分模型

为帮助求职者判断技能的投资回报率，我们构建了一个**技能竞争力指数（Skill Competitiveness Index, SCI）**。

#### 评分维度

| 维度 | 权重 | 计算方式 | 含义 |
|------|:---:|---------|------|
| 需求强度 | 35% | 技能总出现次数 / 最高技能次数 × 100 | 市场对该技能的绝对需求量 |
| 行业渗透度 | 25% | 出现在 Top 5 的行业数 / 13 × 100 | 技能是否跨行业通用 |
| 双市场通用性 | 20% | min(国内次数, 海外次数) / max(国内次数, 海外次数) × 100 | 同时在国内外被认可的程度 |
| 技能组合价值 | 20% | 共现 Top 10 中出现次数 / 最高共现次数 × 100 | 与其他技能搭配的协同价值 |

> **SCI = 需求强度 × 0.35 + 行业渗透度 × 0.25 + 双市场通用性 × 0.20 + 技能组合价值 × 0.20**

#### 评分结果

| 排名 | 技能 | 需求强度 | 行业渗透 | 双市场 | 组合价值 | **SCI** | 建议 |
|:---:|------|:------:|:------:|:-----:|:------:|:------:|------|
| 1 | **LLM** | 100 | 77 | 45 | 100 | **83.3** | 必修课，AI 岗位的"通行证" |
| 2 | **Python** | 68 | 62 | 28 | 95 | **63.0** | 最高 ROI 的编程语言投资 |
| 3 | **Agent Architecture** | 48 | 46 | 73 | 69 | **56.7** | 2024-2025 最热赛道，双市场均认可 |
| 4 | **SQL** | 31 | 31 | 24 | 83 | **39.3** | 容易学、回报高、跨行业刚需 |
| 5 | **Prompt Engineering** | 28 | 46 | 40 | 20 | **33.1** | 入门快但天花板低，需搭配其他技能 |
| 6 | **Data Analysis** | 25 | 38 | 40 | 20 | **29.0** | 金融/咨询/教育行业的差异化优势 |
| 7 | **Machine Learning** | 27 | 31 | 15 | 20 | **23.7** | 海外岗位刚需，国内 JD 虽少提但面试必考 |
| 8 | **Java** | 27 | 8 | 38 | 75 | **33.6** | 企业级 AI 落地的后端底座 |
| 9 | **RAG** | 19 | 8 | 56 | 10 | **18.9** | LLM 应用最成熟的范式，需深入而非浅尝 |
| 10 | **云平台 (AWS/Azure/GCP)** | 24 | 8 | 4 | 60 | **21.2** | 海外必备、国内被严重低估的隐性门槛 |
| 11 | **LangChain** | 15 | 8 | 61 | 10 | **16.5** | Agent 开发事实标准，但更新快需持续跟进 |
| 12 | **PyTorch** | 15 | 8 | 12 | 10 | **11.7** | 深度学习必备，汽车/传媒行业差异化 |
| 13 | **MLOps** | 11 | 0 | 0 | 10 | **5.9** | 国内几乎空白但实际项目离不开，蓝海技能 |
| 14 | **Docker/K8s** | 10 | 0 | 32 | 10 | **11.9** | 工程化基础，与 MLOps 搭配价值倍增 |
| 15 | **Multimodal AI** | 8 | 8 | 52 | 5 | **15.2** | 新兴方向，国内热度高于海外 |

#### 如何使用这个模型

**场景 1：国内求职者查缺补漏**
- 优先补齐 SCI 排名靠前但自己缺失的技能（LLM → Python → Agent → SQL）
- 关注"双市场通用性"高的技能 — 未来国内市场也会逐步要求
- MLOps 和云平台虽然 SCI 不高，但属于**差异化竞争**的利器（几乎没人会 = 会了就是优势）

**场景 2：转行者选方向**
- 金融/咨询背景 → Python + SQL + Data Analysis + LLM（利用数据分析优势）
- 传统后端 → Agent Architecture + LangChain + RAG（利用工程化优势）
- 制造/汽车背景 → Computer Vision + PyTorch + LLM（利用行业领域知识）

**场景 3：海外求职者**
- 必修三件套：Python + 云平台（至少一个）+ ML 基础
- 加分项：Agent + LLM + MLOps
- 注意：海外 JD 会逐项检查技术栈，不能靠"熟悉大模型"一句话概括

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
├── extension/                  # Chrome 浏览器插件（占位，待实现）
│   ├── content_scripts/        # 各平台 JD 提取脚本
│   └── popup/                  # 插件弹窗 UI
├── data/                       # 种子数据 + 配置
│   ├── seed_platforms.json     # 10 个平台元数据
│   ├── seed_skills.json        # 62 个 AI 技能（中英双语别名）
│   ├── skill_aliases.json      # 技能同义词映射表（180+ 条）
│   └── search_keywords.json    # 跨行业采集关键词矩阵（50+ 关键词）
├── docs/
│   └── domestic-scraping-strategy.md  # 国内平台爬虫技术方案
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

积极开发中 — v0.5 已上线，洞察报告 + 跨行业数据扩充

**在线体验：https://agent-hunt.pages.dev**

| Phase | 内容 | 状态 |
|---|---|---|
| 1 | 数据采集管道 + 5 平台采集器（LinkedIn/Indeed/猎聘/Boss直聘/拉勾） | **已完成** ✅ |
| 2 | 跨市场分析引擎（技能归一化、薪资分析、技能共现） | **已完成** ✅ |
| 3 | 前端 7 页 + AI 洞察 + 岗位画像 + 学习路径 | **已完成** ✅ |
| 4 | 行业维度扩展（13 行业分类 + 关键词矩阵 + 行业分析页面） | **已完成** ✅ |
| 5 | AI 洞察报告 + 跨行业数据扩充（2370 条 JD） | **已完成** ✅ |
| 6 | 持续增强（aliases 扩展、Chrome 扩展、Celery 定时采集、用户系统） | 待开始 |

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

## Contributing

欢迎贡献！特别欢迎以下方向：
- 新平台采集器的实现
- 种子 JD 数据的补充（`data/sample_jds/`）
- 技能同义词映射的完善（`data/skill_aliases.json`）

## License

MIT
