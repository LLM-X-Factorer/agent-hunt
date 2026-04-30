"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";

interface NarrativeStats {
  totals: { all_jobs: number; labeled_jobs: number };
  p1_market_basic: { domestic_traditional_to_internet_ratio: number };
  p2_salary_premium: { premium_over_internet_pct: number };
  p4_cross_market: {
    native_intl_to_domestic_ratio: number;
    augmented_intl_to_domestic_ratio: number;
  };
  p5_ghost: { intl_to_domestic_ratio: number };
}

export default function Home() {
  const [stats, setStats] = useState<NarrativeStats | null>(null);

  useEffect(() => {
    fetch("/data/narrative-stats.json")
      .then((r) => r.json())
      .then(setStats);
  }, []);

  return (
    <div className="space-y-12 py-8">
      <header className="text-center space-y-3">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
          Agent Hunt
        </h1>
        <p className="text-lg text-gray-600">AI 招聘市场全景分析平台</p>
        {stats && (
          <p className="text-sm text-gray-500">
            基于 {stats.totals.all_jobs.toLocaleString()} 条 JD（{stats.totals.labeled_jobs.toLocaleString()} 条已 LLM 标注）
            <span className="mx-2">·</span>
            国内 + 海外双市场
          </p>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        <Link href="/narrative" className="group">
          <Card className="h-full transition-all group-hover:border-indigo-300 group-hover:shadow-md">
            <CardContent className="p-6 space-y-3">
              <div className="text-3xl">📖</div>
              <h2 className="text-xl font-bold">叙事手册</h2>
              <p className="text-sm text-gray-600 leading-relaxed">
                基于 8000+ 条 JD 提炼的 <strong>5 条市场判断</strong>，每条带数字 + 业务话术 + 数据来源。
              </p>
              <div className="text-xs text-gray-500 space-y-1 pt-2 border-t">
                <p>· 市场基本盘 · 薪资反直觉</p>
                <p>· 海外蓝海 · 跨市场套利</p>
                <p>· 海外幽灵岗集中度 3×</p>
              </div>
              <div className="pt-1">
                <span className="text-sm font-medium text-indigo-600 group-hover:text-indigo-800">
                  业务人员讲解 / 招生展示 →
                </span>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/roles" className="group">
          <Card className="h-full transition-all group-hover:border-amber-300 group-hover:shadow-md">
            <CardContent className="p-6 space-y-3">
              <div className="text-3xl">🧭</div>
              <h2 className="text-xl font-bold">按岗位探索</h2>
              <p className="text-sm text-gray-600 leading-relaxed">
                <strong>27 个角色簇</strong>（国内 15 + 海外 12），每个给出技能画像 / 薪资分位 / 适合谁不适合谁。
              </p>
              <div className="text-xs text-gray-500 space-y-1 pt-2 border-t">
                <p>· AI/LLM 工程师 · 算法工程师</p>
                <p>· ML Scientist · ML Engineer</p>
                <p>· AI 产品经理 · AI 运营 …</p>
              </div>
              <div className="pt-1">
                <span className="text-sm font-medium text-amber-600 group-hover:text-amber-800">
                  按岗位定位自己 →
                </span>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/report" className="group">
          <Card className="h-full transition-all group-hover:border-emerald-300 group-hover:shadow-md">
            <CardContent className="p-6 space-y-3">
              <div className="text-3xl">📊</div>
              <h2 className="text-xl font-bold">数据看板</h2>
              <p className="text-sm text-gray-600 leading-relaxed">
                7 个交互式 dashboard，跨市场技能 / 薪资 / 行业深度查询。
              </p>
              <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-xs text-gray-500 pt-2 border-t">
                <span>· 洞察报告</span>
                <span>· 技能图谱</span>
                <span>· 薪资分析</span>
                <span>· 市场差异</span>
                <span>· 行业分析</span>
                <span>· 岗位画像</span>
              </div>
              <div className="pt-1">
                <span className="text-sm font-medium text-emerald-600 group-hover:text-emerald-800">
                  深度查询 / 数据验证 →
                </span>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      <div className="text-center text-xs text-gray-400 max-w-2xl mx-auto pt-4">
        本站定位 = 内部叙事手册（业务人员讲解市场用）+ 数据自检工具。
        数据源 = 国内外主流招聘平台 + LLM 厂商官方 ATS + 社区招聘帖（HN / GitHub）+ levels.fyi 真实薪酬。
      </div>
    </div>
  );
}
