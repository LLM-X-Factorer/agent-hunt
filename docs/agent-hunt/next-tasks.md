# Agent Hunt — 跨会话任务清单

> 最近更新：2026-04-29
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

---

## 待办任务清单（按 ROI 排序）

### #17 后续 — GitHub hiring repos【P2 · 推荐先做】

**ROI**：⭐⭐⭐⭐⭐ — GitHub API 公开零反爬，已有参考 collector

**目标**：抓取 GitHub 上的 awesome-jobs / `<company>-hiring` 仓库 + monthly hiring threads（issue 形式）的招聘信息。补充 HN Who is Hiring（已 1365 条）的覆盖。

**入表**：`jobs` 表，`source="community_open"`，`platform_id="community_github_hiring"`

**启动 prompt**：
> 我们继续做 agent-hunt 项目（数据生产端，下游是 aijobfit 求职诊断）。
>
> 【当前 issue】要做 issue #17 后续 — GitHub hiring repos collector。覆盖 awesome-jobs / `<company>-hiring` 类仓库 + monthly hiring threads（issue 形式）。GitHub API 公开零反爬。
>
> 【入表】jobs 表，`source="community_open"`，`platform_id="community_github_hiring"`。
>
> 【参考】backend/scripts/collect_hn_wih.py（HN Algolia API 模式，最接近）。
>
> 【上下文】docs/agent-hunt/next-tasks.md 有完整工作流和约定，请先看。

---

### #14 后续 — 一亩三分地 offer 板【P1】

**ROI**：⭐⭐⭐⭐ — 与现有牛客 collector 同模式，海外 offer + 留学背景互补

**目标**：抓 1point3acres.com 的 offer 板，补 nowcoder（国内）覆盖不到的海外 + 留学群体画像。

**入表**：`applicant_profiles` 表，`source="1point3acres"`

**启动 prompt**：
> 我们继续做 agent-hunt 项目（数据生产端，下游是 aijobfit 求职诊断）。
>
> 【当前 issue】要做 issue #14 后续 — 一亩三分地（1point3acres.com）offer 板 collector，偏海外 + 留学背景。与现有 nowcoder collector 互补（nowcoder 主要是国内应届）。
>
> 【入表】applicant_profiles 表，`source="1point3acres"`。schema 同 nowcoder（用户 background / 学校 / GPA / 海投数 / 录取公司 / offer comp 等）。
>
> 【参考】backend/scripts/collect_nowcoder_posts.py（SSR `__INITIAL_STATE__` regex 模式）+ backend/scripts/export_applicant_profiles.py（衍生 JSON 输出）。
>
> 【上下文】docs/agent-hunt/next-tasks.md 有完整工作流。一亩三分地很可能需要登录 + 反爬，先 spike，反爬太重就降级抓 SEO 公开页。

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

### #13 — 月度快照定时任务【P0 基础设施】

**ROI**：⭐⭐ — `snapshots` 表 schema 已有（migration 003），缺的是定时任务把数据滚起来。其他 issue（#16）依赖此

**启动 prompt**：
> 我们继续做 agent-hunt 项目（数据生产端，下游是 aijobfit 求职诊断）。
>
> 【当前 issue】要做 issue #13 P0 — 数据时间序列（月度快照定时任务）。
>
> 【现状】`snapshots` 表 schema 已有（migration 003），缺定时任务把数据滚起来。
>
> 【实施】
> 1. 看现有 snapshot model + 是否已有 service 写入逻辑
> 2. 加 Celery beat 任务（每月 1 号跑），快照内容：技能 Top N 排名 + 角色 × 行业 矩阵 + 薪资分布
> 3. 加 export_trends.py（已存在）的 month-over-month diff
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

- **#15** levels.fyi CN 大厂扩展（commit 3fd5bfe）— 1392 salary reports
- **#9 / 部分 #10 / 部分 #11** 行业 × 岗位 2D + 增强职业 + graduate-friendly（commit 9884f47）
- **#14 部分** nowcoder applicant profiles（commit 28f70f5）— 718 条
- **#15 部分** levels.fyi 海外 AI 公司 collector（commit d100ade）
- **#12 部分 / #17 部分** vendor ATS（OpenAI/Anthropic/xAI/Cohere/DeepMind 1532 条）+ HN WIH（1365 条）（commits b5f0453 + d6b9a5e）
