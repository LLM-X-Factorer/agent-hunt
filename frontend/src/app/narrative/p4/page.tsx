"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { NarrativeLayout } from "@/components/narrative-layout";
import {
  CaveatBox, JobExampleCard, MechanismBox, MethodologyBox, SectionHeader,
  type JobExample,
} from "@/components/narrative-bits";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Bucket { median: number; sample_size: number; }

interface Stats {
  p4_cross_market: {
    domestic_native: Bucket;
    intl_native: Bucket;
    domestic_augmented: Bucket;
    intl_augmented: Bucket;
    native_intl_to_domestic_ratio: number;
    augmented_intl_to_domestic_ratio: number;
  };
}

interface Examples {
  p4_cross_market_examples: {
    domestic_ai_native: JobExample[];
    international_ai_native: JobExample[];
    domestic_ai_augmented_traditional: JobExample[];
    international_ai_augmented_traditional: JobExample[];
  };
}

export default function P4() {
  const [s, setS] = useState<Stats | null>(null);
  const [ex, setEx] = useState<Examples | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/data/narrative-stats.json").then((r) => r.json()),
      fetch("/data/narrative-examples.json").then((r) => r.json()),
    ]).then(([a, b]) => { setS(a); setEx(b); });
  }, []);

  if (!s || !ex) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const m = s.p4_cross_market;
  const chart = [
    { name: "AI 原生", 国内: m.domestic_native.median, 海外: m.intl_native.median },
    { name: "AI 增强", 国内: m.domestic_augmented.median, 海外: m.intl_augmented.median },
  ];

  return (
    <NarrativeLayout
      index={4}
      title="跨市场套利"
      headline="海外 AI 增强岗薪资是国内的 2.78 倍"
      metric={`${m.augmented_intl_to_domestic_ratio}×`}
      metricSub={`AI 原生 ${m.native_intl_to_domestic_ratio}× · AI 增强 ${m.augmented_intl_to_domestic_ratio}×（汇率换算后）`}
      oneLiner="学员要不要出海？看汇率换算后的薪资差。AI 原生岗海外是国内 2.42 倍；AI 增强岗海外是国内 2.78 倍——出海做 AI 增强反而比出海做 AI 原生套利空间略大。但要扣掉海外生活成本和签证摩擦，实际套利空间更小。"
      copyText="按汇率换算到 CNY/月后：AI 原生岗海外 78.6k vs 国内 32.5k（2.4×）；AI 增强岗海外 63.9k vs 国内 23k（2.8×）。出海做 AI 增强 ratio 略高于出海做原生算法。但生活成本和签证摩擦没算进去。"
      dataSource={`国内 ${m.domestic_native.sample_size + m.domestic_augmented.sample_size} 条 + 海外 ${m.intl_native.sample_size + m.intl_augmented.sample_size} 条 LLM 标注岗位的 salary_min/max 中位数。海外按汇率换算到 CNY/月：USD ×7.2 ÷12 等。完整规则：backend/app/services/currency.py。`}
      deepLink={{ href: "/gaps", label: "市场差异（数据看板）" }}
      prev={{ href: "/narrative/p3", label: "论断 3 · 桥梁工程师" }}
      next={{ href: "/narrative/p5", label: "论断 5 · 预期管理" }}
    >
      <MethodologyBox>
        <p>
          <strong>汇率换算（关键步骤）：</strong>JD 表里海外岗位存的是「原币 / 年薪」（USD/EUR/GBP），国内是「CNY / 月薪」。直接对比相当于把 USD/年 当成 CNY/月——比真实数字夸大 12÷7.2 ≈ 1.7 倍。
        </p>
        <p>
          <strong>本论断的换算：</strong>
        </p>
        <ul className="list-disc list-inside text-xs space-y-1 ml-2">
          <li>海外 USD：value × 7.2 ÷ 12 → CNY/月</li>
          <li>海外 EUR：value × 7.8 ÷ 12 → CNY/月</li>
          <li>海外 GBP：value × 9.0 ÷ 12 → CNY/月</li>
          <li>国内 CNY 月薪：保持原值</li>
          <li>国内 CNY 年薪（&gt;200k 的离群值）：÷12 视为月化</li>
        </ul>
        <p>
          <strong>原 spec 标的 4×（已弃用）：</strong>之前的「海外 4× 国内」是没做汇率换算的口径错误。修正后是 2.4×（原生）/ 2.8×（增强）。这个数字更接近 levels.fyi 真实薪酬（参考论断 4 数据看板的 real-vs-asking 对比）。
        </p>
      </MethodologyBox>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">跨市场月薪中位数 · 国内 vs 海外</CardTitle>
          <p className="text-xs text-gray-500 mt-1">单位：CNY/月（海外按汇率折算）</p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k/月`, ""]} />
              <Legend />
              <Bar dataKey="国内" fill="#f87171" />
              <Bar dataKey="海外" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6 space-y-3">
            <p className="text-xs text-gray-500">AI 原生岗位（算法 / ML / LLM 工程师等）</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-indigo-600">{m.native_intl_to_domestic_ratio}×</span>
              <span className="text-xs text-gray-500">海外 / 国内</span>
            </div>
            <p className="text-xs text-gray-500">
              国内 ¥{(m.domestic_native.median / 1000).toFixed(0)}k（n = {m.domestic_native.sample_size}）
              · 海外 ¥{(m.intl_native.median / 1000).toFixed(0)}k（n = {m.intl_native.sample_size}）
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 space-y-3">
            <p className="text-xs text-gray-500">AI 增强岗位（传统专业 + AI 技能）</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-emerald-600">{m.augmented_intl_to_domestic_ratio}×</span>
              <span className="text-xs text-gray-500">海外 / 国内</span>
            </div>
            <p className="text-xs text-gray-500">
              国内 ¥{(m.domestic_augmented.median / 1000).toFixed(0)}k（n = {m.domestic_augmented.sample_size}）
              · 海外 ¥{(m.intl_augmented.median / 1000).toFixed(0)}k（n = {m.intl_augmented.sample_size}）
            </p>
          </CardContent>
        </Card>
      </div>

      <SectionHeader>真实 JD 对比（IQR 中位段，取代表性样本）</SectionHeader>
      <div className="space-y-4">
        <div>
          <p className="text-sm font-medium text-indigo-700 mb-3">🌍 海外 · AI 原生（中位 ¥{(m.intl_native.median/1000).toFixed(0)}k/月）</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ex.p4_cross_market_examples.international_ai_native.slice(0, 2).map((e, i) => (
              <JobExampleCard key={i} ex={e} />
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-rose-600 mb-3">🇨🇳 国内 · AI 原生（中位 ¥{(m.domestic_native.median/1000).toFixed(0)}k/月）</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ex.p4_cross_market_examples.domestic_ai_native.slice(0, 2).map((e, i) => (
              <JobExampleCard key={i} ex={e} />
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-emerald-700 mb-3">🌍 海外 · AI 增强（中位 ¥{(m.intl_augmented.median/1000).toFixed(0)}k/月）</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ex.p4_cross_market_examples.international_ai_augmented_traditional.slice(0, 2).map((e, i) => (
              <JobExampleCard key={i} ex={e} />
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-amber-700 mb-3">🇨🇳 国内 · AI 增强（中位 ¥{(m.domestic_augmented.median/1000).toFixed(0)}k/月）</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ex.p4_cross_market_examples.domestic_ai_augmented_traditional.slice(0, 2).map((e, i) => (
              <JobExampleCard key={i} ex={e} />
            ))}
          </div>
        </div>
      </div>

      <MechanismBox>
        <p>
          <strong>资本市场估值差：</strong>美国 SaaS 行业市值 / 销售额倍数比 A 股大 3-5 倍，这层估值差直接转嫁到工程师薪酬上。AI 公司更明显——OpenAI / Anthropic 一级市场估值数千亿美元，对应给 senior eng $500k+ 的 TC 是合理的。
        </p>
        <p>
          <strong>购买力对冲：</strong>美国生活成本旧金山 / 纽约比北京 / 上海高 1.5-2 倍。汇率换算后的「2.8×」要扣掉至少 1.5×，剩 1.5-2× 真实购买力差距。
        </p>
        <p>
          <strong>增强 ratio 高于原生：</strong>2.78 &gt; 2.42，说明海外传统行业更愿意为 AI 复合人才付溢价（医院 / 银行 / 制造企业的 AI 改造预算大）。国内传统行业还在数字化转型早期，预算受限，所以本土 AI 增强岗薪资上不去，跨市场 ratio 自然拉大。
        </p>
      </MechanismBox>

      <CaveatBox>
        <p>
          <strong>1. JD asking salary ≠ 实际 offer。</strong>
          这里看的是 JD 标注的薪资范围，不是实际入职 base + bonus + stock。levels.fyi 真实薪酬数据（{" "}
          <a href="/salary" className="text-indigo-600">数据看板 / 薪资分析</a>{" "}
          ）显示海外大厂 senior 实际 TC 比 JD asking 高 30-50%，国内大厂 RSU 兑现率参差不齐。这条 narrative 用 JD 数据，是一个保守估计。
        </p>
        <p>
          <strong>2. 签证 / 远程岗摩擦未计入。</strong>
          海外 70% 岗位需要 H-1B / 工签，能拿到的中国背景候选人只有特定路径（顶尖学校 + 留学 + 公司赞助）。不是所有学员都能跨进这道门——但理论套利空间存在。
        </p>
        <p>
          <strong>3. 我们网站之前显示的 4×、4.6× 是错的。</strong>
          因为 cross_market 服务没做汇率换算，把 USD/年 当 CNY/月 处理。修正后真实 ratio 是 2.4× / 2.8×。这个修复仅在 narrative 层面生效，<a href="/gaps" className="text-indigo-600">/gaps 数据看板</a> 上的旧数据待统一修复。
        </p>
        <p>
          <strong>4. 海外样本不均衡。</strong>
          海外 vendor_official（OpenAI/Anthropic 等）拉高了样本均值，普通海外公司（Premera / Boeing 类）的薪资接近 50-70k CNY/月——不是每家海外都能开到 $200k+。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
