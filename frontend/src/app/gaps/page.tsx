import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GapChart } from "./chart";

export default async function GapsPage() {
  const [overview, gaps] = await Promise.all([
    api.crossMarketOverview(),
    api.skillGaps(),
  ]);

  const dom = overview.domestic;
  const intl = overview.international;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Cross-Market Skill Gaps</h1>
        <p className="text-gray-500 mt-1">
          Comparing domestic ({dom.total_jobs} jobs) vs international (
          {intl.total_jobs} jobs) AI Agent job markets
        </p>
      </div>

      {/* Market Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MarketCard title="Domestic (China)" data={dom} color="red" />
        <MarketCard title="International" data={intl} color="blue" />
      </div>

      {/* Gap Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Skill Demand Gap — Domestic vs International
          </CardTitle>
        </CardHeader>
        <CardContent>
          <GapChart gaps={gaps.slice(0, 20)} />
        </CardContent>
      </Card>

      {/* Gap Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Full Gap Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="py-2 pr-4">Skill</th>
                  <th className="py-2 pr-4 text-right">Domestic %</th>
                  <th className="py-2 pr-4 text-right">International %</th>
                  <th className="py-2 pr-4 text-right">Gap</th>
                  <th className="py-2">Dominant</th>
                </tr>
              </thead>
              <tbody>
                {gaps.map((g) => (
                  <tr key={g.skill_id} className="border-b last:border-0">
                    <td className="py-2 pr-4 font-medium">{g.canonical_name}</td>
                    <td className="py-2 pr-4 text-right text-red-600">
                      {g.domestic_pct}%
                    </td>
                    <td className="py-2 pr-4 text-right text-blue-600">
                      {g.international_pct}%
                    </td>
                    <td className="py-2 pr-4 text-right font-mono">
                      {g.gap.toFixed(1)}
                    </td>
                    <td className="py-2">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          g.dominant_market === "domestic"
                            ? "bg-red-100 text-red-700"
                            : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {g.dominant_market}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function MarketCard({
  title,
  data,
  color,
}: {
  title: string;
  data: {
    total_jobs: number;
    avg_salary: number | null;
    median_salary: number | null;
    work_mode: Record<string, number>;
    education: Record<string, number>;
  };
  color: "red" | "blue";
}) {
  const accent = color === "red" ? "text-red-600" : "text-blue-600";
  return (
    <Card>
      <CardHeader>
        <CardTitle className={`text-base ${accent}`}>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Total Jobs</span>
          <span className="font-medium">{data.total_jobs}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Avg Salary</span>
          <span className="font-medium">
            ¥{((data.avg_salary || 0) / 1000).toFixed(0)}k/mo
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Median Salary</span>
          <span className="font-medium">
            ¥{((data.median_salary || 0) / 1000).toFixed(0)}k/mo
          </span>
        </div>
        <div className="border-t pt-2 mt-2">
          <p className="text-gray-500 mb-1">Work Mode</p>
          <div className="flex gap-3 text-xs">
            {Object.entries(data.work_mode)
              .filter(([, v]) => v > 0)
              .map(([k, v]) => (
                <span key={k} className="bg-gray-100 px-2 py-0.5 rounded">
                  {k}: {v}
                </span>
              ))}
          </div>
        </div>
        <div className="border-t pt-2">
          <p className="text-gray-500 mb-1">Education</p>
          <div className="flex gap-3 text-xs">
            {Object.entries(data.education)
              .filter(([, v]) => v > 0)
              .map(([k, v]) => (
                <span key={k} className="bg-gray-100 px-2 py-0.5 rounded">
                  {k}: {v}
                </span>
              ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
