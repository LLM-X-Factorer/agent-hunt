import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import {
  LEARN_LEVELS,
  LEARN_LEVEL_META,
  loadArticlesByLevel,
  type LearnLevel,
} from "@/lib/learn";

export function generateStaticParams() {
  return LEARN_LEVELS.map((level) => ({ level }));
}

export const dynamicParams = false;

export default async function LearnLevelPage({
  params,
}: {
  params: Promise<{ level: string }>;
}) {
  const { level } = await params;
  if (!LEARN_LEVELS.includes(level as LearnLevel)) notFound();
  const lv = level as LearnLevel;
  const meta = LEARN_LEVEL_META[lv];
  const articles = loadArticlesByLevel(lv);

  return (
    <div className="space-y-6">
      <nav className="text-xs text-gray-500">
        <Link href="/learn" className="hover:text-gray-700">
          课本
        </Link>
        <span className="mx-1.5">/</span>
        <span className="text-gray-700">{meta.label}</span>
      </nav>

      <header className="space-y-2 max-w-3xl">
        <h1 className="text-2xl font-bold">{meta.label}</h1>
        <p className="text-base text-gray-600 leading-relaxed">{meta.subtitle}</p>
        <p className="text-sm text-gray-500 leading-relaxed">{meta.description}</p>
        <p className="text-xs text-gray-500 pt-2">{articles.length} 篇</p>
      </header>

      {articles.length === 0 ? (
        <div className="text-sm text-gray-500 bg-amber-50 border border-amber-200 rounded px-4 py-3 max-w-2xl">
          本级别文章持续补充中（issue #39）。
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {articles.map((a) => (
            <Link
              key={a.slug}
              href={`/learn/${lv}/${a.slug}`}
              className="group block"
            >
              <Card className="h-full transition-all group-hover:border-gray-400 group-hover:shadow-sm">
                <CardContent className="p-5 space-y-2">
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs text-gray-400 tabular-nums font-mono">
                      {String(a.order).padStart(2, "0")}
                    </span>
                    <h3 className="font-semibold text-base leading-snug">{a.title}</h3>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">
                    {a.summary}
                  </p>
                  <div className="flex justify-between items-center pt-1 text-xs text-gray-400">
                    <span>
                      {a.reading_minutes ? `${a.reading_minutes} 分钟` : ""}
                    </span>
                    <span className="group-hover:text-gray-600">阅读 →</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
