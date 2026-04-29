"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { NarrativeLayout } from "@/components/narrative-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface VendorRow {
  total: number;
  categories: Record<string, number>;
  client_facing_total: number;
  client_facing_pct: number;
  samples: Record<string, string[]>;
}

interface Data {
  by_vendor: Record<string, VendorRow>;
  summary: {
    total_vendors: number;
    total_jobs: number;
    total_client_facing: number;
    client_facing_pct: number;
  };
}

const VENDOR_LABEL: Record<string, string> = {
  vendor_openai: "OpenAI",
  vendor_anthropic: "Anthropic",
  vendor_xai: "xAI",
  vendor_cohere: "Cohere",
  vendor_deepmind: "DeepMind",
};

const CAT_LABEL: Record<string, string> = {
  fde: "Forward Deployed",
  solutions: "Solutions Engineer",
  applied: "Applied",
  deploy: "Deployment / Implementation",
  customer: "Customer Engineer / Success",
};

export default function P3() {
  const [d, setD] = useState<Data | null>(null);

  useEffect(() => {
    fetch("/data/vendor-title-breakdown.json").then((r) => r.json()).then(setD);
  }, []);

  if (!d) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const chart = Object.entries(d.by_vendor).map(([vendor, row]) => ({
    name: VENDOR_LABEL[vendor] || vendor,
    Forward_Deployed: row.categories.fde || 0,
    Solutions: row.categories.solutions || 0,
    Applied: row.categories.applied || 0,
    Deploy_Impl: row.categories.deploy || 0,
    Customer: row.categories.customer || 0,
    Core: row.categories.core || 0,
    pct: row.client_facing_pct,
  }));

  const topVendors = ["vendor_openai", "vendor_anthropic"]
    .map((id) => ({ id, label: VENDOR_LABEL[id], data: d.by_vendor[id] }))
    .filter((v) => v.data);

  return (
    <NarrativeLayout
      index={3}
      title="新岗位品类 · 桥梁工程师"
      headline="OpenAI / Anthropic 工程师里 ~17% 是「桥梁工程师」"
      metric={`${d.summary.total_client_facing}`}
      metricSub={`5 家 LLM 厂商 · 占 ${d.summary.client_facing_pct}%`}
      oneLiner="LLM 厂商招聘里有一类被中文世界严重低估的岗位——Forward Deployed / Solutions / Applied / Implementation Engineer，把 LLM 落地到客户业务的桥梁工程师。OpenAI 一家就 110 个，Anthropic 61 个。国内课程市场对这个岗位零覆盖——不是教算法、也不是教产品，是技术 + 客户沟通 + 解决方案三合一。这是早期蓝海。"
      copyText="OpenAI 和 Anthropic 招聘里，约 17% 是『Forward Deployed / Solutions / Applied / Implementation Engineer』——把 LLM 落地到客户业务的桥梁工程师。OpenAI 一家就 110 个，国内课程零覆盖。"
      dataSource={`基于 ${d.summary.total_jobs} 条 vendor_official 岗位 title 正则分类（5 家：OpenAI / Anthropic / xAI / Cohere / DeepMind）。分类首匹配优先，避免重复计算。完整模式见 backend/scripts/export_vendor_title_breakdown.py。`}
      deepLink={{ href: "/insights", label: "岗位画像（数据看板）" }}
      prev={{ href: "/narrative/p2", label: "论断 2 · 薪资反直觉" }}
      next={{ href: "/narrative/p4", label: "论断 4 · 跨市场套利" }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base">5 家 LLM 厂商 · 客户端工程师占比</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            前 5 类 = 客户端 / 桥梁角色 · 灰色 = 内部研发 / 产品 / 其他
          </p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chart} margin={{ top: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="Forward_Deployed" stackId="a" fill="#6366f1" name="Forward Deployed" />
              <Bar dataKey="Solutions" stackId="a" fill="#8b5cf6" name="Solutions Eng" />
              <Bar dataKey="Applied" stackId="a" fill="#a78bfa" name="Applied" />
              <Bar dataKey="Deploy_Impl" stackId="a" fill="#c084fc" name="Deployment/Impl" />
              <Bar dataKey="Customer" stackId="a" fill="#e9d5ff" name="Customer Eng/CS" />
              <Bar dataKey="Core" stackId="a" fill="#d1d5db" name="内部研发/其他" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {topVendors.map(({ id, label, data }) => (
          <Card key={id}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{label}</CardTitle>
              <p className="text-xs text-gray-500">
                {data.client_facing_total} / {data.total} 客户端岗位 · {data.client_facing_pct}%
              </p>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              {Object.entries(data.samples).map(([cat, titles]) => (
                <div key={cat}>
                  <p className="text-xs font-medium text-indigo-700 mb-1">
                    {CAT_LABEL[cat]} · {data.categories[cat]}
                  </p>
                  <ul className="text-xs text-gray-600 space-y-0.5 list-disc list-inside">
                    {titles.slice(0, 3).map((t, i) => (
                      <li key={i} className="truncate">{t}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    </NarrativeLayout>
  );
}
