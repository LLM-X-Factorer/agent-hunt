# Agent Hunt — 文档索引

本目录按"主题"分类组织，避免文档堆积在根目录。

## 📁 目录结构

```
docs/
├── README.md                    ← 你现在看的这个文件
├── agent-hunt/                  Agent Hunt 平台技术文档
├── operations/                  运营 / 业务方文档（产品手册 + 网站使用图文版 + screenshots + PDF）
├── employment-course/           非程序员 AI 就业班产品文档（v1.0 设计阶段）
└── legacy/                      旧课程归档（点头系统班 V7 等，仅供参考）
```

---

## 🛠 agent-hunt/ — 平台技术文档

Agent Hunt 平台本身（数据采集、解析、分析）的技术决策与策略文档。

| 文件 | 内容 |
|---|---|
| [domestic-scraping-strategy.md](agent-hunt/domestic-scraping-strategy.md) | 国内招聘平台采集策略（多层递进：手动 → 插件 → Playwright → API 逆向） |

---

## 📘 operations/ — 运营 / 业务方文档

给运营 / 业务 / 销售 / 内容同学的产品手册。读完能讲清网站做什么、5 论断怎么用、27 角色怎么用、常见误用怎么避。

| 文件 | 内容 |
|---|---|
| [产品手册-运营版.md](operations/产品手册-运营版.md) | 一句话定位 + 数据来源 + 三轨用法 + 5 论断逐条解读 + 话术 + 反例 + 11 条常见误用 |
| [网站使用-图文版.md](operations/网站使用-图文版.md) | 16 张 desktop 截图 + 每页"怎么读" + 速查表 + 上线前自测清单 |
| [pdf/](operations/pdf/) | 同名 PDF（11 页 + 31 页，pandoc + Chrome headless 生成） |
| [screenshots/](operations/screenshots/) | 16 张线上截图（首页 / narrative 列表 + p1-p5 / roles 国内+海外 / role 详情 / 7 数据看板） |

**重新生成 PDF**：`bash scripts/build-docs-pdf.sh`（改完 markdown 后跑一次）

---

## 🎓 employment-course/ — 就业班产品设计

新就业班产品（独立于系统班）的完整设计资料。

| 文件 | 内容 |
|---|---|
| [00-产品设计-v1.md](employment-course/00-产品设计-v1.md) | **产品设计总纲 v1.0**（11 节，含定位/市场分析/课程结构/漏斗/商业模型/透明数据/教练机制/12 周课表/落地清单/风险） |
| [01-竞品扫描-2026-04-21.md](employment-course/01-竞品扫描-2026-04-21.md) | 3000 元档泛 AI 就业班竞品扫描（12 家主竞品横向对比 + 5 类买家心理画像 + 5 条决策性发现） |
| 02-9.9诊断模板.md | （待设计）9.9 诊断报告内容模板 |
| 03-首期招生页.md | （待设计）首期招生页文案与结构 |

---

## 📦 legacy/ — 旧课程归档

历史课程文档，**不再活跃维护**。仅作为新就业班设计的参照（旧的"就业实战线"是新就业班的前身）。

| 文件 | 内容 |
|---|---|
| 点头人工智能系统班V7.md | 系统班 V7 主文档 |
| 点头人工智能系统班V7-就业实战线.md | 旧的就业实战线（嵌在系统班中的子线，已被新就业班取代） |
| 点头人工智能系统班V7-AI应用工程师进阶线.md | 系统班 V7 进阶线（Harness Engineering 方向） |
| 点头人工智能课程产品手册-影像实验室.md | 影像实验室课程产品手册 |

---

## 📝 文档约定

- **新增就业班相关文档** → `employment-course/`，按 `XX-主题.md` 命名（XX 是序号）
- **新增平台技术文档** → `agent-hunt/`
- **临时报告/调研** → 同样放 `employment-course/`，文件名带日期
- **不要直接往 `docs/` 根目录放新文档**（除了本 README）
- 中文文件名 OK（保持已有风格），目录名用英文
