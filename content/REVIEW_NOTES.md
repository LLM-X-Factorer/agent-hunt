# 7 篇内容数据校验报告（C 阶段产出 / issue #25）

> 校验日期：2026-05-03
> 数据基线：v0.11（`frontend/public/data/*.json`）
> 范围：每篇 wechat.md 关键数字 vs 当前 narrative-stats / cross-market-overview / cross-market-skills / vendor-title-breakdown 等数据文件

## 总体结论

**7 篇全部可发**。正文数字 100% 准确，发现 2 处需要修：1 个已修（B 阶段我写的摘要 bug），1 个备注（v0.11 数据微调导致原标题数字差 0.01）。

## 逐篇校验

### #01 — 35 岁危机 ✓

正文国内/海外经验段 8 个数字 + 3 段涨幅（35% / 42% / 63%）全部精确匹配 `cross-market-overview.json`。无需改动。

### #02 — 国内外两种语言 ✓

国内 top1 LLM 6.1%（231 条）✓ / 海外 top1 Python 4.2%（231 条）✓ 完全匹配 `cross-market-skills.json`。无需改动。

### #03 — 课程教转码 vs 等懂业务（p1）✓

- 951 AI 增强岗位 ✓ 匹配 `narrative-stats.json/p1_market_basic.domestic_ai_augmented`
- 传统/互联网 ratio 3.4 ✓ 匹配 3.41

### #04 — 银行 40k 互联网 20k（p2）— 已修 1 处

| 位置 | 现状 | 校验 |
|---|---|---|
| 正文表格 9 行薪资 | 金融 30k / 医疗 30k / 制造 30k / 互联网 25k | ✓ 与 `narrative-stats.p2_salary_premium.premium_median = 30000` 匹配 |
| 正文「+20%」 | 第 48 行 | ✓ 准确 |
| 481 条样本 | 290 + 191 = 481 | ✓ |
| **B 阶段摘要 bug** | 「中位是互联网的 1.5-2 倍」 | ⚠️ 错。已改为「中位 30k，比互联网 25k 高 20%」 |

「1.5-2 倍」错误来源：把 specific case（网商银行 40-55k vs 阿里云 10-20k）的倍数误用作 median 倍数。修复后摘要数字与正文一致。

### #05 — OpenAI 桥梁工程师（p3）✓

- OpenAI 总 651 / client-facing 110 ✓ `vendor-title-breakdown.json/by_vendor.vendor_openai`
- 16.9%（文章 17%）✓ 四舍五入准确
- Anthropic 451 / 61 / 13.5%（备用对照）

### #06 — 海外 4-5× 是错的（p4）— 1 处微小偏差，已在 B 缩短版规避

| 位置 | 现状 | 校验 |
|---|---|---|
| **原标题** | 「真实是 2.42-2.78×」 | ⚠️ v0.11 实际为 2.43-2.78×（差 0.01）。`narrative-stats.p4_cross_market.native_intl_to_domestic_ratio = 2.43` |
| **B 缩短版**（推荐发布用） | 「真实 2.78×」 | ✓ 仅取 augmented 倍数，规避 0.01 偏差 |
| 3,195 条 LLM 标注 JD | — | 此为 native + augmented 总样本（1044+817+843+491=3195），匹配 |

**建议**：发布时用 B 阶段缩短版（不含 2.42），原标题归档保留。

### #07 — Deloitte 19 次（p5）✓

- Deloitte Full Stack 19 ✓ `narrative-stats.p5_ghost.top_ghost_listings[0]`
- Meta PM 17 ✓ `top_ghost_listings[1]`
- 海外 3× 国内 ✓ `intl_to_domestic_ratio = 3.1`
- 海外 5,502 jobs ≈ 文章「5000+」✓
- 「30% 折扣」标题钩子 vs 正文 60%×70%=42% 的推导：标题用 colloquial「30% 折扣」表达「先打折再投」，正文给出严格推导（5000 × 0.6 × 0.7 ≈ 2100）。语义略不严密但可读性占优——保留。

## 改动总结

| 文件 | 操作 |
|---|---|
| `04-traditional-salary-premium/wechat.md` | 修摘要：「1.5-2 倍」→「中位 30k，比互联网 25k 高 20%」 |
| `REVIEW_NOTES.md` | 新增（本文件） |

## 阶段 C 后续（dbs-content / dbs-hook 复审）

数字校验已完成。剩余两件可选项：

- **dbs-content 五维复审**（文字洁癖 / 钩子 / 表达效率 / 认知落差 / AI 辅助）—— 7 篇 thread 已在创作期审过，wechat.md 是从 thread 拓写。建议抽 1-2 篇代表性篇目（如 #01 引流试水 + #04 主线最有冲击）二次复审，不全部跑。
- **dbs-hook 钩子复审** —— 钩子在创作期已用 dbs-hook 跑过 10 方案对比并选定。除非数据变（v0.11 vs 创作期 v0.9 同口径）否则无需重审。

**判断**：数字已稳，发布无硬伤。dbs-content / dbs-hook 复审为锦上添花，可以等用户发布前一天再决定要不要做。
