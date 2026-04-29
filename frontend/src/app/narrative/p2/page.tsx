"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { NarrativeLayout } from "@/components/narrative-layout";
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

const PREMIUM = new Set(["healthcare", "manufacturing", "finance"]);

export default function P2() {
  const [d, setD] = useState<Data | null>(null);

  useEffect(() => {
    fetch("/data/industry-augmented-salary.json").then((r) => r.json()).then(setD);
  }, []);

  if (!d) return <div className="text-center py-20 text-gray-400">加载中...</div>;

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
      oneLiner="学员心里默认「互联网 = 高薪」，结果在 AI 增强方向反向走——互联网公司给『懂 AI 的非算法岗』开 25k；医疗 / 制造 / 金融开 30k；能源开 48k（小样本）。传统行业反而能给 20% 溢价。"
      copyText="国内 AI 增强岗位，互联网公司开 25k；医疗 / 制造 / 金融开 30k——传统行业比互联网高 20%。学员心里默认『互联网=高薪』，结果在 AI 增强方向反向走。"
      dataSource={`基于 ${d.total_jobs} 个国内 ai_augmented_traditional 岗位的 salary_min/max 中位数（仅含薪资样本 ≥5 的行业）。Premium 组 = healthcare + manufacturing + finance（合计 ${d.comparison.premium_traditional_sample_size} 条样本）vs internet（${d.comparison.internet_sample_size} 条）。`}
      deepLink={{ href: "/salary", label: "薪资分析（数据看板）" }}
      prev={{ href: "/narrative/p1", label: "论断 1 · 市场基本盘" }}
      next={{ href: "/narrative/p3", label: "论断 3 · 桥梁工程师" }}
    >
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">高薪传统行业组（医疗/制造/金融）</p>
            <p className="text-3xl font-bold text-amber-600">¥{(d.comparison.premium_traditional_median / 1000).toFixed(0)}k</p>
            <p className="text-xs text-gray-500">中位月薪 · n = {d.comparison.premium_traditional_sample_size}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">互联网行业</p>
            <p className="text-3xl font-bold text-rose-500">¥{(d.comparison.internet_median / 1000).toFixed(0)}k</p>
            <p className="text-xs text-gray-500">中位月薪 · n = {d.comparison.internet_sample_size}</p>
          </CardContent>
        </Card>
      </div>
    </NarrativeLayout>
  );
}
