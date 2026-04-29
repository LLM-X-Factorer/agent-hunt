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
      <MethodologyBox title="📐 这个数字哪来的（学员问就这么答）">
        <p>
          <strong>关键一步：把海外薪资换成「人民币 / 月薪」再比。</strong>
          海外 JD 标的是「美元 / 年薪」（比如 $120k/year），国内是「人民币 / 月薪」（比如 25k/月）。直接对比就是「12 万美元 / 年 vs 2.5 万人民币 / 月」——单位都不一致，不能直接比。
        </p>
        <p>
          <strong>我们的做法：</strong>把海外 $120k/year 按汇率（USD × 7.2）换成 86.4 万人民币 / 年，再 ÷12 = 7.2 万人民币 / 月。这样和国内的月薪同口径。
        </p>
        <p>
          <strong>修正后真实数字：</strong>
        </p>
        <ul className="list-disc list-inside text-sm space-y-1 ml-2">
          <li>AI 原生岗：国内 32.5k vs 海外 78.6k → <strong>2.42 倍</strong></li>
          <li>AI 增强岗：国内 23k vs 海外 63.9k → <strong>2.78 倍</strong></li>
        </ul>
        <p className="bg-amber-100 border-l-4 border-amber-400 p-3 rounded">
          <strong>⚠️ 这点要主动告诉学员：</strong>很多招聘文章流传的「海外是国内 4 倍 / 5 倍」是<strong>没换汇率的错误数字</strong>——直接把美元年薪当人民币月薪比，夸大了 1.7 倍。我们之前展示的也错了，已修正。讲数据时可以主动揭穿这个陷阱，反而显得专业。
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

      <MechanismBox title="🧠 为什么会这样（一句话讲透）">
        <p className="text-base font-medium">
          美国 AI 公司估值是中国的 3-5 倍，这个估值差直接转嫁到工程师薪酬上。
        </p>
        <p>
          OpenAI / Anthropic 一级市场估值数千亿美元，给 senior 工程师 $500k+ 总薪酬是合理的。中国大厂的算法岗 base 涨不上去，不是公司不愿意，是公司估值本身没那么高——薪资天花板被资本市场锁死。
        </p>
        <p>
          <strong>注意 AI 增强 ratio（2.78）比原生（2.42）还高。</strong>
          说明海外传统行业（医院 / 银行 / 制造）更愿意为 AI 复合人才付溢价。国内传统行业还在数字化转型早期，预算受限，所以本土 AI 增强岗薪资上不去——跨市场 ratio 自然就拉大了。
        </p>
        <p>
          这给学员一个反直觉的方向：如果你本职是医生 / 工程师 / 财务，<strong>转 AI 增强出海比转纯算法岗出海，相对溢价更大</strong>。
        </p>
      </MechanismBox>

      <CaveatBox title="⚠️ 给学员讲的时候要说清楚">
        <p>
          <strong>✅ 这个数字适合讲：</strong>海外 AI 岗薪资确实比国内高 2-3 倍（汇率换算后），AI 增强方向的相对优势比原生算法更大——给学员一个反直觉的出海方向感知。
        </p>
        <p>
          <strong>❌ 不能这么说：「2.78 倍 = 到手翻 2.78 倍」。</strong>
          海外生活成本（旧金山 / 纽约）比北京上海高 1.5-2 倍。扣掉之后，<strong>真实购买力差距大约 1.5-2 倍</strong>。还是有套利，但不是新闻里说的「翻几倍」。
        </p>
        <p>
          <strong>❌ 不能这么说：「申请就能去」。</strong>
          海外 70% 岗位需要 H-1B / 工签，能拿到的中国候选人路径很窄（顶尖学校 + 留学 + 公司赞助）。学员要现实评估签证路径再谈套利——纯远程的中国境内 freelancer 接海外活是另一条路，但岗位池小很多。
        </p>
        <p>
          <strong>❌ 不能这么说：「JD 标的 = 实际 offer」。</strong>
          JD 上写的是 base 薪资范围，海外大厂 senior 实际总薪酬（base + bonus + stock）比 JD asking 高 30-50%（levels.fyi 数据，可在 <a href="/salary" className="text-amber-700 underline">薪资分析</a> 看真实 vs JD 对比）。所以海外实际差距比 2.78× 还更大一些；但国内 RSU 兑现率参差不齐，要个案讨论。
        </p>
        <p>
          <strong>学员可能问：「网上看到说海外是国内 4-5 倍，你这才 2.78 是不是太保守了？」</strong>
          诚实答：那些数字大多没换汇率，把美元年薪当人民币月薪比，夸大了 1.7 倍。我们之前网站上展示的也犯过这个错，已经主动修正——这是诚实的口径。如果学员能接受这点，反而更信任你给的数据。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
