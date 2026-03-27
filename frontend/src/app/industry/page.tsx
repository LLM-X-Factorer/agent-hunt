"use client";

import { useEffect, useState } from "react";
import { api, type IndustrySummary, type IndustrySalary } from "@/lib/api";
import { industryLabel, skillLabel } from "@/lib/labels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { IndustryCharts } from "./charts";

export default function IndustryPage() {
  const [overview, setOverview] = useState<IndustrySummary[]>([]);
  const [salary, setSalary] = useState<IndustrySalary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.industryOverview(), api.industrySalary()]).then(([o, s]) => {
      setOverview(o);
      setSalary(s);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  if (overview.length === 0) {
    return (
      <div className="text-center py-20 text-gray-400">
        行业数据正在生成中，请稍后刷新...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">行业 AI 渗透分析</h1>
        <p className="text-gray-500 mt-1">
          AI 岗位在各行业的分布、技能需求和薪资对比
        </p>
      </div>

      <IndustryCharts overview={overview} salary={salary} />

      {/* Industry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {overview.map((ind) => (
          <Card key={ind.industry}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">
                {industryLabel(ind.industry)}
              </CardTitle>
              <p className="text-xs text-gray-500">
                {ind.job_count} 个岗位 · 国内 {ind.domestic_count} / 国际{" "}
                {ind.international_count}
              </p>
            </CardHeader>
            <CardContent className="space-y-3">
              {ind.avg_salary && (
                <div className="text-sm">
                  <span className="text-gray-500">平均月薪：</span>
                  <span className="font-medium">
                    ¥{(ind.avg_salary / 1000).toFixed(0)}k
                  </span>
                </div>
              )}
              <div>
                <p className="text-xs text-gray-500 mb-1">热门技能</p>
                <div className="flex flex-wrap gap-1">
                  {ind.top_skills.map((s) => (
                    <Badge key={s.skill_id} variant="secondary" className="text-xs">
                      {skillLabel(s.skill_id)} ({s.count})
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
