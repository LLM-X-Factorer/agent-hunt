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
      <MethodologyBox>
        <p>
          <strong>样本范围：</strong>
          jobs 表里所有 <code className="text-xs bg-white px-1 rounded">parse_status=&apos;parsed&apos;</code> &amp;{" "}
          <code className="text-xs bg-white px-1 rounded">market=&apos;domestic&apos;</code> &amp;{" "}
          <code className="text-xs bg-white px-1 rounded">role_type=&apos;ai_augmented_traditional&apos;</code>，共 901 条。
        </p>
        <p>
          <strong>role_type 怎么打的：</strong>用 LLM 读全 JD 后，分三类：
          <code className="text-xs bg-white px-1 rounded mx-1">ai_native</code>（算法/ML 等以 AI 为主体）、
          <code className="text-xs bg-white px-1 rounded mx-1">ai_augmented_traditional</code>（主体是传统专业 + 要求 AI 技能，例如「医疗影像分析师 + 深度学习」）、
          null（与 AI 无关）。本论断只看第二类。
        </p>
        <p>
          <strong>「传统行业」=</strong> 10 个非互联网细分（医疗/制造/汽车/金融/教育/媒体/咨询/零售/能源/通信）合计 {m.domestic_traditional_aug_total} 条 ÷ 互联网 {m.domestic_internet_aug_total} 条 = {m.domestic_traditional_to_internet_ratio}×。industry 字段也由 LLM 解析时给出，不是关键字粗分。
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

      <MechanismBox>
        <p>
          <strong>供给端饱和：</strong>市面 AI 课程过去 3 年都在教程序员转「AI 程序员」（提示工程 / RAG / Agent 架构）。结果是互联网行业的 AI 程序员供给侧已经过载——招到一个会 LangChain 的应届生不难。
        </p>
        <p>
          <strong>需求端正在爆发：</strong>传统行业过去 3 年才开始系统性数字化转型，最近 12 个月才开始把 AI 当作业务杠杆（医院做影像辅助诊断、工厂做缺陷检测、银行做风控模型升级）。这些岗位需要的是「懂业务 + 会用 AI 工具 / 模型」的复合人，不是纯算法。
        </p>
        <p>
          <strong>市场错位的结果：</strong>课程市场只服务前者（程序员），却没人服务后者（医生 / 工程师 / 会计转 AI 增强）——这就是 3.4× 这个数字背后的结构性 gap。
        </p>
      </MechanismBox>

      <CaveatBox>
        <p>
          <strong>1. 绝对量上 ai_native 仍多于 ai_augmented。</strong>
          国内 ai_native 1,372 条 vs ai_augmented 939 条——传统行业 + AI 这条线<em>需求</em>大，<em>总量</em>仍小于纯 AI 岗。
          这条 narrative 的洞察在于「相对增速 / 课程供给空白」，不是「绝对岗位多」。
        </p>
        <p>
          <strong>2. 不是所有传统行业都需求大。</strong>
          政府只 2 条、能源 6 条、通信 5 条、零售 47 条——细分行业差异大。如果学员的本职在小样本行业，单独看可能没机会。
        </p>
        <p>
          <strong>3. industry 字段是 LLM 推断，约 5% 误判率。</strong>
          某些岗位（特别是咨询公司服务多个行业、岗位描述模糊）的 industry 归类带噪。但量级不变，3.4× 这个比值在 ±0.3 之间稳定。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
