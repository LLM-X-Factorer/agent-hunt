"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { NarrativeLayout } from "@/components/narrative-layout";
import {
  CaveatBox, JobExampleCard, MechanismBox, MethodologyBox, SectionHeader,
  type JobExample,
} from "@/components/narrative-bits";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { industryLabel } from "@/lib/labels";

interface IndustryRow {
  industry: string;
  job_count: number;
  salary_sample_size: number;
  p25: number;
  p50: number;
  p75: number;
}

interface Data {
  by_industry: IndustryRow[];
  comparison: {
    premium_traditional_median: number;
    internet_median: number;
    delta_pct: number;
    premium_traditional_sample_size: number;
    internet_sample_size: number;
  };
  total_jobs: number;
}

interface Examples {
  p1_p2_industries: Record<string, JobExample[]>;
}

const PREMIUM = new Set(["healthcare", "manufacturing", "finance"]);

export default function P2() {
  const [d, setD] = useState<Data | null>(null);
  const [ex, setEx] = useState<Examples | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/data/industry-augmented-salary.json").then((r) => r.json()),
      fetch("/data/narrative-examples.json").then((r) => r.json()),
    ]).then(([a, b]) => { setD(a); setEx(b); });
  }, []);

  if (!d || !ex) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const chart = d.by_industry.map((r) => ({
    name: industryLabel(r.industry),
    industry: r.industry,
    median: r.p50,
    sample: r.salary_sample_size,
    isInternet: r.industry === "internet",
    isPremium: PREMIUM.has(r.industry),
  }));

  return (
    <NarrativeLayout
      index={2}
      title="薪资反直觉"
      headline="医疗/制造/金融 AI 增强岗，比互联网高 20%"
      metric={`+${d.comparison.delta_pct}%`}
      metricSub={`30k vs 25k（中位数）`}
      oneLiner="学员心里默认「互联网 = 高薪」，结果在 AI 增强方向反向走——互联网公司给『懂 AI 的非算法岗』开 25k；医疗 / 制造 / 金融开 30k。传统行业反而能给 20% 溢价。"
      copyText="国内 AI 增强岗位，互联网公司开 25k；医疗 / 制造 / 金融开 30k——传统行业比互联网高 20%。学员心里默认『互联网=高薪』，结果在 AI 增强方向反向走。"
      dataSource={`${d.total_jobs} 个国内 ai_augmented_traditional 岗位的 salary_min/salary_max 中位数。Premium 组 = healthcare + manufacturing + finance（合计 ${d.comparison.premium_traditional_sample_size} 条样本，全部 CNY/月）vs internet（${d.comparison.internet_sample_size} 条）。`}
      deepLink={{ href: "/salary", label: "薪资分析（数据看板）" }}
      prev={{ href: "/narrative/p1", label: "论断 1 · 市场基本盘" }}
      next={{ href: "/narrative/p3", label: "论断 3 · 桥梁工程师" }}
    >
      <MethodologyBox title="📐 这个数字哪来的（学员问就这么答）">
        <p>
          <strong>一句话：</strong>从国内 901 条 AI 增强岗位（见 <a href="/narrative/p1" className="text-gray-900 underline">论断 1</a> 口径）按行业分组取薪资<strong>中位数</strong>——不用平均数，因为平均数会被几个 CEO / 创始人级别岗位拉高，失真。要求每个行业至少 5 条样本，避免「能源 1 条 80k」这种伪信号。
        </p>
        <p>
          <strong>30k vs 25k 是怎么挑的：</strong>挑出 3 个中位数都达到 30k 的传统行业——医疗、制造、金融（合计 {d.comparison.premium_traditional_sample_size} 条）。和互联网（25k / {d.comparison.internet_sample_size} 条）直接对比，差 +{d.comparison.delta_pct}%。
        </p>
        <p>
          <strong>注意是「3 个高薪传统行业 vs 互联网」，不是「所有传统 vs 互联网」。</strong>
          教育 / 媒体 / 零售的薪资其实低于互联网（见图）——这条 narrative 缩到「最 hot 的 3 个行业」更准确。
        </p>
      </MethodologyBox>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">国内 AI 增强岗位 · 行业薪资中位数</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            金色 = 高薪传统行业（医疗/制造/金融）· 红色 = 互联网 · 灰色 = 其他
          </p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={Math.max(280, chart.length * 32)}>
            <BarChart data={chart} layout="vertical" margin={{ left: 100 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={100} />
              <Tooltip
                formatter={(v, _n, p) => [
                  `¥${(Number(v) / 1000).toFixed(1)}k/月（n=${p.payload.sample}）`,
                  "中位月薪",
                ]}
              />
              <Bar dataKey="median">
                {chart.map((row, i) => (
                  <Cell
                    key={i}
                    fill={row.isPremium ? "#f59e0b" : row.isInternet ? "#f87171" : "#9ca3af"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <SectionHeader>真实 JD 对比（高薪传统行业 vs 互联网）</SectionHeader>
      <div className="space-y-4">
        <div>
          <p className="text-sm font-medium text-amber-700 mb-3">
            🟠 高薪传统行业（中位 30k/月，n = {d.comparison.premium_traditional_sample_size}）
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ex.p1_p2_industries.healthcare?.[0] && <JobExampleCard ex={ex.p1_p2_industries.healthcare[0]} />}
            {ex.p1_p2_industries.manufacturing?.[0] && <JobExampleCard ex={ex.p1_p2_industries.manufacturing[0]} />}
            {ex.p1_p2_industries.finance?.[0] && <JobExampleCard ex={ex.p1_p2_industries.finance[0]} />}
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-rose-600 mb-3">
            🔴 互联网（中位 25k/月，n = {d.comparison.internet_sample_size}）
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ex.p1_p2_industries.internet?.slice(0, 2).map((e, i) => (
              <JobExampleCard key={i} ex={e} />
            ))}
          </div>
        </div>
      </div>

      <MechanismBox title="🧠 为什么会这样（一句话讲透）">
        <p className="text-base font-medium">
          会业务又会 AI 的「复合型人才」太少。
        </p>
        <p>
          医院里既懂临床又会调 LLM 的人有几个？工厂里既懂精密加工又会跑视觉模型的工程师有几个？金融里既懂量化业务又会写策略代码的人有几个？——极少。这种稀缺性直接转化成薪资溢价。
        </p>
        <p>
          相比之下，互联网公司「会用 Copilot 的全栈」「会调 Prompt 的 PM」遍地都是——供给充分，没溢价。
        </p>
        <p>
          另一个原因是<strong>付费意愿不同</strong>：传统行业「AI 改造业务」的预算来自数字化转型经费（一次性投入），愿意为关键岗位开高薪；互联网公司的 AI 增强是日常成本，倾向控制 headcount。
        </p>
      </MechanismBox>

      <CaveatBox title="⚠️ 给学员讲的时候要说清楚">
        <p>
          <strong>✅ 这个数字适合讲：</strong>学员若本职是医生 / 工业工程师 / 金融分析师，转 AI 增强方向反而比纯互联网背景的 AI 程序员更吃香——稀缺性带来溢价。
        </p>
        <p>
          <strong>❌ 不能这么说：「传统行业 = 高薪」。</strong>
          零售 15k / 媒体 12.5k / 教育 25k——和互联网持平甚至更低。准确说法是<strong>「医疗、制造、金融三强 = 高薪」</strong>，其他传统行业不一定。
        </p>
        <p>
          <strong>❌ 不能这么说：「中位数 30k 就是能拿 30k」。</strong>
          中位数是「有一半人拿这个或更多」。p75（前 25% 高薪）：医疗 45k / 制造 45k / 金融 50k——上四分位也不算特别高。这数字适合讲「平均能给到」，不适合讲「最高能给多少」。
        </p>
        <p>
          <strong>学员可能问：「能源 48k 那么高，我能去吗？」</strong>
          诚实答：那是 6 条样本的小样本数字，统计学上不显著，不能作为承诺。把焦点放在医疗 / 制造 / 金融三强。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
