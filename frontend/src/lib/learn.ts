import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

export type LearnLevel = "lv1" | "lv2" | "lv3";

export const LEARN_LEVELS: LearnLevel[] = ["lv1", "lv2", "lv3"];

export const LEARN_LEVEL_META: Record<
  LearnLevel,
  { label: string; subtitle: string; description: string; accent: string }
> = {
  lv1: {
    label: "Lv1 · 入门",
    subtitle: "什么是就业市场 / AI 怎么改变工作",
    description: "用生活类比讲清楚 AI 招聘的底层逻辑 — 适合从未接触过求职 / 初次了解 AI 行业的人。",
    accent: "emerald",
  },
  lv2: {
    label: "Lv2 · 职业百科",
    subtitle: "8 个 AI 岗 + 8 个传统职业每篇是什么",
    description: "对照 27 角色 / 8 传统职业的画像页，把每个职业用 6 岁能懂的方式重新讲一遍 — 适合定位前补功课。",
    accent: "amber",
  },
  lv3: {
    label: "Lv3 · 转岗路径",
    subtitle: "传统职业 → AI 怎么转",
    description: "电气 → 具身智能 / 机械 → 机器人 / 教师 → AI Education / 销售 → AI Sales 等具体路径 — 适合想动手转型的人。",
    accent: "indigo",
  },
};

export interface LearnArticleMeta {
  level: LearnLevel;
  slug: string;
  title: string;
  order: number;
  summary: string;
  linked_roles?: { market: "domestic" | "international"; role_id: string }[];
  linked_professions?: string[];
  reading_minutes?: number;
}

export interface LearnArticle extends LearnArticleMeta {
  content: string; // raw markdown body (frontmatter stripped)
}

const CONTENT_ROOT = path.join(process.cwd(), "..", "content", "learn");

function safeReadDir(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
}

export function loadArticlesByLevel(level: LearnLevel): LearnArticle[] {
  const dir = path.join(CONTENT_ROOT, level);
  const files = safeReadDir(dir);
  const articles: LearnArticle[] = files.map((file) => {
    const raw = fs.readFileSync(path.join(dir, file), "utf-8");
    const { data, content } = matter(raw);
    const slug = file.replace(/\.md$/, "").replace(/^\d+-/, "");
    return {
      level,
      slug,
      title: data.title ?? slug,
      order: typeof data.order === "number" ? data.order : 999,
      summary: data.summary ?? "",
      linked_roles: data.linked_roles ?? undefined,
      linked_professions: data.linked_professions ?? undefined,
      reading_minutes: data.reading_minutes ?? undefined,
      content,
    };
  });
  return articles.sort((a, b) => a.order - b.order);
}

export function loadAllArticles(): LearnArticle[] {
  return LEARN_LEVELS.flatMap((lv) => loadArticlesByLevel(lv));
}

export function findArticle(level: LearnLevel, slug: string): LearnArticle | null {
  return loadArticlesByLevel(level).find((a) => a.slug === slug) ?? null;
}

export function neighbors(
  level: LearnLevel,
  slug: string,
): { prev: LearnArticleMeta | null; next: LearnArticleMeta | null } {
  const all = loadArticlesByLevel(level);
  const idx = all.findIndex((a) => a.slug === slug);
  if (idx === -1) return { prev: null, next: null };
  return {
    prev: idx > 0 ? all[idx - 1] : null,
    next: idx < all.length - 1 ? all[idx + 1] : null,
  };
}
