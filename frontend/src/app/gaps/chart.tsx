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
  ReferenceLine,
} from "recharts";
import type { SkillGap } from "@/lib/api";

export function GapChart({ gaps }: { gaps: SkillGap[] }) {
  const data = gaps.map((g) => ({
    name: g.canonical_name,
    domestic: g.domestic_pct,
    international: -g.international_pct,
    dominant: g.dominant_market,
  }));

  return (
    <ResponsiveContainer width="100%" height={500}>
      <BarChart data={data} layout="vertical" margin={{ left: 140 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          type="number"
          tickFormatter={(v) => `${Math.abs(v)}%`}
          domain={["dataMin - 5", "dataMax + 5"]}
        />
        <YAxis
          dataKey="name"
          type="category"
          tick={{ fontSize: 12 }}
          width={140}
        />
        <Tooltip
          formatter={(value, name) => [
            `${Math.abs(Number(value)).toFixed(1)}%`,
            name === "domestic" ? "Domestic" : "International",
          ]}
        />
        <Legend />
        <ReferenceLine x={0} stroke="#666" />
        <Bar dataKey="domestic" fill="#f87171" name="Domestic %" />
        <Bar dataKey="international" fill="#60a5fa" name="International %" />
      </BarChart>
    </ResponsiveContainer>
  );
}
