"use client";

import { useEffect, useState } from "react";
import { NarrativeLayout } from "@/components/narrative-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Ghost {
  company: string;
  title: string;
  variant_count: number;
  markets: string[];
  platforms: string[];
}

interface Stats {
  p5_ghost: {
    intl_ghost_clusters: number;
    intl_total_jobs: number;
    intl_ghost_pct: number;
    domestic_ghost_clusters: number;
    domestic_total_jobs: number;
    domestic_ghost_pct: number;
    intl_to_domestic_ratio: number;
    top_ghost_listings: Ghost[];
  };
}

export default function P5() {
  const [s, setS] = useState<Stats | null>(null);

  useEffect(() => {
    fetch("/data/narrative-stats.json").then((r) => r.json()).then(setS);
  }, []);

  if (!s) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const g = s.p5_ghost;

  return (
    <NarrativeLayout
      index={5}
      title="预期管理 · 幽灵岗"
      headline="海外幽灵岗集中度是国内的 3 倍"
      metric={`${g.intl_to_domestic_ratio}×`}
      metricSub={`海外 ${g.intl_ghost_pct}% · 国内 ${g.domestic_ghost_pct}%（占总 JD 比）`}
      oneLiner="学员看 LinkedIn 发现海外岗位多，建议先打 30% 折扣。海外 AI 招聘里同公司同岗位重复发布远多于国内——Deloitte 一个 Full Stack Engineer 标题挂了 19 次，Meta 同样的 PM 标题 17 次。岗位数量不等于实际 hiring slot。"
      copyText="海外 LinkedIn 上同公司同岗位重复发布是国内的 3 倍。Deloitte 的 Full Stack Engineer 挂了 19 次，Meta 的 PM 17 次。海外岗位数量 ≠ hiring slot——建议先打 30% 折扣。"
      dataSource={`Ghost cluster 定义：同 company + 同 title 出现 ≥5 次（variant_count ≥ 5）。海外 ${g.intl_ghost_clusters} 簇 / ${g.intl_total_jobs} 总 JD = ${g.intl_ghost_pct}%；国内 ${g.domestic_ghost_clusters} 簇 / ${g.domestic_total_jobs} 总 JD = ${g.domestic_ghost_pct}%。完整列表见 jobs-quality-signals.json。`}
      deepLink={{ href: "/report", label: "完整洞察报告（数据看板）" }}
      prev={{ href: "/narrative/p4", label: "论断 4 · 跨市场套利" }}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">海外（LinkedIn / Indeed / vendor）</p>
            <p className="text-3xl font-bold text-rose-500">{g.intl_ghost_pct}%</p>
            <p className="text-xs text-gray-500">
              {g.intl_ghost_clusters} 个幽灵岗簇 / {g.intl_total_jobs.toLocaleString()} 总 JD
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">国内（Boss / Liepin / Lagou / vendor）</p>
            <p className="text-3xl font-bold text-emerald-600">{g.domestic_ghost_pct}%</p>
            <p className="text-xs text-gray-500">
              {g.domestic_ghost_clusters} 个幽灵岗簇 / {g.domestic_total_jobs.toLocaleString()} 总 JD
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">海外幽灵岗 Top 10（重复发布次数最高）</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            同 company + title 出现 ≥5 次的簇，按重复次数降序
          </p>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="py-2 pr-4">公司</th>
                  <th className="py-2 pr-4">岗位标题</th>
                  <th className="py-2 pr-4 text-right">重复</th>
                  <th className="py-2 pr-4">市场</th>
                  <th className="py-2">平台</th>
                </tr>
              </thead>
              <tbody>
                {g.top_ghost_listings.map((row, i) => (
                  <tr key={i} className="border-b last:border-0 text-gray-700">
                    <td className="py-2 pr-4 font-medium">{row.company}</td>
                    <td className="py-2 pr-4">{row.title}</td>
                    <td className="py-2 pr-4 text-right tabular-nums">{row.variant_count}×</td>
                    <td className="py-2 pr-4 text-xs text-gray-500">{row.markets.join("/")}</td>
                    <td className="py-2 text-xs text-gray-500">{row.platforms.join("/")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </NarrativeLayout>
  );
}
