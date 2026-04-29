"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { NarrativeLayout } from "@/components/narrative-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Bucket {
  median: number;
  sample_size: number;
}

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

export default function P4() {
  const [s, setS] = useState<Stats | null>(null);

  useEffect(() => {
    fetch("/data/narrative-stats.json").then((r) => r.json()).then(setS);
  }, []);

  if (!s) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const m = s.p4_cross_market;
  const chart = [
    { name: "AI 原生", 国内: m.domestic_native.median, 海外: m.intl_native.median },
    { name: "AI 增强", 国内: m.domestic_augmented.median, 海外: m.intl_augmented.median },
  ];

  return (
    <NarrativeLayout
      index={4}
      title="跨市场套利"
      headline="海外 AI 增强岗薪资是国内的 4.6 倍"
      metric={`${m.augmented_intl_to_domestic_ratio}×`}
      metricSub={`AI 原生 ${m.native_intl_to_domestic_ratio}× · AI 增强 ${m.augmented_intl_to_domestic_ratio}×`}
      oneLiner="学员要不要出海？看薪资差。AI 原生海外是国内 3.96 倍；AI 增强海外是国内 4.6 倍——出海做 AI 增强反而比出海做 AI 原生套利空间更大。传统行业 + AI + 海外是三重叠加。"
      copyText="AI 原生海外是国内 4 倍，AI 增强海外是国内 4.6 倍。出海做 AI 增强反而比做 AI 原生套利更大——传统行业 + AI + 海外是三重叠加。"
      dataSource={`国内 ${m.domestic_native.sample_size + m.domestic_augmented.sample_size} 条 + 海外 ${m.intl_native.sample_size + m.intl_augmented.sample_size} 条 LLM 标注岗位的 salary_min/max 中位数（CNY 月薪等价）。海外岗位薪资按汇率折算。`}
      deepLink={{ href: "/gaps", label: "市场差异（数据看板）" }}
      prev={{ href: "/narrative/p3", label: "论断 3 · 桥梁工程师" }}
      next={{ href: "/narrative/p5", label: "论断 5 · 预期管理" }}
    >
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
    </NarrativeLayout>
  );
}
