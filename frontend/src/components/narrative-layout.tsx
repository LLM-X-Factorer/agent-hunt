"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";

interface Props {
  index: number;
  title: string;
  headline: string;
  metric: string;
  metricSub?: string;
  oneLiner: string;
  copyText: string;
  dataSource: string;
  deepLink?: { href: string; label: string };
  prev?: { href: string; label: string };
  next?: { href: string; label: string };
  children: React.ReactNode;
}

export function NarrativeLayout({
  index,
  title,
  headline,
  metric,
  metricSub,
  oneLiner,
  copyText,
  dataSource,
  deepLink,
  prev,
  next,
  children,
}: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(copyText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <nav className="text-xs text-gray-500">
        <Link href="/narrative" className="hover:text-gray-900">叙事手册</Link>
        <span className="mx-2">/</span>
        <span>论断 {index} · {title}</span>
      </nav>

      <header className="space-y-4 py-6">
        <p className="text-sm text-indigo-600 font-medium">论断 {index} · {title}</p>
        <h1 className="text-3xl md:text-4xl font-bold leading-tight">{headline}</h1>
        <div className="flex items-baseline gap-3 pt-2">
          <span className="text-6xl md:text-7xl font-bold text-indigo-600 tracking-tight">
            {metric}
          </span>
          {metricSub && <span className="text-base text-gray-600">{metricSub}</span>}
        </div>
        <p className="text-base text-gray-700 leading-relaxed pt-2 border-t">
          {oneLiner}
        </p>
      </header>

      <div className="space-y-6">{children}</div>

      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <p className="text-xs font-semibold text-indigo-700 mb-2">📋 业务人员一句话（招生 / 讲解直接复述）</p>
            <p className="text-sm text-gray-800 leading-relaxed">{copyText}</p>
          </div>
          <button
            onClick={handleCopy}
            className="shrink-0 px-3 py-1.5 text-xs font-medium bg-white border border-indigo-200 rounded-md hover:bg-indigo-100 transition-colors"
          >
            {copied ? "✓ 已复制" : "复制"}
          </button>
        </div>
      </div>

      <div className="text-xs text-gray-500 space-y-2 pt-4 border-t">
        <p>📊 <span className="font-medium">数据来源：</span>{dataSource}</p>
        {deepLink && (
          <p>
            🔗 <span className="font-medium">深度数据：</span>
            <Link href={deepLink.href} className="text-indigo-600 hover:text-indigo-800">
              {deepLink.label}
            </Link>
          </p>
        )}
      </div>

      <div className="flex justify-between pt-6 text-sm">
        {prev ? (
          <Link href={prev.href} className="text-gray-600 hover:text-gray-900">
            ← {prev.label}
          </Link>
        ) : (
          <span />
        )}
        {next ? (
          <Link href={next.href} className="text-gray-600 hover:text-gray-900">
            {next.label} →
          </Link>
        ) : (
          <span />
        )}
      </div>
    </div>
  );
}
