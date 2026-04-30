"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ChartDatum {
  skill: string;
  required: number;
  preferred: number;
}

export function SkillBarChart({
  data,
  accent,
}: {
  data: ChartDatum[];
  accent: "red" | "blue";
}) {
  const requiredColor = accent === "red" ? "#f87171" : "#60a5fa";
  const preferredColor = accent === "red" ? "#fca5a5" : "#93c5fd";
  const height = Math.max(220, data.length * 30);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" tick={{ fontSize: 11 }} />
        <YAxis
          dataKey="skill"
          type="category"
          tick={{ fontSize: 12 }}
          width={130}
        />
        <Tooltip cursor={{ fill: "#f3f4f6" }} />
        <Legend />
        <Bar dataKey="required" name="Required" fill={requiredColor} />
        <Bar dataKey="preferred" name="Preferred" fill={preferredColor} />
      </BarChart>
    </ResponsiveContainer>
  );
}
