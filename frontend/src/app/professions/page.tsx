import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import {
  type ProfessionCategory,
  type ProfessionProfile,
  PROFESSION_CATEGORY_LABELS,
  PROFESSION_CATEGORY_ORDER,
  sampleTier,
} from "@/lib/professions";

const PROFESSIONS_PATH = path.join(
  process.cwd(),
  "public",
  "data",
  "profession-profiles.json",
);

function loadProfessions(): ProfessionProfile[] {
  return JSON.parse(fs.readFileSync(PROFESSIONS_PATH, "utf-8"));
}

export default function ProfessionsListPage() {
  const all = loadProfessions();
  const byCategory = new Map<ProfessionCategory, ProfessionProfile[]>();
  for (const cat of PROFESSION_CATEGORY_ORDER) byCategory.set(cat, []);
  for (const p of all) byCategory.get(p.category)?.push(p);

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">传统职业 × AI 转型路径</h1>
        <p className="text-gray-500 text-sm leading-relaxed max-w-3xl">
          回答业务方反复问的「我是 X 怎么转 AI」—— 8 个传统职业（4 工程线 + 2 商科 + 2 服务）的 AI 增强样本聚合 + 手写转型路径。
          数据来源：agent-hunt 已抓取的 ai_augmented_traditional 岗位（{all.reduce((s, p) => s + p.sample_size, 0)} 条），
          按 base_profession 字段反向聚合到对应传统职业。点击职业卡查看详情。
        </p>
        <div className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2 max-w-3xl">
          ⚠ 部分职业（土木 / 化工 / 电气）的国内 AI 增强样本较少（&lt; 10）—— 详情页保留手写转型路径，数据基线会标注 disclaimer。
          纯传统 JD 采集计划进行中（#34），后续会补齐 baseline 部分。
        </div>
      </header>

      {PROFESSION_CATEGORY_ORDER.map((cat) => {
        const items = byCategory.get(cat) || [];
        if (items.length === 0) return null;
        return (
          <section key={cat} className="space-y-3">
            <h2 className="text-sm font-medium text-gray-700">
              {PROFESSION_CATEGORY_LABELS[cat]}
              <span className="ml-2 text-xs text-gray-400">{items.length} 个职业</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {items.map((p) => (
                <ProfessionCard key={p.profession_id} p={p} />
              ))}
            </div>
          </section>
        );
      })}

      <p className="text-xs text-gray-400 pt-2">
        薪资 = 月薪人民币口径（海外岗已用各币种汇率换算 ÷12 月化）。每个职业的 sample_size 指对应「AI 增强版」岗位数，不是纯传统 JD 数。
      </p>
    </div>
  );
}

function ProfessionCard({ p }: { p: ProfessionProfile }) {
  const tier = sampleTier(p.sample_size);
  const tierBadge = {
    strong: { bg: "bg-emerald-50", text: "text-emerald-700", label: "数据充足" },
    medium: { bg: "bg-yellow-50", text: "text-yellow-700", label: "样本中等" },
    weak: { bg: "bg-rose-50", text: "text-rose-700", label: "样本稀疏" },
    none: { bg: "bg-gray-100", text: "text-gray-500", label: "暂无数据" },
  }[tier];

  return (
    <Link href={`/professions/${p.profession_id}`} className="group block">
      <Card className="h-full transition-all group-hover:border-gray-400 group-hover:shadow-sm">
        <CardContent className="p-5 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div className="space-y-1">
              <h3 className="font-semibold text-lg leading-snug">{p.cn_name}</h3>
              <div className="text-xs text-gray-400 font-mono">{p.en_name}</div>
            </div>
            <span
              className={`text-[11px] px-2 py-0.5 rounded-full ${tierBadge.bg} ${tierBadge.text} font-medium shrink-0`}
            >
              {p.sample_size} · {tierBadge.label}
            </span>
          </div>

          <p className="text-sm text-gray-700 leading-relaxed">{p.one_liner}</p>

          {p.ai_pivot_targets.length > 0 && (
            <div className="pt-2 border-t space-y-1.5">
              <div className="text-[11px] text-gray-500">能转的 AI 岗位（按样本占比）</div>
              <div className="flex flex-wrap gap-1.5">
                {p.ai_pivot_targets.slice(0, 4).map((t) => (
                  <span
                    key={`${t.market}-${t.role_id}`}
                    className="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-700"
                  >
                    {t.role_name} <span className="text-gray-400">×{t.count}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end text-xs pt-1">
            <span className="text-gray-400 group-hover:text-gray-600">详情 →</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
