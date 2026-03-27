"use client";

import { useEffect, useState } from "react";
import { api, type Skill } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SkillChart } from "./chart";

const CATEGORY_LABELS: Record<string, string> = {
  language: "编程语言",
  framework: "框架",
  tool: "工具",
  concept: "概念",
  cloud: "云平台",
};

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.skills().then((s) => { setSkills(s); setLoading(false); });
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
                <div className="space-y-2">
                  {catSkills.map((s) => (
                    <div key={s.id} className="flex justify-between text-sm py-1 border-b last:border-0">
                      <span>{s.canonical_name}</span>
                      <span className="tabular-nums text-gray-500">
                        <span className="text-red-500">{s.domestic_count}</span>
                        {" / "}
                        <span className="text-blue-500">{s.international_count}</span>
                      </span>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  <span className="text-red-500">国内</span> / <span className="text-blue-500">国际</span>
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
