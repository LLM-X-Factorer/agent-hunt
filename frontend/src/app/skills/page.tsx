"use client";

import { useEffect, useState } from "react";
import { api, type Skill, type JobSampleGroup } from "@/lib/api";
import { skillLabel } from "@/lib/labels";
import { InsightCard } from "@/components/insight-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SkillChart } from "./chart";

const CATEGORY_LABELS: Record<string, string> = {
  language: "编程语言",
  framework: "框架",
  tool: "工具与平台",
  concept: "核心概念",
  cloud: "云服务",
};

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [samples, setSamples] = useState<Record<string, JobSampleGroup>>({});
  const [insight, setInsight] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.skills(), api.jobSamples(), api.insights()]).then(([s, sam, ins]) => {
      setSkills(s);
      setSamples(sam);
      setInsight(ins.skills_insight || "");
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const active = skills.filter((s) => s.total_count > 0);
  const categories = [...new Set(active.map((s) => s.category))];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">技能图谱</h1>
        <p className="text-gray-500 mt-1">追踪 {active.length} 个技能在国内外市场的需求分布</p>
      </div>

      {insight && <InsightCard text={insight} />}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Top 25 技能 — 国内 vs 国际</CardTitle>
        </CardHeader>
        <CardContent>
          <SkillChart skills={active.slice(0, 25)} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {categories.map((cat) => {
          const catSkills = active.filter((s) => s.category === cat).sort((a, b) => b.total_count - a.total_count);
          if (catSkills.length === 0) return null;
          return (
            <Card key={cat}>
              <CardHeader>
                <CardTitle className="text-base">{CATEGORY_LABELS[cat] || cat}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {catSkills.map((s) => (
                    <div key={s.id}>
                      <div
                        className="flex justify-between text-sm py-1.5 border-b cursor-pointer hover:bg-gray-50 px-1 rounded"
                        onClick={() => setExpanded(expanded === s.id ? null : s.id)}
                      >
                        <span className="flex items-center gap-1">
                          {samples[s.id] && <span className="text-xs text-indigo-400">▶</span>}
                          {skillLabel(s.canonical_name)}
                        </span>
                        <span className="tabular-nums text-gray-500">
                          <span className="text-red-500">{s.domestic_count}</span>
                          {" / "}
                          <span className="text-blue-500">{s.international_count}</span>
                        </span>
                      </div>
                      {expanded === s.id && samples[s.id] && (
                        <div className="ml-4 mb-2 space-y-2 mt-1">
                          {samples[s.id].jobs.map((j, i) => (
                            <div key={i} className="text-xs bg-gray-50 rounded p-3 border">
                              <div className="flex justify-between mb-1">
                                <span className="font-medium text-gray-800">{j.title}</span>
                                <span className={j.market === "国内" ? "text-red-500" : "text-blue-500"}>{j.market}</span>
                              </div>
                              <div className="text-gray-500 mb-1">{j.company} · {j.location} · {j.salary}</div>
                              <p className="text-gray-600 line-clamp-3">{j.snippet}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  <span className="text-red-500">国内</span> / <span className="text-blue-500">国际</span>
                  {" · 点击技能查看真实 JD 样本"}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
