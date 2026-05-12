import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { industryLabel, skillLabel } from "@/lib/labels";
import {
  type ProfessionProfile,
  PROFESSION_CATEGORY_LABELS,
  sampleTier,
} from "@/lib/professions";
import { EDU_LABELS, WORK_MODE_LABELS, fmtSalaryK, marketLabel } from "@/lib/roles";

const PROFESSIONS_PATH = path.join(
  process.cwd(),
  "public",
  "data",
  "profession-profiles.json",
);
const SKILLS_PATH = path.join(process.cwd(), "public", "data", "skills.json");

function loadProfessions(): ProfessionProfile[] {
  return JSON.parse(fs.readFileSync(PROFESSIONS_PATH, "utf-8"));
}

function loadSkillNames(): Record<string, string> {
  const skills: { id: string; canonical_name: string }[] = JSON.parse(
    fs.readFileSync(SKILLS_PATH, "utf-8"),
  );
  return Object.fromEntries(skills.map((s) => [s.id, s.canonical_name]));
}

export function generateStaticParams() {
  return loadProfessions().map((p) => ({ id: p.profession_id }));
}

export const dynamicParams = false;

export default async function ProfessionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const all = loadProfessions();
  const p = all.find((x) => x.profession_id === id);
  if (!p) notFound();

  const skillNames = loadSkillNames();
  const skillName = (sid: string) => skillLabel(skillNames[sid] || sid);

  const tier = sampleTier(p.sample_size);
  const showBaseline = tier !== "none" && p.sample_size > 0;
  const totalPivot = p.ai_pivot_targets.reduce((s, t) => s + t.count, 0);

  // Education / work mode pre-sort
  const eduEntries = showBaseline
    ? Object.entries(p.education || {})
        .filter(([, v]) => v > 0)
        .sort((a, b) => b[1] - a[1])
    : [];
  const totalEdu = eduEntries.reduce((s, [, v]) => s + v, 0);

  const wmEntries = showBaseline
    ? Object.entries(p.work_mode || {})
        .filter(([, v]) => v > 0)
        .sort((a, b) => b[1] - a[1])
    : [];
  const totalWm = wmEntries.reduce((s, [, v]) => s + v, 0);

  return (
    <div className="space-y-8">
      <nav className="text-xs text-gray-500">
        <Link href="/professions" className="hover:text-gray-700">
          传统职业
        </Link>
        <span className="mx-1.5">/</span>
        <span>{PROFESSION_CATEGORY_LABELS[p.category]}</span>
        <span className="mx-1.5">/</span>
        <span className="text-gray-700">{p.cn_name}</span>
      </nav>

      <header className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 font-medium">
              {PROFESSION_CATEGORY_LABELS[p.category]}
            </span>
            <span className="text-xs text-gray-500 font-mono">{p.en_name}</span>
            <SampleTierBadge tier={tier} count={p.sample_size} />
          </div>
          <h1 className="text-3xl font-bold">{p.cn_name}</h1>
          <p className="text-base text-gray-600 leading-relaxed max-w-3xl">
            {p.one_liner}
          </p>
        </div>

        {tier === "none" ? (
          <div className="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded px-3 py-2 max-w-3xl">
            ⚠ 该职业的 AI 增强样本仅 {p.sample_size} 条（&lt; 5）— 数据 baseline 不足以显示，下方保留手写转型路径 + AI 角色匹配信号。
            纯传统 JD 大规模采集计划进行中（#34）。
          </div>
        ) : tier === "weak" ? (
          <div className="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded px-3 py-2 max-w-3xl">
            ⚠ 该职业的 AI 增强样本仅 {p.sample_size} 条（&lt; 10）— baseline 部分仅供参考，分位 / 分布波动大。
            纯传统 JD 大规模采集计划进行中（#34）。
          </div>
        ) : tier === "medium" ? (
          <div className="text-sm text-yellow-700 bg-yellow-50 border border-yellow-200 rounded px-3 py-2 max-w-3xl">
            样本中等（{p.sample_size} 条 AI 增强 JD），分位 / 分布有代表性但仍偏窄，建议结合手写转型描述判断。
          </div>
        ) : null}
      </header>

      {/* Description */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">这职业到底在做什么</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-[15px] text-gray-700 leading-7 whitespace-pre-line">
            {p.description}
          </p>
          <div>
            <h3 className="text-sm font-medium text-gray-800 mb-2">传统核心职责</h3>
            <ul className="space-y-1.5 text-sm text-gray-700">
              {p.responsibilities.map((r, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-gray-300 shrink-0">·</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* AI Pivot Targets — 能转哪些 AI 岗 */}
      <Card className="border-indigo-200 bg-indigo-50/30">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-indigo-900">
            能转哪些 AI 岗（按已采集到的 AI 增强样本占比）
          </CardTitle>
          <p className="text-xs text-gray-500 pt-1">
            从 {p.sample_size} 条「base_profession = {p.cn_name}」的 ai_augmented_traditional JD
            出发，按 JD 标题归类到对应 AI 角色簇。点击进入该角色画像。
          </p>
        </CardHeader>
        <CardContent>
          {p.ai_pivot_targets.length === 0 ? (
            <p className="text-sm text-gray-600">
              当前 sample 量不足以做角色聚合 — 见手写「转型路径」section 中的方向建议。
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {p.ai_pivot_targets.map((t) => {
                const pct = totalPivot ? (t.count / totalPivot) * 100 : 0;
                return (
                  <Link
                    key={`${t.market}-${t.role_id}`}
                    href={`/roles/${t.market}/${t.role_id}`}
                    className="block group"
                  >
                    <div className="border rounded-lg bg-white p-3 transition-all group-hover:border-indigo-400 group-hover:shadow-sm">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                              t.market === "domestic"
                                ? "bg-red-50 text-red-600"
                                : "bg-blue-50 text-blue-600"
                            }`}
                          >
                            {marketLabel(t.market)}
                          </span>
                          <span className="text-sm font-medium text-gray-800 group-hover:text-indigo-700">
                            {t.role_name}
                          </span>
                        </div>
                        <span className="text-xs tabular-nums text-gray-500">
                          {t.count} 条 ({pct.toFixed(0)}%)
                        </span>
                      </div>
                      <div className="h-1 bg-gray-100 rounded">
                        <div
                          className="h-full rounded bg-indigo-300"
                          style={{ width: `${Math.min(pct, 100)}%` }}
                        />
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pathway — 手写转型路径 */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">转 AI 的路径</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-[15px] text-gray-700 leading-7 whitespace-pre-line">
            {p.pathway_summary}
          </p>
        </CardContent>
      </Card>

      {/* Who should / shouldn't pivot */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-emerald-200 bg-emerald-50/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-emerald-700">✓ 谁该转</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">{p.who_should_pivot}</p>
          </CardContent>
        </Card>
        <Card className="border-rose-200 bg-rose-50/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-rose-700">✗ 谁不该转</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">{p.who_shouldnt_pivot}</p>
          </CardContent>
        </Card>
      </div>

      {/* Baseline — only when sample_size > 0 */}
      {showBaseline && (
        <>
          {/* Salary + Experience snapshot */}
          {p.salary && p.experience && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">薪资 + 经验分布</CardTitle>
                <p className="text-xs text-gray-500 pt-1">
                  基于 {p.sample_size} 条 AI 增强样本聚合。月薪人民币口径（海外岗按汇率
                  ÷12 月化）
                  {tier === "weak" && " · 样本量小，分位仅供参考"}
                </p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <StatCell
                    label="样本量"
                    value={p.sample_size.toLocaleString()}
                    sub="ai_augmented JD"
                  />
                  <StatCell
                    label="中位月薪"
                    value={fmtSalaryK(p.salary.median)}
                    sub={`p25 ${fmtSalaryK(p.salary.p25)} · p75 ${fmtSalaryK(p.salary.p75)}`}
                  />
                  <StatCell
                    label="经验中位"
                    value={`${p.experience.median_min} 年起`}
                    sub={`样本 ${p.experience.sample_size} 条`}
                  />
                  <StatCell
                    label="主流工作模式"
                    value={WORK_MODE_LABELS[wmEntries[0]?.[0] || "unknown"] || "—"}
                    sub={
                      totalWm
                        ? `${Math.round(((wmEntries[0]?.[1] || 0) / totalWm) * 100)}% 占比`
                        : ""
                    }
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* 学历 + 专业 */}
          {(eduEntries.length > 0 || (p.top_majors && p.top_majors.length > 0)) && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">学历 + 专业分布</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {eduEntries.length > 0 && (
                    <div>
                      <div className="flex items-baseline justify-between mb-3">
                        <h3 className="text-sm font-medium text-gray-800">学历</h3>
                        <span className="text-[11px] text-gray-400 tabular-nums">
                          {totalEdu} 条样本
                        </span>
                      </div>
                      <div className="space-y-2">
                        {eduEntries.map(([k, v]) => (
                          <DistRow
                            key={k}
                            label={EDU_LABELS[k] || k}
                            value={v}
                            pct={(v / totalEdu) * 100}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                  {p.top_majors && p.top_majors.length > 0 && (
                    <div>
                      <div className="flex items-baseline justify-between mb-3">
                        <h3 className="text-sm font-medium text-gray-800">高频专业 top 5</h3>
                        <span className="text-[11px] text-gray-400 tabular-nums">
                          {p.majors_sample_size} / {p.sample_size} 条 JD 提到
                        </span>
                      </div>
                      <div className="space-y-2">
                        {p.top_majors.map((m) => (
                          <DistRow
                            key={m.major}
                            label={m.major}
                            value={m.count}
                            pct={
                              p.majors_sample_size
                                ? (m.count / p.majors_sample_size) * 100
                                : 0
                            }
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* 高频职责（来自 AI 增强 JD，可以反映 AI 后的工作内容） */}
          {p.top_responsibilities && p.top_responsibilities.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">AI 增强后的高频职责</CardTitle>
                <p className="text-xs text-gray-500 pt-1">
                  从 {p.responsibilities_sample_size} / {p.sample_size} 条 AI 增强 JD 的职责描述里直接计数 —
                  反映「这职业被 AI 改写后日常做什么」
                </p>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2.5">
                  {p.top_responsibilities.map((r, i) => (
                    <li
                      key={i}
                      className="flex gap-3 text-sm text-gray-700 leading-relaxed"
                    >
                      <span className="shrink-0 text-xs tabular-nums px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-medium h-fit mt-0.5">
                        ×{r.count}
                      </span>
                      <span>{r.text}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* 学这些技能能转过去 */}
          {p.required_skills && p.required_skills.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">学这些技能能转过去</CardTitle>
                <p className="text-xs text-gray-500 pt-1">
                  AI 增强版「{p.cn_name}」JD 里出现频次最高的硬技能 — 把这些点亮到简历上，是从{p.cn_name}转 AI 路径的「最小可行 skill set」
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-[11px] text-gray-500 mb-2">硬性要求 (Required)</div>
                  <div className="flex flex-wrap gap-2">
                    {p.required_skills.slice(0, 12).map((s) => (
                      <span
                        key={s.skill_id}
                        className="text-sm px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 font-medium border border-indigo-200"
                      >
                        {skillName(s.skill_id)}
                        <span className="ml-1 text-[11px] text-indigo-400 tabular-nums">
                          ×{s.count}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
                {p.preferred_skills && p.preferred_skills.length > 0 && (
                  <div>
                    <div className="text-[11px] text-gray-500 mb-2">加分项 (Preferred)</div>
                    <div className="flex flex-wrap gap-2">
                      {p.preferred_skills.slice(0, 8).map((s) => (
                        <span
                          key={s.skill_id}
                          className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700"
                        >
                          {skillName(s.skill_id)}
                          <span className="ml-1 text-[11px] text-gray-400 tabular-nums">
                            ×{s.count}
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Companies + Industries + Sample titles */}
          {(p.top_companies?.length || p.top_industries?.length) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {p.top_companies && p.top_companies.length > 0 && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">头部招聘公司</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {p.top_companies.map((c) => (
                        <span
                          key={c}
                          className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-800"
                        >
                          {c}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              {p.top_industries && p.top_industries.length > 0 && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">主要行业分布</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {p.top_industries.map((it) => (
                        <DistRow
                          key={it.industry}
                          label={industryLabel(it.industry)}
                          value={it.count}
                          pct={(it.count / p.sample_size) * 100}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {p.sample_titles && p.sample_titles.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">真实 JD 标题样本</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm text-gray-700">
                  {p.sample_titles.map((t, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-gray-300">·</span>
                      <span>{t}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </>
      )}

      <p className="text-xs text-gray-400 pt-2">
        本页 baseline 数据 = agent-hunt 已抓取的 base_profession = {p.cn_name} 的「ai_augmented_traditional」岗位聚合，
        不是纯传统 JD。纯传统职业 baseline 采集（#34）计划补齐后会区分展示。
      </p>
    </div>
  );
}

function SampleTierBadge({
  tier,
  count,
}: {
  tier: "strong" | "medium" | "weak" | "none";
  count: number;
}) {
  const badge = {
    strong: { bg: "bg-emerald-50", text: "text-emerald-700", label: "数据充足" },
    medium: { bg: "bg-yellow-50", text: "text-yellow-700", label: "样本中等" },
    weak: { bg: "bg-rose-50", text: "text-rose-700", label: "样本稀疏" },
    none: { bg: "bg-gray-100", text: "text-gray-500", label: "暂无数据" },
  }[tier];
  return (
    <span
      className={`text-[11px] px-2 py-0.5 rounded-full ${badge.bg} ${badge.text} font-medium`}
    >
      {count} 条 · {badge.label}
    </span>
  );
}

function StatCell({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="bg-white border rounded-lg p-3 space-y-0.5">
      <div className="text-[11px] text-gray-500">{label}</div>
      <div className="text-xl font-bold tabular-nums text-gray-800">{value}</div>
      {sub && <div className="text-[11px] text-gray-400 tabular-nums">{sub}</div>}
    </div>
  );
}

function DistRow({
  label,
  value,
  pct,
}: {
  label: string;
  value: number;
  pct: number;
}) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-700">{label}</span>
        <span className="tabular-nums text-gray-500">
          {value} <span className="text-gray-400">({pct.toFixed(0)}%)</span>
        </span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded">
        <div
          className="h-full rounded bg-indigo-300"
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  );
}
