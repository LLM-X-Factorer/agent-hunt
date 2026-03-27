import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SkillChart } from "./chart";

export default async function SkillsPage() {
  const skills = await api.skills();
  const active = skills.filter((s) => s.total_count > 0);

  const categories = [...new Set(active.map((s) => s.category))];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Skill Rankings</h1>
        <p className="text-gray-500 mt-1">
          {active.length} skills tracked across domestic and international markets
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Top 25 Skills — Domestic vs International
          </CardTitle>
        </CardHeader>
        <CardContent>
          <SkillChart skills={active.slice(0, 25)} />
        </CardContent>
      </Card>

      {/* By Category */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {categories.map((cat) => {
          const catSkills = active
            .filter((s) => s.category === cat)
            .sort((a, b) => b.total_count - a.total_count);
          if (catSkills.length === 0) return null;
          return (
            <Card key={cat}>
              <CardHeader>
                <CardTitle className="text-base capitalize">{cat}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {catSkills.map((s) => (
                    <div
                      key={s.id}
                      className="flex justify-between text-sm py-1 border-b last:border-0"
                    >
                      <span>{s.canonical_name}</span>
                      <span className="tabular-nums text-gray-500">
                        <span className="text-red-500">{s.domestic_count}</span>
                        {" / "}
                        <span className="text-blue-500">
                          {s.international_count}
                        </span>
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
