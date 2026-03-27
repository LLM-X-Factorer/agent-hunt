"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { Skill } from "@/lib/api";

export function SkillChart({ skills }: { skills: Skill[] }) {
  const data = skills.map((s) => ({
    name: s.canonical_name,
    domestic: s.domestic_count,
    international: s.international_count,
  }));

  return (
    <ResponsiveContainer width="100%" height={500}>
      <BarChart data={data} layout="vertical" margin={{ left: 120 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={120} />
        <Tooltip />
        <Legend />
        <Bar dataKey="domestic" fill="#f87171" name="Domestic" />
        <Bar dataKey="international" fill="#60a5fa" name="International" />
      </BarChart>
    </ResponsiveContainer>
  );
}
