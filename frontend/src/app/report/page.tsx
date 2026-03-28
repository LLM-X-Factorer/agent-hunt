"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Report {
  overview: string;
  key_findings: string;
  industry_deep_dive: string;
  career_guide: string;
  trends: string;
}

export default function ReportPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/data/report.json")
      .then((r) => r.json())
      .then((d) => { setReport(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-400">加载中...</div>;
  if (!report) return <div className="text-center py-20 text-gray-400">报告尚未生成</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center py-8">
        <h1 className="text-3xl font-bold">AI 职业市场洞察报告</h1>
        <p className="text-gray-500 mt-2">
          基于国内外 5 大招聘平台真实 JD 数据，AI 驱动生成
        </p>
      </div>

      {/* Key Findings */}
      <Card className="border-indigo-200 bg-indigo-50/50">
        <CardHeader>
          <CardTitle className="text-lg">核心发现</CardTitle>
        </CardHeader>
        <CardContent>
          <MarkdownContent text={report.key_findings} />
        </CardContent>
      </Card>

      {/* Overview */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <span className="text-indigo-500">01</span> 全景概览
        </h2>
        <Card>
          <CardContent className="pt-6">
            <MarkdownContent text={report.overview} />
          </CardContent>
        </Card>
      </section>

      {/* Industry Deep Dive */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <span className="text-indigo-500">02</span> 行业深度分析
        </h2>
        <Card>
          <CardContent className="pt-6">
            <MarkdownContent text={report.industry_deep_dive} />
          </CardContent>
        </Card>
      </section>

      {/* Career Guide */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <span className="text-indigo-500">03</span> 跨界求职指南
        </h2>
        <Card>
          <CardContent className="pt-6">
            <MarkdownContent text={report.career_guide} />
          </CardContent>
        </Card>
      </section>

      {/* Trends */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <span className="text-indigo-500">04</span> 趋势判断
        </h2>
        <Card>
          <CardContent className="pt-6">
            <MarkdownContent text={report.trends} />
          </CardContent>
        </Card>
      </section>

      <div className="text-center text-xs text-gray-400 py-8">
        本报告由 Gemini AI 基于真实 JD 数据生成 · Agent Hunt
      </div>
    </div>
  );
}

function MarkdownContent({ text }: { text: string }) {
  const html = text
    .replace(/### (.+)/g, '<h3 class="text-lg font-bold mt-6 mb-2">$1</h3>')
    .replace(/## (.+)/g, '<h2 class="text-xl font-bold mt-6 mb-3">$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^\- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal">$1</li>')
    .replace(/\n\n/g, '</p><p class="mt-3">')
    .replace(/\n/g, "<br/>");

  return (
    <div
      className="prose prose-sm max-w-none text-gray-700 leading-relaxed [&_strong]:text-gray-900 [&_h3]:text-gray-900 [&_h2]:text-gray-900"
      dangerouslySetInnerHTML={{ __html: `<p>${html}</p>` }}
    />
  );
}
