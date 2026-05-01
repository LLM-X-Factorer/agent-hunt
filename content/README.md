# Content — 自媒体内容管理

基于 agent-hunt 数据洞察的自媒体内容，按选题组织。

## 目录结构

```
content/
  {序号}-{选题slug}/
    thread.md        # X/推特 thread（6-7 条，发布渠道 1）
    xiaohongshu.md   # 小红书图文 配文 + 标签 + 发布注意（渠道 2）
    xhs-cards.md     # 喂 md2red 的 markdown（生成 7-9 张小红书卡片）
    wechat.md        # 公众号长文（渠道 3）
    assets/          # 图表、封面等横版素材（X / 公众号用）+ charts.html 源文件
    xhs-output/      # md2red 生成的竖版卡（小红书用）
```

## 内容规划（7 篇）

总体结构：**0 期引流 2 篇 + 主线 5 篇（对应 narrative `/narrative/p1~p5` 五条论断）**。

**状态：7 篇全部交付完成**（2026-05-01）。所有 thread 均经过 `/dbs-content` + `/dbs-hook` 审核标准化。

### 0 期引流（2 篇 ✅）

发布定位：建账号调性 / 数据驱动反主流叙事。不在 narrative 5 论断范围里，但内容风格一致，先发试水。

| # | 选题 | 核心钩子 | 状态 |
|---|------|---------|------|
| 01 | 35 岁危机是假的 | 「『35 岁危机』在 AI 领域是错的——5-10 年涨幅 +63% vs 0-3 年 +35%」 | ✅ v0.11 + dbs 审核完成 |
| 02 | 国内外 AI 招聘说两种语言 | 「国内 top 1 是 LLM，海外 top 1 是 Python——招『会用 AI 的人』vs『能建 AI 系统的人』」 | ✅ v0.11 + dbs 审核完成 |

### 主线 5 篇（5 篇 ✅）

每篇严格对应 narrative 5 论断，**钩子 + 引流均经 `/dbs-content` 审核** 确保和 0 期 2 篇形成差异化叙事。

