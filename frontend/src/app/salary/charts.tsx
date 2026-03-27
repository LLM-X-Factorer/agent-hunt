"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SalaryDistribution, SkillSalary, ExperienceSalary, PlatformSalary } from "@/lib/api";
import { platformLabel, skillLabel } from "@/lib/labels";

const COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe", "#ede9fe"];

export function SalaryCharts({
  distribution, bySkill, byExperience, byPlatform,
}: {
  distribution: SalaryDistribution;
  bySkill: SkillSalary[];
  byExperience: ExperienceSalary[];
  byPlatform: PlatformSalary[];
}) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle className="text-base">薪资分布（人民币/月）</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distribution.buckets}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range_label" />
              <YAxis />
              <Tooltip formatter={(value, name) => name === "count" ? [`${value} 条`, "数量"] : [`${value}%`, "占比"]} />
              <Bar dataKey="count" name="count">
                {distribution.buckets.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle className="text-base">按经验年限</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byExperience}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="bracket" />
                <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k`, "平均月薪"]} />
                <Bar dataKey="avg_salary" fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">按平台</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byPlatform.map(p => ({...p, name: platformLabel(p.platform_id)}))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k`, "平均月薪"]} />
                <Bar dataKey="avg_salary" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">按技能（Top 15 高薪技能）</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={450}>
            <BarChart data={bySkill.map(s => ({...s, name: skillLabel(s.canonical_name)}))} layout="vertical" margin={{ left: 160 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={160} />
              <Tooltip formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k`, "平均月薪"]} />
              <Bar dataKey="avg_salary" fill="#a78bfa" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
