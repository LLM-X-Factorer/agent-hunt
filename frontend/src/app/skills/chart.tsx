"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import type { Skill } from "@/lib/api";
import { skillLabel } from "@/lib/labels";

export function SkillChart({ skills }: { skills: Skill[] }) {
  const data = skills.map((s) => ({
    name: skillLabel(s.canonical_name),
    国内: s.domestic_count,
    国际: s.international_count,
  }));

  return (
    <ResponsiveContainer width="100%" height={500}>
      <BarChart data={data} layout="vertical" margin={{ left: 120 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={120} />
        <Tooltip />
        <Legend />
        <Bar dataKey="国内" fill="#f87171" />
        <Bar dataKey="国际" fill="#60a5fa" />
      </BarChart>
    </ResponsiveContainer>
  );
}
