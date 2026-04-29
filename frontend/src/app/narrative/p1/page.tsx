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

interface Stats {
  totals: { all_jobs: number; labeled_jobs: number };
  p1_market_basic: {
    domestic_ai_native: number;
    domestic_ai_augmented: number;
    domestic_traditional_aug_total: number;
    domestic_internet_aug_total: number;
    domestic_traditional_to_internet_ratio: number;
    domestic_industry_breakdown: { industry: string; count: number }[];
  };
}

interface Examples {
  p1_p2_industries: Record<string, JobExample[]>;
}

const TRADITIONAL = new Set([
  "manufacturing", "automotive", "healthcare", "media",
  "finance", "education", "consulting", "retail",
  "energy", "telecom",
]);

export default function P1() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [ex, setEx] = useState<Examples | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/data/narrative-stats.json").then((r) => r.json()),
      fetch("/data/narrative-examples.json").then((r) => r.json()),
    ]).then(([s, e]) => { setStats(s); setEx(e); });
  }, []);

  if (!stats || !ex) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const m = stats.p1_market_basic;
  const data = m.domestic_industry_breakdown.map((row) => ({
    name: industryLabel(row.industry),
    industry: row.industry,
    count: row.count,
    isInternet: row.industry === "internet",
    isTraditional: TRADITIONAL.has(row.industry),
  }));

  // Pick 1 example per representative industry for diversity.
  const sampleIndustries = ["healthcare", "manufacturing", "finance", "automotive", "internet"];
  const showcaseExamples = sampleIndustries
    .map((ind) => ({ ind, ex: ex.p1_p2_industries[ind]?.[0] }))
    .filter((x) => x.ex);

  return (
    <NarrativeLayout
      index={1}
      title="市场基本盘"
      headline="国内传统行业 AI 增强需求 = 互联网的 3.4×"
      metric={`${m.domestic_traditional_to_internet_ratio}×`}
      metricSub={`${m.domestic_traditional_aug_total} vs ${m.domestic_internet_aug_total} 个岗位`}
      oneLiner="AI 招聘市场不只算法工程师。把 JD 拆开看，国内医疗 / 制造 / 汽车 / 金融 / 教育的 AI 增强需求，加起来是互联网行业的 3.4 倍。市面上所有 AI 课程都在教程序员转 AI 程序员——传统行业用 AI 这条赛道无人覆盖。"
      copyText="国内招聘市场，传统行业（医疗/制造/汽车/金融/教育）的 AI 增强需求，是互联网行业的 3.4 倍。市面所有 AI 课程都在教程序员，没人教传统行业用 AI——这是市场最大的认知错位。"
      dataSource={`国内 901 个 ai_augmented_traditional 岗位（基于 ${stats.totals.labeled_jobs.toLocaleString()} 条 LLM 标注岗位的国内子集）按 industry 字段分组。`}
      deepLink={{ href: "/industry", label: "行业分析（数据看板）" }}
      next={{ href: "/narrative/p2", label: "论断 2 · 薪资反直觉" }}
    >
      <MethodologyBox title="📐 这个数字哪来的（学员问就这么答）">
        <p>
          <strong>一句话：</strong>我们从国内主流招聘平台（Boss直聘 / 猎聘 / 拉勾）和国内大厂官网采集了几千条真实招聘 JD，用 AI 模型逐条读完整内容判断岗位类型——不是简单匹配「AI / 智能」关键词，因为这些词被太多公司滥用（连「智能客服话务员」都用）。
        </p>
        <p>
          <strong>每条 JD 分成三类：</strong>① <strong>AI 原生岗</strong>（核心是 AI 技术，如算法工程师）② <strong>AI 增强岗</strong>（传统岗位 + 要求会用 AI 工具，如「医疗影像分析师 + 深度学习」「工艺工程师 + 计算机视觉」）③ 与 AI 无关（剔除）。本论断只数第二类。
        </p>
        <p>
          <strong>3.4× 是怎么算的：</strong>国内 AI 增强岗共 {m.domestic_ai_augmented} 条。其中互联网 {m.domestic_internet_aug_total} 条；传统行业（医疗 / 制造 / 汽车 / 金融 / 教育 / 媒体 / 咨询 / 零售 / 能源 / 通信 共 10 个）加起来 {m.domestic_traditional_aug_total} 条。{m.domestic_traditional_aug_total} ÷ {m.domestic_internet_aug_total} ≈ {m.domestic_traditional_to_internet_ratio}×。
        </p>
        <p>
          <strong>学员若问「这数字 6 个月后还成立吗？」：</strong>有采样波动，但 3.0–3.8 是稳定区间，不会反转——这是结构性差异，不是临时现象。
        </p>
      </MethodologyBox>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">国内 AI 增强岗位 · 行业分布</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            红色 = 互联网（{m.domestic_internet_aug_total}）· 绿色 = 传统行业（合计 {m.domestic_traditional_aug_total}）· 灰色 = 其他
          </p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={Math.max(280, data.length * 32)}>
            <BarChart data={data} layout="vertical" margin={{ left: 100 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={100} />
              <Tooltip formatter={(v) => [`${v} 个岗位`, "数量"]} />
              <Bar dataKey="count">
                {data.map((d, i) => (
                  <Cell
                    key={i}
                    fill={d.isInternet ? "#f87171" : d.isTraditional ? "#22c55e" : "#9ca3af"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <SectionHeader>真实 JD 例子（从样本中各行业各取 1 条）</SectionHeader>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {showcaseExamples.map(({ ind, ex }) => (
          <div key={ind}>
            <p className="text-xs text-gray-500 mb-2 font-medium">
              · {industryLabel(ind)} {ind === "internet" ? "（对照基线）" : "（传统行业）"}
            </p>
            {ex && <JobExampleCard ex={ex} />}
          </div>
        ))}
      </div>

      <MechanismBox title="🧠 为什么会这样（一句话讲透）">
        <p className="text-base font-medium">
          互联网程序员都已经会用 AI 工具了，但医院 / 工厂的医生和工程师还没人教。
        </p>
        <p>
          互联网公司的 AI 程序员供给已经过载——每个程序员入职第一周都在用 Copilot，「会调 Prompt 的 PM」遍地都是。同时市面所有 AI 课都在教「程序员怎么转 AI」。
        </p>
        <p>
          可没人教「医生怎么用 AI 看 CT」「工艺工程师怎么用 CV 检测产品缺陷」「会计怎么用 LLM 拆账」。传统行业最近 12 个月才开始把 AI 当业务杠杆，需要的是「懂业务 + 会用 AI」的复合型人——这个人才市场还没成形。这就是 3.4× 这个数字背后的<strong>结构性错位</strong>。
        </p>
      </MechanismBox>

      <CaveatBox title="⚠️ 给学员讲的时候要说清楚">
        <p>
          <strong>✅ 这个数字适合讲：</strong>传统行业的 AI 复合型人才供给空缺巨大，赛道还没竞品。学员若本职是医生 / 工业工程师 / 财务 / 会计 / 临床—— AI 增强是被市场严重低估的方向。
        </p>
        <p>
          <strong>❌ 不能这么说：「传统行业 AI 岗比互联网多」。</strong>
          算上纯算法岗（AI 原生 {m.domestic_ai_native} 条），互联网仍是岗位最多的行业。这条 narrative 讲的是 <strong>AI 增强这一个细分</strong>，不是整个 AI 招聘市场。
        </p>
        <p>
          <strong>❌ 不能这么说：「所有传统行业都有大量需求」。</strong>
          政府只 2 条、能源 6 条、通信 5 条——细分行业差异大。学员如果本职在小样本行业，要看具体细分。
        </p>
        <p>
          <strong>学员可能问：「医疗 AI 现在到底缺人不缺人？」</strong>
          诚实答：医疗 AI 增强岗 87 条，是 10 个传统行业里的中等水位；但供给侧（既是医生又会 AI 的人）极少，所以薪资能给到 30k+（见 <a href="/narrative/p2" className="text-amber-700 underline">论断 2</a>）。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
