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
      <MethodologyBox>
        <p>
          <strong>怎么算的：</strong>每条 JD 取 (salary_min + salary_max) / 2 作为薪资中点（CNY/月），按 industry 分组取中位数（不是平均数——避免 CEO/创始人级别离群值拉高）。样本 ≥ 5 才显示，避免「能源 1 条 80k」这类伪信号。
        </p>
        <p>
          <strong>「Premium 组」怎么定义的：</strong>挑出 3 个中位数都达到 30k 的传统行业（healthcare 30k / manufacturing 30k / finance 30k），合计 285 条样本。和互联网（25k 中位 / 191 条）直接对比 → +20% 溢价。这不是「所有传统行业都比互联网高」，是「最 hot 的 3 个传统行业比互联网高」。
        </p>
        <p>
          <strong>不混合海外数据：</strong>本论断只看国内市场（CNY 月薪），国内外薪资对比见{" "}
          <a href="/narrative/p4" className="text-indigo-600">论断 4</a>。
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

      <MechanismBox>
        <p>
          <strong>稀缺性溢价：</strong>「医生 + AI」「工厂工艺工程师 + 深度学习」「金融分析师 + 量化模型」需要双重背景的复合人。传统行业里既懂业务又会 AI 工具的人极少——所以企业愿意为合格候选人开溢价。
        </p>
        <p>
          <strong>互联网 AI 增强供给充分：</strong>互联网公司里「会用 Copilot 的全栈」「会调 Prompt 的 PM」遍地都是——每个程序员入职第一周就在用。供给充分 = 没溢价。
        </p>
        <p>
          <strong>付费意愿：</strong>传统行业为「AI 改造业务」的预算来自数字化转型经费（一次性 capex），愿意为关键岗位开高薪；互联网公司的 AI 增强是日常 opex，倾向控制 headcount 成本。
        </p>
      </MechanismBox>

      <CaveatBox>
        <p>
          <strong>1. 不是所有传统行业都溢价。</strong>
          retail 15k、media 12.5k、education 25k——和互联网持平甚至更低。「传统行业 = 高薪」是错的，「医疗/制造/金融 = 高薪」才是事实。把 narrative 缩小到这 3 个行业。
        </p>
        <p>
          <strong>2. energy 48k 是小样本（n = 6）。</strong>
          看着最高，但样本量太小，不能作为论断主线，只能在补充图表里出现。
        </p>
        <p>
          <strong>3. 中位数不能告诉你天花板。</strong>
          表里的 p75 数据：healthcare 45k、manufacturing 45k、finance 50k——上四分位也不算特别高。这个数字适合谈「平均能给到」，不适合谈「最高能给多少」。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
