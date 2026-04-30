import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { skillLabel, industryLabel } from "@/lib/labels";
import {
  type RoleProfile,
  EDU_LABELS,
  WORK_MODE_LABELS,
  fmtSalaryK,
  isMixedCluster,
  marketLabel,
} from "@/lib/roles";
import { SkillBarChart } from "./skill-chart";

const ROLE_PROFILES_PATH = path.join(
  process.cwd(),
  "public",
  "data",
  "role-profiles.json",
);
const SKILLS_PATH = path.join(process.cwd(), "public", "data", "skills.json");

function loadProfiles(): RoleProfile[] {
  return JSON.parse(fs.readFileSync(ROLE_PROFILES_PATH, "utf-8"));
}

function loadSkillNames(): Record<string, string> {
  const skills: { id: string; canonical_name: string }[] = JSON.parse(
    fs.readFileSync(SKILLS_PATH, "utf-8"),
  );
  return Object.fromEntries(skills.map((s) => [s.id, s.canonical_name]));
}

export function generateStaticParams() {
  return loadProfiles().map((r) => ({ market: r.market, roleId: r.role_id }));
}

export const dynamicParams = false;

export default async function RoleDetailPage({
  params,
}: {
  params: Promise<{ market: string; roleId: string }>;
}) {
  const { market, roleId } = await params;
  const profiles = loadProfiles();
  const role = profiles.find((p) => p.market === market && p.role_id === roleId);
  if (!role) notFound();

  const skillNames = loadSkillNames();
  const skillName = (id: string) => skillLabel(skillNames[id] || id);

  // Find the neighbor role within same market for vs_neighbor section
  const neighbor = role.vs_neighbor.neighbor_id
    ? profiles.find(
        (p) =>
          p.market === role.market && p.role_id === role.vs_neighbor.neighbor_id,
      )
    : null;

  const mixed = isMixedCluster(role.role_id);
  const accent = role.market === "domestic" ? "red" : "blue";
  const accentText = accent === "red" ? "text-red-600" : "text-blue-600";
  const accentBg = accent === "red" ? "bg-red-50" : "bg-blue-50";

  // Required + Preferred top 10 by count for the chart
  const chartData = role.required_skills
    .slice(0, 10)
    .map((rs) => {
      const pref = role.preferred_skills.find((p) => p.skill_id === rs.skill_id);
      return {
        skill: skillName(rs.skill_id),
        required: rs.count,
        preferred: pref?.count || 0,
      };
    });

  // Add preferred skills not already in required (top 5 of those)
  const requiredIds = new Set(role.required_skills.slice(0, 10).map((r) => r.skill_id));
  for (const pref of role.preferred_skills.slice(0, 10)) {
    if (chartData.length >= 12) break;
    if (!requiredIds.has(pref.skill_id)) {
      chartData.push({
        skill: skillName(pref.skill_id),
        required: 0,
        preferred: pref.count,
      });
    }
  }

  // Education + work_mode pre-sort
  const eduEntries = Object.entries(role.education)
    .filter(([, v]) => v > 0)
    .sort((a, b) => b[1] - a[1]);
  const totalEdu = eduEntries.reduce((s, [, v]) => s + v, 0);

  const wmEntries = Object.entries(role.work_mode)
    .filter(([, v]) => v > 0)
    .sort((a, b) => b[1] - a[1]);
  const totalWm = wmEntries.reduce((s, [, v]) => s + v, 0);

  return (
    <div className="space-y-8">
      <nav className="text-xs text-gray-500">
        <Link href="/roles" className="hover:text-gray-700">岗位画像</Link>
        <span className="mx-1.5">/</span>
        <span>{marketLabel(role.market)}</span>
        <span className="mx-1.5">/</span>
        <span className="text-gray-700">{role.role_name}</span>
      </nav>

      <header className="space-y-4">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-xs px-2 py-0.5 rounded-full ${accentBg} ${accentText} font-medium`}>
                {marketLabel(role.market)}
              </span>
              <span className="text-xs text-gray-500 font-mono">{role.role_id}</span>
              {mixed && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">
                  混合簇 · 下一轮 P2 拆细
                </span>
              )}
            </div>
            <h1 className="text-3xl font-bold">{role.role_name}</h1>
            <p className="text-base text-gray-600 leading-relaxed max-w-3xl">
              {role.role_description}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          <StatCell label="岗位数" value={role.job_count.toLocaleString()} accent={accentText} />
          <StatCell label="中位月薪" value={fmtSalaryK(role.salary.median)} accent={accentText} sub={`p25 ${fmtSalaryK(role.salary.p25)} · p75 ${fmtSalaryK(role.salary.p75)}`} />
          <StatCell
            label="经验中位"
            value={`${role.experience.median_min} 年起`}
            sub={`样本 ${role.experience.sample_size} 条`}
          />
          <StatCell
            label="主流工作模式"
            value={WORK_MODE_LABELS[wmEntries[0]?.[0] || "unknown"] || "—"}
            sub={`${Math.round(((wmEntries[0]?.[1] || 0) / totalWm) * 100)}% 占比`}
          />
        </div>
      </header>

      {/* Narrative */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">这岗到底是干啥的</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-[15px] text-gray-700 leading-7 whitespace-pre-line">
            {role.narrative}
          </p>
        </CardContent>
      </Card>

      {/* Core skills + Skills chart */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">技能画像</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div>
            <p className="text-xs text-gray-500 mb-2">
              精选核心技能（手挑信号清晰的 {role.core_skills.length} 项，不完全按计数排序）
            </p>
            <div className="flex flex-wrap gap-2">
              {role.core_skills.map((sid) => (
                <span
                  key={sid}
                  className={`text-sm px-3 py-1 rounded-full ${accentBg} ${accentText} font-medium border ${accent === "red" ? "border-red-200" : "border-blue-200"}`}
                >
                  {skillName(sid)}
                </span>
              ))}
            </div>
          </div>

          {chartData.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-2">
                完整技能分布 — Required（在 JD 中作为硬性要求） vs Preferred（加分项），按 JD 出现次数
              </p>
              <SkillBarChart data={chartData} accent={accent} />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Fit / Doesn't fit */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-emerald-200 bg-emerald-50/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-emerald-700">✓ 适合谁</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">{role.who_fits}</p>
          </CardContent>
        </Card>
        <Card className="border-rose-200 bg-rose-50/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-rose-700">✗ 不适合谁</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">{role.who_doesnt}</p>
          </CardContent>
        </Card>
      </div>

      {/* vs neighbor */}
      {neighbor && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">和最相邻角色的差别</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-700 leading-relaxed">{role.vs_neighbor.summary}</p>
            <div className="grid grid-cols-2 gap-3 pt-2 border-t">
              <div className="space-y-1">
                <div className="text-xs text-gray-500">{role.role_name}</div>
                <div className="text-sm font-medium">{role.role_description}</div>
                <div className="text-xs text-gray-500 pt-1">
                  中位 {fmtSalaryK(role.salary.median)} · 经验 {role.experience.median_min} 年起 · {role.job_count} 岗位
                </div>
              </div>
              <div className="space-y-1 pl-3 border-l">
                <Link
                  href={`/roles/${neighbor.market}/${neighbor.role_id}`}
                  className="text-xs text-gray-500 hover:text-gray-700 underline"
                >
                  {neighbor.role_name} →
                </Link>
                <div className="text-sm font-medium">{neighbor.role_description}</div>
                <div className="text-xs text-gray-500 pt-1">
                  中位 {fmtSalaryK(neighbor.salary.median)} · 经验 {neighbor.experience.median_min} 年起 · {neighbor.job_count} 岗位
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Distribution cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">学历要求</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {eduEntries.map(([k, v]) => {
                const pct = (v / totalEdu) * 100;
                return (
                  <DistRow key={k} label={EDU_LABELS[k] || k} value={v} pct={pct} accent={accent} />
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">工作模式</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {wmEntries.map(([k, v]) => {
                const pct = (v / totalWm) * 100;
                return (
                  <DistRow key={k} label={WORK_MODE_LABELS[k] || k} value={v} pct={pct} accent={accent} />
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Companies + Industries + Sample titles */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">头部公司</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {role.top_companies.map((c) => (
                <span key={c} className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-800">
                  {c}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">主要行业</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {role.top_industries.map((it) => {
                const pct = (it.count / role.job_count) * 100;
                return (
                  <DistRow
                    key={it.industry}
                    label={industryLabel(it.industry)}
                    value={it.count}
                    pct={pct}
                    accent={accent}
                  />
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">真实 JD 标题样本</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm text-gray-700">
            {role.sample_titles.map((t, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-gray-300">·</span>
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <p className="text-xs text-gray-400 pt-2">
        薪资 = 月薪人民币口径（海外岗已用各币种汇率换算 ÷12 月化）。样本量小于 30 的分位值参考性弱。
      </p>
    </div>
  );
}

function StatCell({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="bg-white border rounded-lg p-3 space-y-0.5">
      <div className="text-[11px] text-gray-500">{label}</div>
      <div className={`text-xl font-bold tabular-nums ${accent || "text-gray-800"}`}>
        {value}
      </div>
      {sub && <div className="text-[11px] text-gray-400 tabular-nums">{sub}</div>}
    </div>
  );
}

function DistRow({
  label,
  value,
  pct,
  accent,
}: {
  label: string;
  value: number;
  pct: number;
  accent: "red" | "blue";
}) {
  const barColor = accent === "red" ? "bg-red-300" : "bg-blue-300";
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-700">{label}</span>
        <span className="tabular-nums text-gray-500">
          {value} <span className="text-gray-400">({pct.toFixed(0)}%)</span>
        </span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded">
        <div className={`h-full rounded ${barColor}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
    </div>
  );
}
