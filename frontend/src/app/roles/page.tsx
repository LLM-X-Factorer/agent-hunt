"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { skillLabel } from "@/lib/labels";
import {
  type Market,
  type RoleProfile,
  fmtSalaryK,
  isMixedCluster,
  marketLabel,
} from "@/lib/roles";

interface SkillIdMap {
  [id: string]: string;
}

export default function RolesPage() {
  const [profiles, setProfiles] = useState<RoleProfile[]>([]);
  const [skillNames, setSkillNames] = useState<SkillIdMap>({});
  const [loading, setLoading] = useState(true);
  const [activeMarket, setActiveMarket] = useState<Market>("domestic");

  useEffect(() => {
    Promise.all([
      fetch("/data/role-profiles.json").then((r) => r.json()),
      fetch("/data/skills.json").then((r) => r.json()),
    ]).then(([p, s]: [RoleProfile[], { id: string; canonical_name: string }[]]) => {
      setProfiles(p);
      setSkillNames(Object.fromEntries(s.map((sk) => [sk.id, sk.canonical_name])));
      setLoading(false);
    });
  }, []);

  const grouped = useMemo(() => {
    const dom = profiles.filter((p) => p.market === "domestic");
    const intl = profiles.filter((p) => p.market === "international");
    return { domestic: dom, international: intl };
  }, [profiles]);

  if (loading) return <div className="text-center py-20 text-gray-400">加载中…</div>;

  const visible = grouped[activeMarket];
  const accent: "red" | "blue" = activeMarket === "domestic" ? "red" : "blue";

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">岗位画像</h1>
        <p className="text-gray-500 text-sm leading-relaxed">
          27 个角色簇，国内 {grouped.domestic.length} 个 + 海外 {grouped.international.length} 个 ——
          每个角色给出技能画像、薪资分布、和最相邻角色的差别，告诉你「这岗到底是干啥的，谁该投谁不该投」。
          点击角色卡进入详情。
        </p>
      </header>

      <div className="inline-flex bg-gray-100 rounded-lg p-1 gap-1">
        <MarketButton
          active={activeMarket === "domestic"}
          onClick={() => setActiveMarket("domestic")}
          label={`国内 · ${grouped.domestic.length} 角色`}
          activeColor="red"
        />
        <MarketButton
          active={activeMarket === "international"}
          onClick={() => setActiveMarket("international")}
          label={`海外 · ${grouped.international.length} 角色`}
          activeColor="blue"
        />
      </div>

      <RoleGrid roles={visible} skillNames={skillNames} accent={accent} />

      <p className="text-xs text-gray-400 pt-2">
        薪资 = 月薪人民币口径（海外岗已用各币种汇率换算 ÷12 月化）。
      </p>
    </div>
  );
}

function MarketButton({
  active,
  onClick,
  label,
  activeColor,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  activeColor: "red" | "blue";
}) {
  const activeText = activeColor === "red" ? "text-red-700" : "text-blue-700";
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-4 py-1.5 text-sm rounded-md transition-colors ${
        active ? `bg-white shadow-sm font-medium ${activeText}` : "text-gray-600 hover:text-gray-900"
      }`}
    >
      {label}
    </button>
  );
}

function RoleGrid({
  roles,
  skillNames,
  accent,
}: {
  roles: RoleProfile[];
  skillNames: SkillIdMap;
  accent: "red" | "blue";
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {roles.map((r) => (
        <RoleCard key={r.role_id} role={r} skillNames={skillNames} accent={accent} />
      ))}
    </div>
  );
}

function RoleCard({
  role,
  skillNames,
  accent,
}: {
  role: RoleProfile;
  skillNames: SkillIdMap;
  accent: "red" | "blue";
}) {
  const mixed = isMixedCluster(role.role_id);
  const accentText = accent === "red" ? "text-red-600" : "text-blue-600";
  const accentDot = accent === "red" ? "bg-red-400" : "bg-blue-400";
  const href = `/roles/${role.market}/${role.role_id}`;

  return (
    <Link href={href} className="group block">
      <Card className="h-full transition-all group-hover:border-gray-400 group-hover:shadow-sm">
        <CardContent className="p-5 space-y-3">
          <div className="flex items-start justify-between gap-2">
            <div className="space-y-1">
              <h3 className="font-semibold text-base leading-snug">{role.role_name}</h3>
              <div className="flex items-center gap-1.5 text-xs">
                <span className={`inline-block w-1.5 h-1.5 rounded-full ${accentDot}`} />
                <span className="text-gray-500">{marketLabel(role.market)} · {role.role_id}</span>
                {mixed && (
                  <span className="ml-1 px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 text-[10px]">
                    混合簇
                  </span>
                )}
              </div>
            </div>
            <div className={`text-right ${accentText} shrink-0`}>
              <div className="text-xl font-bold tabular-nums leading-none">
                {role.job_count.toLocaleString()}
              </div>
              <div className="text-[10px] text-gray-500 mt-0.5">岗位数</div>
            </div>
          </div>

          <p className="text-sm text-gray-700 leading-relaxed line-clamp-3">
            {role.role_description}
          </p>

          <div className="flex flex-wrap gap-1 pt-1">
            {role.core_skills.slice(0, 5).map((sid) => (
              <span
                key={sid}
                className="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-700"
              >
                {skillLabel(skillNames[sid] || sid)}
              </span>
            ))}
          </div>

          <div className="flex justify-between items-center pt-2 border-t text-xs">
            <span className="text-gray-500">
              中位 <span className="font-semibold text-gray-800">{fmtSalaryK(role.salary.median)}</span>
              <span className="ml-2 text-gray-400">
                p25 {fmtSalaryK(role.salary.p25)} · p75 {fmtSalaryK(role.salary.p75)}
              </span>
            </span>
            <span className="text-gray-400 group-hover:text-gray-600">详情 →</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
