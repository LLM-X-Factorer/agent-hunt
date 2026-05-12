import Link from "next/link";
import { notFound } from "next/navigation";
import { marked } from "marked";
import { Card, CardContent } from "@/components/ui/card";
import {
  LEARN_LEVELS,
  LEARN_LEVEL_META,
  findArticle,
  loadAllArticles,
  neighbors,
  type LearnLevel,
} from "@/lib/learn";

export function generateStaticParams() {
  return loadAllArticles().map((a) => ({ level: a.level, slug: a.slug }));
}

export const dynamicParams = false;

marked.setOptions({ gfm: true, breaks: false });

export default async function LearnArticlePage({
  params,
}: {
  params: Promise<{ level: string; slug: string }>;
}) {
  const { level, slug } = await params;
  if (!LEARN_LEVELS.includes(level as LearnLevel)) notFound();
  const lv = level as LearnLevel;
  const article = findArticle(lv, slug);
  if (!article) notFound();

  const meta = LEARN_LEVEL_META[lv];
  const html = await marked.parse(article.content);
  const { prev, next } = neighbors(lv, slug);

  return (
    <article className="space-y-8 max-w-3xl mx-auto">
      <nav className="text-xs text-gray-500">
        <Link href="/learn" className="hover:text-gray-700">
          课本
        </Link>
        <span className="mx-1.5">/</span>
        <Link href={`/learn/${lv}`} className="hover:text-gray-700">
          {meta.label}
        </Link>
        <span className="mx-1.5">/</span>
        <span className="text-gray-700">{article.title}</span>
      </nav>

      <header className="space-y-3 pb-6 border-b">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-gray-500 font-mono">
            {meta.label} · 第 {String(article.order).padStart(2, "0")} 篇
          </span>
          {article.reading_minutes && (
            <span className="text-xs text-gray-400">
              · {article.reading_minutes} 分钟阅读
            </span>
          )}
        </div>
        <h1 className="text-3xl font-bold leading-tight">{article.title}</h1>
        <p className="text-base text-gray-600 leading-relaxed">{article.summary}</p>
      </header>

      <div
        className="learn-prose text-[15px] text-gray-800 leading-7"
        dangerouslySetInnerHTML={{ __html: html }}
      />

      {(article.linked_roles?.length || article.linked_professions?.length) && (
        <Card className="border-indigo-200 bg-indigo-50/30">
          <CardContent className="p-5 space-y-2">
            <p className="text-sm font-medium text-indigo-900">相关数据 / 画像</p>
            <div className="flex flex-wrap gap-2">
              {article.linked_professions?.map((id) => (
                <Link
                  key={`prof-${id}`}
                  href={`/professions/${id}`}
                  className="text-sm px-3 py-1 rounded-full bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-100"
                >
                  传统职业 · {id} →
                </Link>
              ))}
              {article.linked_roles?.map((r) => (
                <Link
                  key={`role-${r.market}-${r.role_id}`}
                  href={`/roles/${r.market}/${r.role_id}`}
                  className="text-sm px-3 py-1 rounded-full bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-100"
                >
                  AI 角色 · {r.role_id} ({r.market === "domestic" ? "国内" : "海外"}) →
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <nav className="grid grid-cols-2 gap-3 pt-6 border-t">
        {prev ? (
          <Link
            href={`/learn/${lv}/${prev.slug}`}
            className="block group rounded-lg border p-4 hover:border-gray-400 hover:shadow-sm transition-all"
          >
            <div className="text-xs text-gray-500 mb-1">← 上一篇</div>
            <div className="text-sm font-medium text-gray-800 group-hover:text-gray-900">
              {prev.title}
            </div>
          </Link>
        ) : (
          <div />
        )}
        {next ? (
          <Link
            href={`/learn/${lv}/${next.slug}`}
            className="block group rounded-lg border p-4 hover:border-gray-400 hover:shadow-sm transition-all text-right"
          >
            <div className="text-xs text-gray-500 mb-1">下一篇 →</div>
            <div className="text-sm font-medium text-gray-800 group-hover:text-gray-900">
              {next.title}
            </div>
          </Link>
        ) : (
          <Link
            href={`/learn/${lv}`}
            className="block group rounded-lg border p-4 hover:border-gray-400 hover:shadow-sm transition-all text-right"
          >
            <div className="text-xs text-gray-500 mb-1">回到</div>
            <div className="text-sm font-medium text-gray-800 group-hover:text-gray-900">
              {meta.label} 目录
            </div>
          </Link>
        )}
      </nav>
    </article>
  );
}
