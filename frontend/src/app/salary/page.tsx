import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SalaryCharts } from "./charts";

export default async function SalaryPage() {
  const [distribution, bySkill, byExperience, byPlatform] = await Promise.all([
    api.salaryDistribution(),
    api.salaryBySkill(15),
    api.salaryByExperience(),
    api.salaryByPlatform(),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Salary Analysis</h1>
        <p className="text-gray-500 mt-1">
          Based on {distribution.total_jobs_with_salary} jobs with salary data
        </p>
      </div>

      <SalaryCharts
        distribution={distribution}
        bySkill={bySkill}
        byExperience={byExperience}
        byPlatform={byPlatform}
      />
    </div>
  );
}
