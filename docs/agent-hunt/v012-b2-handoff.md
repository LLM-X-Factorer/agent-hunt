# v0.12 B2 接力 prompt — /professions 列表 + 详情页

放在 `docs/agent-hunt/` 方便下个会话 cat 给 Claude。

---

## 给下个会话的 prompt

继续 agent-hunt v0.12 epic（GitHub [#32](https://github.com/LLM-X-Factorer/agent-hunt/issues/32)）下一项，做 [#37 B2](https://github.com/LLM-X-Factorer/agent-hunt/issues/37)：新建 `/professions` 列表 + 详情页，让业务方能回答"我是 X 传统职业怎么转 AI"。

**已完成（commit `61f66ca` on main）**：
- B1 [#36](https://github.com/LLM-X-Factorer/agent-hunt/issues/36)：`/roles/[id]` 硬性要求 section（学历 + 专业 + 高频职责）+ 国内 JD 大幅扩 ByteDance 3170 条
- A1 [#33](https://github.com/LLM-X-Factorer/agent-hunt/issues/33)：`major_requirement` 字段 + 9286 backfill
- A3 [#35](https://github.com/LLM-X-Factorer/agent-hunt/issues/35)：`role_type` enum 加 `non_ai_traditional`
- 国内数据：3786 → 6956 parsed jobs（+84%）

**#37 任务清单**（GitHub issue 原话）：
- [ ] `frontend/src/app/professions/page.tsx` 列表（8 张卡）
- [ ] `frontend/src/app/professions/[id]/page.tsx` 详情（SSG `generateStaticParams`）
- [ ] 详情结构（参考 `/roles/[id]`）：一句话定位 + 手写描述 / 学历 / 专业 / 高频职责 / 薪资分位 / **「能转哪些 AI 岗」**（基于 `ai_augmented_traditional` + `base_profession` 链接到对应 `/roles/[id]`) / 「学这些技能能转过去」
- [ ] 首页加第 4 入口卡：「探索你的传统职业」
- [ ] 手写 8 条 `backend/data/profession_descriptions.json`（结构参考 `role_descriptions.json`）
- [ ] 数据契约：新增 `backend/scripts/export_profession_profiles.py` → `frontend/public/data/profession-profiles.json`

8 个传统职业（来自 [#34 A2](https://github.com/LLM-X-Factorer/agent-hunt/issues/34) 已 scope）：
- 工程线 4：电气工程师 / 机械工程师 / 土木工程师 / 化工工程师
- 商科线 2：会计 / 金融分析师
- 服务线 2：教师 / 销售

---

## ⚠️ 关键阻塞 — #34 数据采集状态

#37 issue 原本 blocked by #34（采集 8 个传统职业 baseline JD）。**#34 还没启动且当前路径有难度**：

- 计划用 Boss/Liepin/Lagou 采，但这次 session 实测 Boss/Liepin 反爬全面升级 — 浏览器指纹 + 行为检测双层。CDP attach 到真人 Chrome 也撑不过 ~20 条 sequential JD detail（Liepin 触发 SMS 验证）。**Boss/Liepin 大规模采集事实上不可行**
- LinkedIn/Indeed via JobSpy 还能用，但只覆盖海外
- 国内传统职业（电气/机械/土木/化工/会计/金融/教师/销售）目前**没有干净的开放 ATS 数据源**

### 现有数据可用部分

虽然没有 8 个传统职业的"纯净 baseline"，但 DB 里已有 **2096 条 `ai_augmented_traditional` 岗位**（AI 增强版的传统职业），`base_profession` 字段已部分覆盖目标 8 职业：

```
教师           45 条
金融分析师      30 条
销售/销售经理/销售总监   58 条
机械工程师      17 条
（电气/土木/化工/会计 多数 < 10 条，需要更多收集）
```

这部分数据**直接支撑 #37 的「能转哪些 AI 岗」section**，因为这些岗位本身就标了 `base_profession=电气工程师` 等，可以反向聚合"AI 增强的电气工程师都在哪些 role_id 下"。

### 推荐执行方向

**方案 A（推荐）：UI-first，半数据 ship**
1. 先建路由 + 详情页结构
2. "能转哪些 AI 岗" / "学这些技能转过去" 用现有 `ai_augmented_traditional` 数据驱动（这是 #37 最有业务价值的那半）
3. baseline（学历/专业/薪资/职责）用现有 `ai_augmented_traditional` 子集近似展示，标 disclaimer "数据基于 X 个 AI 增强样本，纯传统 JD 采集 in flight"
4. 8 条手写 profession_description 是干货
5. 后续 #34 真正采到数据再迭代 baseline 部分
- 工作量：~3-4h
- 业务价值：80%（缺纯净 baseline，但 cross-link 这块完整）

**方案 B：先解 #34，再做 #37**
- 用 JobSpy 拉海外 + 用浏览器扩展（B/D 之前提过的）手动补国内 → 2-3 周持续工作
- 不建议，因为没有等待价值

**方案 C：只做手写描述 + cross-link，跳过 baseline**
- 不放 baseline section，只展示职业卡 + AI 转型路径
- 最小可行，~2h
- 缺一些数据味，但诚实

我个人建议 A（80% 价值最小风险）。

---

## 数据 + 文件参考

### 已有可用数据
- `backend/data/role_descriptions.json` — 27 角色的手写描述结构，**直接模仿写 profession_descriptions.json**
- DB Job.role_type='ai_augmented_traditional' AND base_profession='教师'（等）→ 这些数据驱动「能转哪些 AI 岗」
- `frontend/public/data/role-profiles.json` — 27 角色已有的 sample_titles / required_skills 等，可以反向找传统职业 → AI 角色 的链接关系

### 模仿现有结构
- `frontend/src/app/roles/page.tsx` → 列表 with tabs（domestic/intl）
- `frontend/src/app/roles/[market]/[roleId]/page.tsx` → SSG 详情页结构（已有 generateStaticParams 模式）
- `backend/scripts/export_role_profiles.py` → 文件 merge 模式（手写描述 + DB aggregate）
- `frontend/src/lib/roles.ts` → 类型定义模式

### 实施步骤建议
1. `backend/data/profession_descriptions.json` — 8 条手写（profession_id / cn_name / en_name / one_liner / responsibilities / pathway_summary / who_should_pivot 等）
2. `backend/scripts/export_profession_profiles.py` —
   - 读 `profession_descriptions.json`
   - 查 DB: `ai_augmented_traditional` jobs grouped by `base_profession` 模糊匹配 8 职业
   - 对每职业聚合：sample_size / median_salary / top role_ids / top skills
   - 写 `frontend/public/data/profession-profiles.json`
3. `frontend/src/lib/professions.ts` — 类型定义
4. `frontend/src/app/professions/page.tsx` — 8 张卡列表
5. `frontend/src/app/professions/[id]/page.tsx` — SSG 详情，每张卡含「能转哪些 AI 岗」section（用 Link 到 `/roles/[market]/[roleId]`）
6. `frontend/src/app/page.tsx` — 加第 4 入口卡（现在 3 张：叙事手册 / 岗位画像 / 数据看板）
7. `npm run build` + `wrangler pages deploy out --project-name agent-hunt`
8. 关 #37

### 注意
- 不要碰 `/roles` 现有路由（27 角色页已上线，别影响）
- 部署链：`agent-hunt.pages.dev`
- 业务方关心的核心问题（issue #32 epic 原文）：「我是电气工程师怎么转 AI / 教师能不能用 AI」— 详情页 narrative 要回答这个
- 8 职业里目前 base_profession 数据稀疏的（电气/土木/化工/会计）：详情页可以做但 sample 量小，需要 disclaimer 同 B1 的 pattern

### 验证
- 业务方 `/professions/teacher`（教师）应该能看到：
  - 教师职业一句话定位 + 描述
  - 「能转哪些 AI 岗」section 列出 N 个 AI role 卡（如 ai_engineer / product_manager / operations 等带 base_profession='教师' 出现频次最高的），每张可点击跳到 `/roles/domestic/X`
  - 薪资 / 学历 baseline（基于 ai_augmented_traditional 教师 45 条）+ disclaimer

---

## 检查清单（开会话时第一件事）

- [ ] `cat docs/agent-hunt/v012-b2-handoff.md` 拉一遍上下文
- [ ] `git log --oneline -5` 确认 `61f66ca` 在 main
- [ ] `gh issue list --state open` 确认 #37 还 open
- [ ] DB 连接：`cd backend && .venv/bin/alembic current` 应返回 `009`
- [ ] 跑一次 base_profession 分布 query 看数据底盘（见上面 "现有数据可用部分"）
- [ ] 跟用户确认走方案 A / B / C 哪个（推荐 A）
