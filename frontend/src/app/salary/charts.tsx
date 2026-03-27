"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type {
  SalaryDistribution,
  SkillSalary,
  ExperienceSalary,
  PlatformSalary,
} from "@/lib/api";

const COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#a78bfa",
  "#c4b5fd",
  "#ddd6fe",
  "#ede9fe",
];

export function SalaryCharts({
  distribution,
  bySkill,
  byExperience,
  byPlatform,
}: {
  distribution: SalaryDistribution;
  bySkill: SkillSalary[];
  byExperience: ExperienceSalary[];
  byPlatform: PlatformSalary[];
}) {
  return (
    <div className="space-y-6">
      {/* Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Salary Distribution (RMB/month)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distribution.buckets}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range_label" />
              <YAxis />
              <Tooltip
                formatter={(value, name) =>
                  name === "count"
                    ? [`${value} jobs`, "Count"]
                    : [`${value}%`, "Percentage"]
                }
              />
              <Bar dataKey="count" name="count">
                {distribution.buckets.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Experience */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Avg Salary by Experience</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byExperience}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="bracket" />
                <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k`, "Avg Salary"]}
                />
                <Bar dataKey="avg_salary" fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* By Platform */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Avg Salary by Platform</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byPlatform}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="platform_id" />
                <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k`, "Avg Salary"]}
                />
                <Bar dataKey="avg_salary" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* By Skill */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Avg Salary by Skill (Top 15)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={450}>
            <BarChart
              data={bySkill}
              layout="vertical"
              margin={{ left: 140 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              />
              <YAxis
                dataKey="canonical_name"
                type="category"
                tick={{ fontSize: 12 }}
                width={140}
              />
              <Tooltip
                formatter={(v) => [`¥${(Number(v) / 1000).toFixed(1)}k`, "Avg Salary"]}
              />
              <Bar dataKey="avg_salary" fill="#a78bfa" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
