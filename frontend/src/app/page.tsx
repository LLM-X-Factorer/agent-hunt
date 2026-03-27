"use client";

import { useEffect, useState } from "react";
import { api, type Skill, type CooccurrenceResult, type MarketOverview, type JobListResponse } from "@/lib/api";
import { skillLabel } from "@/lib/labels";
import { InsightCard } from "@/components/insight-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function Dashboard() {
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [cooccurrence, setCooccurrence] = useState<CooccurrenceResult | null>(null);
  const [jobData, setJobData] = useState<JobListResponse | null>(null);
  const [insight, setInsight] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.crossMarketOverview(),
      api.skills(),
      api.cooccurrence(),
      api.jobCount(),
      api.insights(),
    ]).then(([o, s, c, j, ins]) => {
      setOverview(o);
      setSkills(s);
      setCooccurrence(c);
      setJobData(j);
      setInsight(ins.dashboard_insight || "");
      setLoading(false);
    });
  }, []);

  if (loading || !overview || !jobData || !cooccurrence) {
    return <div className="text-center py-20 text-gray-400">加载中...</div>;
  }

  const topSkills = skills.filter((s) => s.total_count > 0).slice(0, 10);
  const dom = overview.domestic;
  const intl = overview.international;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">AI Agent 岗位市场总览</h1>
        <p className="text-gray-500 mt-1">
          共 {jobData.total} 条 JD，覆盖国内 {dom.total_jobs} 条 + 国际 {intl.total_jobs} 条
        </p>
      </div>

      {insight && <InsightCard text={insight} />}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="JD 总量" value={jobData.total} sub={`${dom.total_jobs} 国内 + ${intl.total_jobs} 国际`} />
        <StatCard
          title="国内平均月薪"
          value={`¥${((dom.avg_salary || 0) / 1000).toFixed(0)}k`}
          sub={`中位数 ¥${((dom.median_salary || 0) / 1000).toFixed(0)}k/月`}
        />
        <StatCard
          title="国际平均月薪"
          value={`¥${((intl.avg_salary || 0) / 1000).toFixed(0)}k`}
          sub={`中位数 ¥${((intl.median_salary || 0) / 1000).toFixed(0)}k/月（折合人民币）`}
        />
        <StatCard
          title="追踪技能数"
          value={skills.filter((s) => s.total_count > 0).length}
          sub={`技能库共 ${skills.length} 个`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top 10 热门技能</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topSkills.map((s, i) => (
                <div key={s.id} className="flex items-center gap-3">
                  <span className="text-sm text-gray-400 w-5">{i + 1}</span>
                  <div className="flex-1">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{skillLabel(s.canonical_name)}</span>
                      <span className="text-gray-500">{s.total_count}</span>
                    </div>
                    <div className="mt-1 flex h-2 rounded-full overflow-hidden bg-gray-100">
                      <div className="bg-red-400" style={{ width: `${(s.domestic_count / s.total_count) * 100}%` }} />
                      <div className="bg-blue-400" style={{ width: `${(s.international_count / s.total_count) * 100}%` }} />
                    </div>
                  </div>
                </div>
              ))}
              <div className="flex gap-4 text-xs text-gray-400 pt-2">
                <span className="flex items-center gap-1"><span className="w-3 h-2 bg-red-400 rounded" /> 国内</span>
                <span className="flex items-center gap-1"><span className="w-3 h-2 bg-blue-400 rounded" /> 国际</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">技能共现 Top 10</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {cooccurrence.top_pairs.map((p) => (
                <div key={`${p.skill_a}-${p.skill_b}`} className="flex justify-between text-sm py-1.5 border-b last:border-0">
                  <span>{skillLabel(p.skill_a_name)} <span className="text-gray-400">+</span> {skillLabel(p.skill_b_name)}</span>
                  <span className="text-gray-500 tabular-nums">
                    {p.cooccurrence_count}次
                    <span className="text-xs ml-1 text-gray-400">J={p.jaccard_index.toFixed(2)}</span>
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-400 mt-3">
              基于 {cooccurrence.total_jobs_analyzed} 条 JD 分析，J = Jaccard 相似系数
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickLink href="/skills" title="技能图谱" desc="完整技能排名，国内外对比视图" />
        <QuickLink href="/salary" title="薪资分析" desc="分布直方图，按技能/经验/平台切分" />
        <QuickLink href="/gaps" title="市场差异" desc="哪些技能在哪个市场更受欢迎" />
      </div>
    </div>
  );
}

function StatCard({ title, value, sub }: { title: string; value: string | number; sub: string }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        <p className="text-xs text-gray-400 mt-1">{sub}</p>
      </CardContent>
    </Card>
  );
}

function QuickLink({ href, title, desc }: { href: string; title: string; desc: string }) {
  return (
    <Link href={href}>
      <Card className="hover:border-gray-300 transition-colors cursor-pointer h-full">
        <CardContent className="pt-6">
          <p className="font-medium">{title}</p>
          <p className="text-sm text-gray-500 mt-1">{desc}</p>
        </CardContent>
      </Card>
    </Link>
  );
}
