"use client";

import { useEffect, useState } from "react";
import { api, type MarketOverview, type SkillGap } from "@/lib/api";
import { skillLabel } from "@/lib/labels";
import { InsightCard } from "@/components/insight-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GapChart } from "./chart";

export default function GapsPage() {
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [gaps, setGaps] = useState<SkillGap[]>([]);
  const [insight, setInsight] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.crossMarketOverview(), api.skillGaps(), api.insights()]).then(([o, g, ins]) => {
      setOverview(o);
      setGaps(g);
      setInsight(ins.gaps_insight || "");
      setLoading(false);
    });
  }, []);

  if (loading || !overview) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const dom = overview.domestic;
  const intl = overview.international;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">跨市场技能差异</h1>
        <p className="text-gray-500 mt-1">
          对比国内（{dom.total_jobs} 条）与国际（{intl.total_jobs} 条）AI Agent 岗位需求
        </p>
      </div>

      {insight && <InsightCard text={insight} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MarketCard title="国内市场" data={dom} color="red" />
        <MarketCard title="国际市场" data={intl} color="blue" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">技能需求差异图 — 国内 vs 国际</CardTitle>
        </CardHeader>
        <CardContent>
          <GapChart gaps={gaps.slice(0, 20)} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">完整差异分析表</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="py-2 pr-4">技能</th>
                  <th className="py-2 pr-4 text-right">国内占比</th>
                  <th className="py-2 pr-4 text-right">国际占比</th>
                  <th className="py-2 pr-4 text-right">差异</th>
                  <th className="py-2">主导市场</th>
                </tr>
              </thead>
              <tbody>
                {gaps.map((g) => (
                  <tr key={g.skill_id} className="border-b last:border-0">
                    <td className="py-2 pr-4 font-medium">{skillLabel(g.canonical_name)}</td>
                    <td className="py-2 pr-4 text-right text-red-600">{g.domestic_pct}%</td>
                    <td className="py-2 pr-4 text-right text-blue-600">{g.international_pct}%</td>
                    <td className="py-2 pr-4 text-right font-mono">{g.gap.toFixed(1)}</td>
                    <td className="py-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        g.dominant_market === "domestic" ? "bg-red-100 text-red-700" : "bg-blue-100 text-blue-700"
                      }`}>
                        {g.dominant_market === "domestic" ? "国内" : "国际"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function MarketCard({ title, data, color }: {
  title: string;
  data: { total_jobs: number; avg_salary: number | null; median_salary: number | null; work_mode: Record<string, number>; education: Record<string, number> };
  color: "red" | "blue";
}) {
  const accent = color === "red" ? "text-red-600" : "text-blue-600";
  const WORK_MODE_ZH: Record<string, string> = { onsite: "现场", remote: "远程", hybrid: "混合", unknown: "未知" };
  const EDU_ZH: Record<string, string> = { bachelor: "本科", master: "硕士", phd: "博士", any_or_unspecified: "不限" };

  return (
    <Card>
      <CardHeader><CardTitle className={`text-base ${accent}`}>{title}</CardTitle></CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="flex justify-between"><span className="text-gray-500">JD 总数</span><span className="font-medium">{data.total_jobs}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">平均月薪</span><span className="font-medium">¥{((data.avg_salary || 0) / 1000).toFixed(0)}k</span></div>
        <div className="flex justify-between"><span className="text-gray-500">中位月薪</span><span className="font-medium">¥{((data.median_salary || 0) / 1000).toFixed(0)}k</span></div>
        <div className="border-t pt-2 mt-2">
          <p className="text-gray-500 mb-1">工作模式</p>
          <div className="flex gap-3 text-xs flex-wrap">
            {Object.entries(data.work_mode).filter(([, v]) => v > 0).map(([k, v]) => (
              <span key={k} className="bg-gray-100 px-2 py-0.5 rounded">{WORK_MODE_ZH[k] || k}: {v}</span>
            ))}
          </div>
        </div>
        <div className="border-t pt-2">
          <p className="text-gray-500 mb-1">学历要求</p>
          <div className="flex gap-3 text-xs flex-wrap">
            {Object.entries(data.education).filter(([, v]) => v > 0).map(([k, v]) => (
              <span key={k} className="bg-gray-100 px-2 py-0.5 rounded">{EDU_ZH[k] || k}: {v}</span>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
