import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default async function Dashboard() {
  const [overview, skills, cooccurrence, jobData] = await Promise.all([
    api.crossMarketOverview(),
    api.skills(),
    api.cooccurrence(10),
    api.jobCount(),
  ]);

  const topSkills = skills.filter((s) => s.total_count > 0).slice(0, 10);
  const dom = overview.domestic;
  const intl = overview.international;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">AI Agent Job Market Dashboard</h1>
        <p className="text-gray-500 mt-1">
          {jobData.total} JDs across {dom.total_jobs + intl.total_jobs} parsed,
          covering domestic and international markets
        </p>
      </div>

      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total JDs"
          value={jobData.total}
          sub={`${dom.total_jobs} domestic + ${intl.total_jobs} international`}
        />
        <StatCard
          title="Domestic Avg Salary"
          value={`¥${((dom.avg_salary || 0) / 1000).toFixed(0)}k`}
          sub={`Median ¥${((dom.median_salary || 0) / 1000).toFixed(0)}k/mo`}
        />
        <StatCard
          title="International Avg Salary"
          value={`¥${((intl.avg_salary || 0) / 1000).toFixed(0)}k`}
          sub={`Median ¥${((intl.median_salary || 0) / 1000).toFixed(0)}k/mo (RMB equiv.)`}
        />
        <StatCard
          title="Skills Tracked"
          value={skills.filter((s) => s.total_count > 0).length}
          sub={`${skills.length} total in taxonomy`}
        />
      </div>

      {/* Top Skills */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top 10 Skills</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topSkills.map((s, i) => (
                <div key={s.id} className="flex items-center gap-3">
                  <span className="text-sm text-gray-400 w-5">{i + 1}</span>
                  <div className="flex-1">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{s.canonical_name}</span>
                      <span className="text-gray-500">{s.total_count}</span>
                    </div>
                    <div className="mt-1 flex h-2 rounded-full overflow-hidden bg-gray-100">
                      <div
                        className="bg-red-400"
                        style={{
                          width: `${(s.domestic_count / s.total_count) * 100}%`,
                        }}
                      />
                      <div
                        className="bg-blue-400"
                        style={{
                          width: `${(s.international_count / s.total_count) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
              <div className="flex gap-4 text-xs text-gray-400 pt-2">
                <span className="flex items-center gap-1">
                  <span className="w-3 h-2 bg-red-400 rounded" /> Domestic
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-3 h-2 bg-blue-400 rounded" /> International
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top Skill Pairs (Co-occurrence)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {cooccurrence.top_pairs.map((p, i) => (
                <div
                  key={`${p.skill_a}-${p.skill_b}`}
                  className="flex justify-between text-sm py-1.5 border-b last:border-0"
                >
                  <span>
                    {p.skill_a_name}{" "}
                    <span className="text-gray-400">+</span>{" "}
                    {p.skill_b_name}
                  </span>
                  <span className="text-gray-500 tabular-nums">
                    {p.cooccurrence_count}x
                    <span className="text-xs ml-1 text-gray-400">
                      J={p.jaccard_index.toFixed(2)}
                    </span>
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-400 mt-3">
              Based on {cooccurrence.total_jobs_analyzed} jobs. J = Jaccard similarity.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickLink
          href="/skills"
          title="Skill Rankings"
          desc="Full skill ranking with domestic vs international breakdown"
        />
        <QuickLink
          href="/salary"
          title="Salary Analysis"
          desc="Distribution, by skill, by experience, by platform"
        />
        <QuickLink
          href="/gaps"
          title="Market Gaps"
          desc="Which skills dominate in which market"
        />
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  sub,
}: {
  title: string;
  value: string | number;
  sub: string;
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        <p className="text-xs text-gray-400 mt-1">{sub}</p>
      </CardContent>
    </Card>
  );
}

function QuickLink({
  href,
  title,
  desc,
}: {
  href: string;
  title: string;
  desc: string;
}) {
  return (
    <Link href={href}>
      <Card className="hover:border-gray-300 transition-colors cursor-pointer h-full">
        <CardContent className="pt-6">
          <p className="font-medium">{title}</p>
          <p className="text-sm text-gray-500 mt-1">{desc}</p>
        </CardContent>
      </Card>
    </Link>
  );
}
