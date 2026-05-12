import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import {
  LEARN_LEVELS,
  LEARN_LEVEL_META,
  loadArticlesByLevel,
  type LearnLevel,
} from "@/lib/learn";

export default function LearnIndexPage() {
  const counts: Record<LearnLevel, number> = {
    lv1: loadArticlesByLevel("lv1").length,
    lv2: loadArticlesByLevel("lv2").length,
    lv3: loadArticlesByLevel("lv3").length,
  };
  const total = counts.lv1 + counts.lv2 + counts.lv3;

  return (
    <div className="space-y-8">
      <header className="space-y-3 max-w-3xl">
        <h1 className="text-2xl font-bold">课本 · /learn</h1>
        <p className="text-gray-600 text-[15px] leading-relaxed">
          6 岁能懂的 AI 招聘市场科普。三层课本：
          <strong>入门</strong>（什么是就业市场 / AI 怎么改变工作）→
          <strong>职业百科</strong>（每个职业 6 岁能懂地讲一遍）→
          <strong>转岗路径</strong>（传统职业怎么转 AI 的可执行步骤）。
        </p>
        <p className="text-xs text-gray-500">
          总文章数：{total} 篇{total < 20 ? "（持续补充中，目标 ~20 篇）" : ""}
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {LEARN_LEVELS.map((lv) => {
          const meta = LEARN_LEVEL_META[lv];
          const accent = {
            emerald: {
              border: "group-hover:border-emerald-300",
              link: "text-emerald-600 group-hover:text-emerald-800",
              chip: "bg-emerald-50 text-emerald-700",
            },
            amber: {
              border: "group-hover:border-amber-300",
              link: "text-amber-600 group-hover:text-amber-800",
              chip: "bg-amber-50 text-amber-700",
            },
            indigo: {
              border: "group-hover:border-indigo-300",
              link: "text-indigo-600 group-hover:text-indigo-800",
              chip: "bg-indigo-50 text-indigo-700",
            },
          }[meta.accent as "emerald" | "amber" | "indigo"];
          return (
            <Link key={lv} href={`/learn/${lv}`} className="group">
              <Card className={`h-full transition-all ${accent.border} group-hover:shadow-md`}>
                <CardContent className="p-6 space-y-3">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold">{meta.label}</h2>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${accent.chip} font-medium`}>
                      {counts[lv]} 篇
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-700">{meta.subtitle}</p>
                  <p className="text-sm text-gray-600 leading-relaxed">{meta.description}</p>
                  <div className="pt-2">
                    <span className={`text-sm font-medium ${accent.link}`}>
                      查看 {meta.label.split(" · ")[1]} →
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="text-xs text-gray-500 bg-gray-50 border rounded-lg px-4 py-3 max-w-3xl">
        <p className="font-medium mb-1">这本课本和其他三轨什么关系？</p>
        <p className="leading-relaxed">
          <strong>叙事手册 / 岗位画像 / 传统职业</strong> 是给业务方讲市场 / 给学员定位用的「数据 + 论断」视角。
          <strong>课本 /learn</strong> 是给完全没接触过 AI 招聘的人「打地基」用的 — 不假设你懂任何术语，
          每篇用生活类比 + 真实场景把概念讲一遍。所有文章末尾都会链回相关
          <Link href="/roles" className="underline">岗位画像</Link> 或
          <Link href="/professions" className="underline">传统职业</Link>。
        </p>
      </div>
    </div>
  );
}