| # | 对应论断 | 钩子 | 引流问法（差异化）| 状态 |
|---|---------|-----|------------------|------|
| 03 | **[p1 市场基本盘](https://agent-hunt.pages.dev/narrative/p1)** | 「所有课程在教转码 / 所有岗位在等懂业务的人——传统行业 AI 增强 = 互联网 3.4×」 | 本职 + 想用 AI 做的事 → 5 条对口 JD + 缺什么 | ✅ |
| 04 | **[p2 薪资反直觉](https://agent-hunt.pages.dev/narrative/p2)** | 「网商银行 40-55k vs 阿里云 10-20k——同城同方向同经验，银行下限 = 互联网上限 × 2」 | 本职 + 期望薪资 → p25/p50/p75 + 期望能不能拿到 + 缺什么 | ✅ |
| 05 | **[p3 桥梁工程师](https://agent-hunt.pages.dev/narrative/p3)** | 「OpenAI 招的 110 个工程师不是写代码的——是『派去客户公司驻场把 LLM 落地』的桥梁角色」 | SWE/MLE 年数 + 客户对接经验 → 5 家 vendor 对口岗位（带 source URL）+ 月薪 + 缺什么 3 项 | ✅ |
| 06 | **[p4 跨市场套利](https://agent-hunt.pages.dev/narrative/p4)** | 「『海外 AI 4-5 倍』是错的——汇率换算后只有 2.78×。那『4-5 倍』是怎么算出来的？」 | 本职 + 想去的城市 → 城市级真实薪资 + 真实购买力 + 签证路径感知 | ✅ |
| 07 | **[p5 预期管理](https://agent-hunt.pages.dev/narrative/p5)** | 「Deloitte 一个 Full Stack 标题挂了 19 次 / Meta PM 17 次——海外岗位数量 ≠ 真实 hiring slot」 | 海外目标公司清单（1-3 家）+ title → 重发集中度 + 真实 active 岗位 + 海投建议 | ✅ |

**Issue 追踪**：
- 发布：#1（01）/ #2（02）—— 待用户发布
- 创作：#20-#24（03-07）—— 全部 close

## 数据基线

所有内容都基于 agent-hunt **v0.11**（2026-05）数据集：22 个数据源 / 9,287 条 AI 岗位 JD（国内 3,786 / 海外 5,501）/ LLM 结构化解析 / 27 角色画像。

写作前先核对数字，必看：
- `frontend/public/data/cross-market-overview.json` — 国内/海外薪资 + 经验段
- `frontend/public/data/cross-market-skills.json` — 技能差异
- `frontend/public/data/narrative-stats.json` — 5 论断核心数字
- `frontend/public/data/narrative-examples.json` — 真实 JD 例子
- `frontend/public/data/role-profiles.json` — 27 角色画像（v0.11 新增）
- `frontend/public/data/industry-augmented-salary.json` — 行业 × AI 增强薪资
- `frontend/public/data/vendor-title-breakdown.json` — 5 家 vendor 桥梁岗占比

## 创作工作流（标准化）

每篇内容（无论新写还是重写）都按这套流程：

1. **拉数据 + 读对应 narrative 页**（如 `/narrative/p1`）—— 把业务话术 / 方法论 / caveat 内化
2. **写 thread.md v1**（X 7 条结构：钩子 / 数据 / 例子 / 机制 / caveat / 行动 / 引流）
3. **调用 `/dbs-content` skill 审核** —— 五维诊断（文字洁癖 / 钩子 / 表达效率 / 认知落差 / AI 辅助）+ 引流话术专项诊断
4. **采纳改法 → 改 thread.md v2**（钩子如果需要 10 方案对比，调用 `/dbs-hook`）
5. **同步写 xiaohongshu.md / xhs-cards.md / wechat.md**（基于改后的 thread 钩子和引流话术）
6. **做 charts.html + playwright 截图** —— 横版（1280×720）2-3 张给 X / 公众号 + 竖版（900×~900）1 张给小红书
7. **跑 md2red** —— 喂 `xhs-cards.md` 生成 7-9 张小红书卡
8. **commit + push** —— 关联对应 issue（`Closes #X`）

## 引流闭环

每条内容评论区留**抓 thread 主题的具体小价值承诺 + 数量限制**（前 30 个免费）→ 引导到 [aijobfit](https://aijobfit.llmxfactor.cloud/) 免费诊断 → 撞遮罩 → 加小助理微信 → 用激活码 `AIJOB-2026` 解锁完整报告。

7 篇引流话术全部差异化（避免连读重复），见上面表格的「引流问法（差异化）」列。

## 工具

- 横版图表（X / 公众号）：自建 `assets/charts.html`（Chart.js + 真实数据），用 playwright 截图保存 PNG
- 小红书 7-9 张卡：`/Users/liu/Projects/md2red/` 工具，喂 `xhs-cards.md`，命令：
  ```bash
  cd /Users/liu/Projects/md2red
  node dist/cli/index.js generate <path>/xhs-cards.md -o <path>/xhs-output
  ```
  **md2red 已知坑**：处理 list (`- ...`) 会合并成一行，要拆成空行分隔的段落
- 截图临时服务：在 agent-hunt 根目录跑 `python3 -m http.server 8765 --bind 127.0.0.1`，playwright 访问 `http://127.0.0.1:8765/content/<id>/assets/charts.html`，对各 panel 用 `target` 选择器精确截图

## 发布流程

每篇内容遵循同一发布顺序：

1. **X thread 试水**（工作日上午 9-10 点）— 发推 + 24h 观察评论
2. **小红书图文跟上**（中午 12-13 点）— 7-9 张卡片 + 配文 + 标签
3. **公众号长文压轴**（晚 8-9 点）— 完整论述 + 引流

## 数据更新触发的内容修订

数据集每次跨大版本（如 v0.6 → v0.11）后，已发布内容的「样本量 + 核心数字」要重新校准；叙事弧线如果还成立就保留，破了就重写。

校准流程：拉最新数据 → 比对每个数字点 → 改 4 个 markdown → 重跑 charts + md2red → commit。
