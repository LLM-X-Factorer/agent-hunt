"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { NarrativeLayout } from "@/components/narrative-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { industryLabel } from "@/lib/labels";

interface Stats {
  p1_market_basic: {
    domestic_traditional_aug_total: number;
    domestic_internet_aug_total: number;
    domestic_traditional_to_internet_ratio: number;
    domestic_industry_breakdown: { industry: string; count: number }[];
  };
}

const TRADITIONAL = new Set([
  "manufacturing", "automotive", "healthcare", "media",
  "finance", "education", "consulting", "retail",
  "energy", "telecom",
]);

export default function P1() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetch("/data/narrative-stats.json").then((r) => r.json()).then(setStats);
  }, []);

  if (!stats) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const m = stats.p1_market_basic;
  const data = m.domestic_industry_breakdown.map((row) => ({
    name: industryLabel(row.industry),
    industry: row.industry,
    count: row.count,
    isInternet: row.industry === "internet",
    isTraditional: TRADITIONAL.has(row.industry),
  }));

  return (
    <NarrativeLayout
      index={1}
      title="市场基本盘"
      headline="国内传统行业 AI 增强需求 = 互联网的 3.4×"
      metric={`${m.domestic_traditional_to_internet_ratio}×`}
      metricSub={`${m.domestic_traditional_aug_total} vs ${m.domestic_internet_aug_total} 个岗位`}
      oneLiner="AI 招聘市场不只算法工程师。把 JD 拆开看，国内医疗 / 制造 / 汽车 / 金融 / 教育的 AI 增强需求，加起来是互联网行业的 3.4 倍。市面上所有 AI 课程都在教程序员转 AI 程序员——传统行业用 AI 这条赛道无人覆盖。这是市场最大的认知错位。"
      copyText="国内招聘市场，传统行业（医疗/制造/汽车/金融/教育）的 AI 增强需求，是互联网行业的 3.4 倍。市面所有 AI 课程都在教程序员，没人教传统行业用 AI——这是市场最大的认知错位。"
      dataSource="国内 901 个 ai_augmented_traditional 岗位 LLM 标注后按 industry 字段分组（基于 5673 条 LLM-labeled 中的国内子集）。完整 query 见 docs/agent-hunt/next-tasks.md。"
      deepLink={{ href: "/industry", label: "行业分析（数据看板）" }}
      next={{ href: "/narrative/p2", label: "论断 2 · 薪资反直觉" }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base">国内 AI 增强岗位 · 行业分布</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            红色 = 互联网（197）· 绿色 = 传统行业（合计 {m.domestic_traditional_aug_total}）· 灰色 = 其他
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">传统行业合计（10 个细分）</p>
            <p className="text-3xl font-bold text-emerald-600">{m.domestic_traditional_aug_total}</p>
            <p className="text-xs text-gray-500">医疗 / 制造 / 汽车 / 金融 / 教育 / 媒体 / 咨询 / 零售 / 能源 / 通信</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">互联网行业 AI 增强</p>
            <p className="text-3xl font-bold text-rose-500">{m.domestic_internet_aug_total}</p>
            <p className="text-xs text-gray-500">含 SaaS / 电商 / 内容平台等</p>
          </CardContent>
        </Card>
      </div>
    </NarrativeLayout>
  );
}
