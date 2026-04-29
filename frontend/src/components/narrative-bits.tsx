"use client";

import { Card, CardContent } from "@/components/ui/card";

export interface JobExample {
  title: string;
  company: string | null;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  salary_min_cny_monthly: number | null;
  salary_max_cny_monthly: number | null;
  experience_requirement: string | null;
  education: string | null;
  work_mode: string | null;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  base_profession: string | null;
  platform_id: string;
  source_url: string | null;
}

const PLATFORM_LABEL: Record<string, string> = {
  liepin: "猎聘",
  boss_zhipin: "Boss直聘",
  lagou: "拉勾",
  linkedin: "LinkedIn",
  indeed: "Indeed",
  vendor_openai: "OpenAI 官网",
  vendor_anthropic: "Anthropic 官网",
  vendor_xai: "xAI 官网",
  vendor_cohere: "Cohere 官网",
  vendor_deepmind: "DeepMind 官网",
  community_hn_wih: "HN Who is Hiring",
  community_github_hiring: "GitHub Hiring Repo",
};

function formatSalary(ex: JobExample): string {
  if (!ex.salary_min || !ex.salary_max) return "未披露";
  const cur = ex.salary_currency || "CNY";
  if (cur === "CNY") {
    return `¥${(ex.salary_min / 1000).toFixed(0)}k–${(ex.salary_max / 1000).toFixed(0)}k/月`;
  }
  // Foreign currency: show original (annual) + CNY/月 conversion
  const sym = cur === "USD" ? "$" : cur === "EUR" ? "€" : cur === "GBP" ? "£" : "";
  const main = sym
    ? `${sym}${(ex.salary_min / 1000).toFixed(0)}k–${(ex.salary_max / 1000).toFixed(0)}k/年`
    : `${ex.salary_min}–${ex.salary_max} ${cur}/年`;
  if (ex.salary_min_cny_monthly && ex.salary_max_cny_monthly) {
    return `${main}（≈ ¥${(ex.salary_min_cny_monthly / 1000).toFixed(0)}k–${(ex.salary_max_cny_monthly / 1000).toFixed(0)}k/月）`;
  }
  return main;
}

export function JobExampleCard({ ex }: { ex: JobExample }) {
  return (
    <Card>
      <CardContent className="pt-5 space-y-3">
        <div className="flex flex-wrap items-baseline gap-2 justify-between">
          <h4 className="font-semibold text-sm leading-snug">{ex.title}</h4>
          <span className="text-xs text-gray-500 shrink-0">
            {PLATFORM_LABEL[ex.platform_id] || ex.platform_id}
          </span>
        </div>
        <div className="text-xs text-gray-600 space-y-1">
          <p>
            <span className="text-gray-400">公司：</span>
            {ex.company || "未披露"}
            {ex.location && <span className="text-gray-400 ml-2">· {ex.location}</span>}
          </p>
          <p>
            <span className="text-gray-400">薪资：</span>
            <span className="font-medium text-gray-800">{formatSalary(ex)}</span>
            {ex.experience_requirement && (
              <span className="text-gray-400 ml-2">· {ex.experience_requirement}</span>
            )}
            {ex.education && <span className="text-gray-400 ml-2">· {ex.education}</span>}
          </p>
          {ex.base_profession && (
            <p>
              <span className="text-gray-400">原职业：</span>
              <span className="font-medium">{ex.base_profession}</span>
            </p>
          )}
        </div>

        {ex.required_skills.length > 0 && (
          <div>
            <p className="text-xs text-gray-400 mb-1">技能要求</p>
            <div className="flex flex-wrap gap-1">
              {ex.required_skills.slice(0, 6).map((s, i) => (
                <span key={i} className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-700">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {ex.responsibilities.length > 0 && (
          <div>
            <p className="text-xs text-gray-400 mb-1">职责（部分）</p>
            <ul className="text-xs text-gray-700 space-y-1 list-disc list-inside">
              {ex.responsibilities.slice(0, 2).map((r, i) => (
                <li key={i} className="leading-relaxed">{r}</li>
              ))}
            </ul>
          </div>
        )}

        {ex.source_url && (
          <a
            href={ex.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-indigo-600 hover:text-indigo-800 inline-block"
          >
            查看原始 JD →
          </a>
        )}
      </CardContent>
    </Card>
  );
}

export function MethodologyBox({
  title = "📐 这个数字怎么算的",
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-5 space-y-2 text-sm text-gray-700">
      <p className="font-semibold text-gray-900">{title}</p>
      <div className="space-y-2 leading-relaxed">{children}</div>
    </div>
  );
}

export function MechanismBox({
  title = "🧠 为什么会这样",
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-5 space-y-2 text-sm text-gray-700">
      <p className="font-semibold text-emerald-900">{title}</p>
      <div className="space-y-2 leading-relaxed">{children}</div>
    </div>
  );
}

export function CaveatBox({
  title = "⚠️ 边界与反例",
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-5 space-y-2 text-sm text-gray-700">
      <p className="font-semibold text-amber-900">{title}</p>
      <div className="space-y-2 leading-relaxed">{children}</div>
    </div>
  );
}

export function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xl font-bold pt-4 border-t">
      {children}
    </h2>
  );
}
