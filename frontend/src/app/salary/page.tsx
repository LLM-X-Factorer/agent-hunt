"use client";

import { useEffect, useState } from "react";
import { api, type SalaryDistribution, type SkillSalary, type ExperienceSalary, type PlatformSalary } from "@/lib/api";
import { SalaryCharts } from "./charts";

export default function SalaryPage() {
  const [distribution, setDistribution] = useState<SalaryDistribution | null>(null);
  const [bySkill, setBySkill] = useState<SkillSalary[]>([]);
  const [byExperience, setByExperience] = useState<ExperienceSalary[]>([]);
  const [byPlatform, setByPlatform] = useState<PlatformSalary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.salaryDistribution(),
      api.salaryBySkill(15),
      api.salaryByExperience(),
      api.salaryByPlatform(),
    ]).then(([d, s, e, p]) => {
      setDistribution(d);
      setBySkill(s);
      setByExperience(e);
      setByPlatform(p);
      setLoading(false);
    });
  }, []);

  if (loading || !distribution) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">薪资分析</h1>
        <p className="text-gray-500 mt-1">基于 {distribution.total_jobs_with_salary} 条有薪资数据的 JD</p>
      </div>
      <SalaryCharts distribution={distribution} bySkill={bySkill} byExperience={byExperience} byPlatform={byPlatform} />
    </div>
  );
}
