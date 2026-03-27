"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { industryLabel } from "@/lib/labels";
import type { IndustrySummary, IndustrySalary } from "@/lib/api";

const COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#ec4899", "#f43f5e", "#f97316", "#eab308", "#22c55e", "#14b8a6", "#06b6d4", "#3b82f6", "#8b5cf6"];

export function IndustryCharts({
  overview, salary,
}: {
  overview: IndustrySummary[];
  salary: IndustrySalary[];
}) {
  const jobData = overview.map((o, i) => ({
    name: industryLabel(o.industry),
    国内: o.domestic_count,
    国际: o.international_count,
  }));

  const salaryData = salary.map((s) => ({
    name: industryLabel(s.industry),
    avg_salary: s.avg_salary,
    job_count: s.job_count,
  }));

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">各行业 AI 岗位数量（国内 vs 国际）</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={jobData} layout="vertical" margin={{ left: 120 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={120} />
              <Tooltip />
              <Legend />
              <Bar dataKey="国内" fill="#f87171" />
              <Bar dataKey="国际" fill="#60a5fa" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">各行业 AI 岗位平均月薪</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={salaryData} layout="vertical" margin={{ left: 120 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={120} />
              <Tooltip formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k`, "平均月薪"]} />
              <Bar dataKey="avg_salary">
                {salaryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
