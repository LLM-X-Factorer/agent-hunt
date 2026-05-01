# Content — 自媒体内容管理

基于 agent-hunt 数据洞察的自媒体内容，按选题组织。

## 目录结构

```
content/
  {序号}-{选题slug}/
    thread.md        # X/推特 thread（6 条左右，发布渠道 1）
    xiaohongshu.md   # 小红书图文 配文 + 标签 + 发布注意（渠道 2）
    xhs-cards.md     # 喂 md2red 的 markdown（生成 7 张小红书卡片）
    wechat.md        # 公众号长文（渠道 3）
    assets/          # 图表、封面等横版素材（X / 公众号用）+ charts.html 源文件
    xhs-output/      # md2red 生成的 7 张竖版卡（小红书用）
```

## 内容规划（7 篇）

总体结构：**0 期引流 2 篇 + 主线 5 篇（对应 narrative `/narrative/p1~p5` 五条论断）**。

### 0 期引流（已创作）

发布定位：建账号调性 / 数据驱动反主流叙事。不在 narrative 5 论断范围里，但内容风格一致，先发试水。

| # | 选题 | 核心数据 | 状态 |
|---|------|---------|------|
| 01 | 35 岁危机是假的 | 国内 AI 涨幅 35% → 42% → 63%（加速） | ✅ 内容已创作 + v0.11 校准 |
| 02 | 国内外 AI 招聘说两种语言 | 技能鸿沟 Top 5 | 🚧 内容已写但 v0.6 数据，待重写（叙事要换角度） |

### 主线 5 篇（待创作）

每篇严格对应 narrative 5 论断，发布前去 `/narrative/p{N}` 对一遍业务话术 + 适用边界。

| # | 对应论断 | 选题钩子 | 核心数据点 | 状态 |
|---|---------|---------|-----------|------|
| 03 | **[p1 市场基本盘](https://agent-hunt.pages.dev/narrative/p1)** | AI 工程师别盯 BAT，盯传统行业（医疗 / 制造 / 金融）| 国内传统行业 AI 增强需求 = 互联网 3.4×（677 vs 197 条）| 📋 待创作 |
| 04 | **[p2 薪资反直觉](https://agent-hunt.pages.dev/narrative/p2)** | 转 AI 别去互联网，医疗/制造/金融多给 20% | AI 增强中位 30k vs 互联网 25k | 📋 待创作 |
| 05 | **[p3 桥梁工程师](https://agent-hunt.pages.dev/narrative/p3)** | 海外 OpenAI / Anthropic 17% 招「桥梁工程师」，国内课程零覆盖 | FDE / Solutions / Applied Engineer ~17% 占比 | 📋 待创作 |
| 06 | **[p4 跨市场套利](https://agent-hunt.pages.dev/narrative/p4)** | 国内外 AI 薪资差距 2.78× 不是 4-5×（汇率换算前都吹大）| 海外 AI 增强 / 国内 = 2.78× | 📋 待创作 |
| 07 | **[p5 预期管理](https://agent-hunt.pages.dev/narrative/p5)** | 海外 AI 海投前先看「幽灵岗」信号 | 海外集中度 0.55% vs 国内 0.18% = 3× | 📋 待创作 |

每篇追踪 issue：#1（01 发布）/ #2（02 发布）/ #20-#24（03-07 创作）。

## 数据基线

所有内容都基于 agent-hunt **v0.11**（2026-05）数据集：22 个数据源 / 9,287 条 AI 岗位 JD（国内 3,786 / 海外 5,501）/ LLM 结构化解析 / 27 角色画像。

写作前先核对数字，必看：
- `frontend/public/data/cross-market-overview.json` — 国内/海外薪资 + 经验段
- `frontend/public/data/cross-market-skills.json` — 技能差异
- `frontend/public/data/narrative-stats.json` — 5 论断核心数字
- `frontend/public/data/narrative-examples.json` — 真实 JD 例子
- `frontend/public/data/role-profiles.json` — 27 角色画像（v0.11 新增）

## 发布流程

每篇内容遵循同一发布顺序：

1. **X thread 试水**（工作日上午 9-10 点）— 发推 + 24h 观察评论
2. **小红书图文跟上**（中午 12-13 点）— 7 张卡片 + 配文 + 标签
3. **公众号长文压轴**（晚 8-9 点）— 完整论述 + 引流

## 引流闭环

每条内容评论区留：「留下技能栈，帮你做市场定位」→ 引导到 [aijobfit](https://aijobfit.llmxfactor.cloud/) 免费诊断 → 撞遮罩 → 加小助理微信 → 用激活码 `AIJOB-2026` 解锁完整报告。

## 工具

- 横版图表（X / 公众号）：自建 `assets/charts.html`（Chart.js + 真实数据），用 playwright 截图保存 PNG
- 小红书 7 张卡：`/Users/liu/Projects/md2red/` 工具，喂 `xhs-cards.md`，命令：
  ```bash
  cd /Users/liu/Projects/md2red
  node dist/cli/index.js generate <path>/xhs-cards.md -o <path>/xhs-output
  ```
  注意 md2red 处理 list (`- ...`) 会合并成一行，要拆成空行分隔的段落

## 数据更新触发的内容修订

数据集每次跨大版本（如 v0.6 → v0.11）后，已发布内容的「样本量 + 核心数字」要重新校准；叙事弧线如果还成立就保留，破了就重写。
