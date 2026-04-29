"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { NarrativeLayout } from "@/components/narrative-layout";
import {
  CaveatBox, JobExampleCard, MechanismBox, MethodologyBox, SectionHeader,
  type JobExample,
} from "@/components/narrative-bits";
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

interface Examples {
  p3_vendor_examples: Record<string, Record<string, JobExample[]>>;
}

const VENDOR_LABEL: Record<string, string> = {
  vendor_openai: "OpenAI",
  vendor_anthropic: "Anthropic",
  vendor_xai: "xAI",
  vendor_cohere: "Cohere",
  vendor_deepmind: "DeepMind",
};

const CAT_LABEL: Record<string, string> = {
  fde: "Forward Deployed Engineer",
  solutions: "Solutions Engineer",
  applied: "Applied Engineer",
  deploy: "Deployment / Implementation",
  customer: "Customer / Technical Success",
};

export default function P3() {
  const [d, setD] = useState<Data | null>(null);
  const [ex, setEx] = useState<Examples | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/data/vendor-title-breakdown.json").then((r) => r.json()),
      fetch("/data/narrative-examples.json").then((r) => r.json()),
    ]).then(([a, b]) => { setD(a); setEx(b); });
  }, []);

  if (!d || !ex) return <div className="text-center py-20 text-gray-400">加载中...</div>;

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

  // Pull diverse examples across categories from OpenAI + Anthropic.
  const fdeExamples: JobExample[] = [
    ex.p3_vendor_examples.vendor_openai?.fde?.[0],
    ex.p3_vendor_examples.vendor_anthropic?.fde?.[0],
  ].filter(Boolean) as JobExample[];
  const solutionsExamples: JobExample[] = [
    ex.p3_vendor_examples.vendor_openai?.solutions?.[0],
    ex.p3_vendor_examples.vendor_openai?.solutions?.[1],
  ].filter(Boolean) as JobExample[];
  const otherExamples: JobExample[] = [
    ex.p3_vendor_examples.vendor_anthropic?.applied?.[0],
    ex.p3_vendor_examples.vendor_openai?.deploy?.[0],
  ].filter(Boolean) as JobExample[];

  const oai = d.by_vendor.vendor_openai;
  const anth = d.by_vendor.vendor_anthropic;

  return (
    <NarrativeLayout
      index={3}
      title="新岗位品类 · 桥梁工程师"
      headline="OpenAI / Anthropic 工程师里 ~17% 是「桥梁工程师」"
      metric={`${(oai?.client_facing_total || 0) + (anth?.client_facing_total || 0)}`}
      metricSub={`OpenAI ${oai?.client_facing_pct}% · Anthropic ${anth?.client_facing_pct}% · 中位 ~ 17%`}
      oneLiner="LLM 厂商招聘里有一类被中文世界严重低估的岗位——Forward Deployed / Solutions / Applied / Implementation Engineer，把 LLM 落地到客户业务的桥梁工程师。OpenAI 一家就 110 个，Anthropic 61 个。国内课程市场零覆盖——不是教算法，也不是教产品，是技术 + 客户沟通 + 解决方案三合一。"
      copyText="OpenAI 和 Anthropic 招聘里，约 17% 是『Forward Deployed / Solutions / Applied / Implementation Engineer』——把 LLM 落地到客户业务的桥梁工程师。OpenAI 一家就 110 个，国内课程零覆盖。"
      dataSource={`${d.summary.total_jobs} 条 vendor_official 岗位 title 正则分类（5 家：OpenAI / Anthropic / xAI / Cohere / DeepMind）。完整匹配规则：backend/scripts/export_vendor_title_breakdown.py。`}
      deepLink={{ href: "/insights", label: "岗位画像（数据看板）" }}
      prev={{ href: "/narrative/p2", label: "论断 2 · 薪资反直觉" }}
      next={{ href: "/narrative/p4", label: "论断 4 · 跨市场套利" }}
    >
      <MethodologyBox title="📐 这个数字哪来的（学员问就这么答）">
        <p>
          <strong>一句话：</strong>我们直接抓了 OpenAI / Anthropic / xAI / Cohere / DeepMind 5 家 LLM 厂商的官方招聘页，共 {d.summary.total_jobs} 条 JD——比 LinkedIn 干净（LinkedIn 有大量猎头转发噪音）。
        </p>
        <p>
          <strong>什么算「桥梁工程师」？</strong>title 里包含以下任一关键词：
        </p>
        <ul className="list-disc list-inside text-xs space-y-1 ml-2">
          <li><strong>Forward Deployed Engineer</strong>：派工程师驻场客户公司</li>
          <li><strong>Solutions Engineer / Architect</strong>：解决方案架构师</li>
          <li><strong>Applied Engineer</strong>：应用工程师</li>
          <li><strong>Deployment / Implementation Engineer</strong>：部署 / 实施</li>
          <li><strong>Customer / Technical Success Engineer</strong>：客户工程师</li>
        </ul>
        <p>
          <strong>17% 怎么算的：</strong>OpenAI {oai?.total} 条里 {oai?.client_facing_total} 条命中（{oai?.client_facing_pct}%），Anthropic {anth?.total} 条里 {anth?.client_facing_total} 条（{anth?.client_facing_pct}%），两家平均约 17%。
        </p>
        <p>
          <strong>这个数字是保守估计</strong>——如果把「Applied Research Scientist」这种也算进来能到 20%，但那不算客户端。我们只统计明确面客的 title。
        </p>
      </MethodologyBox>

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

      <SectionHeader>真实 JD 例子（OpenAI / Anthropic 官方 ATS 抓取）</SectionHeader>
      {fdeExamples.length > 0 && (
        <div>
          <p className="text-sm font-medium text-indigo-700 mb-3">🌐 Forward Deployed Engineer</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {fdeExamples.map((e, i) => <JobExampleCard key={i} ex={e} />)}
          </div>
        </div>
      )}
      {solutionsExamples.length > 0 && (
        <div>
          <p className="text-sm font-medium text-violet-700 mb-3">🔧 Solutions Engineer</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {solutionsExamples.map((e, i) => <JobExampleCard key={i} ex={e} />)}
          </div>
        </div>
      )}
      {otherExamples.length > 0 && (
        <div>
          <p className="text-sm font-medium text-purple-700 mb-3">🚀 Applied / Deployment</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {otherExamples.map((e, i) => <JobExampleCard key={i} ex={e} />)}
          </div>
        </div>
      )}

      <MechanismBox title="🧠 为什么会这样（一句话讲透）">
        <p className="text-base font-medium">
          LLM 落地是脏活累活，需要既懂技术又能跟客户对话的人。
        </p>
        <p>
          客户公司（医院 / 银行 / 政府）买了 OpenAI / Anthropic 的 API，但自己没有 ML 团队会用——于是 vendor 派工程师驻场：评估业务场景、设计 Agent / RAG 方案、在客户系统里实际部署、持续优化。这 4 步全都需要工程师能直接和客户业务方对话，不是写论文的研究员，也不是只画线框图的 PM。
        </p>
        <p>
          这个角色不是新发明——<strong>Palantir 已经验证了 20 年</strong>。OpenAI 现在大量招 FDE 就是在抄 Palantir 的剧本。
        </p>
        <p>
          <strong>这是早期抢人窗口：</strong>171 个岗位集中在 OpenAI/Anthropic 两家。Google / Microsoft 也在做但还没这么开放招聘。等 1-2 年所有 SaaS 都开始抄这个模式后，竞争会激烈起来。
        </p>
      </MechanismBox>

      <CaveatBox title="⚠️ 给学员讲的时候要说清楚">
        <p>
          <strong>✅ 这个数字适合讲：</strong>想出海做 AI、有客户沟通能力、又懂代码的学员，FDE / Solutions Engineer 是被中文世界严重低估的赛道。学员若是「技术男 + 想转客户岗 / 商业岗」，这是天然路径。
        </p>
        <p>
          <strong>❌ 不能这么说：「学完明天就能去 OpenAI 当 FDE」。</strong>
          这类岗位典型要求「6+ 年 SWE / MLE 经验 + 客户沟通 + 解决方案构建」——是<strong>高门槛资深岗</strong>，不是入门级。这条 narrative 适合作为「3-5 年职业方向感知」教学，不是「明天就能转行」。
        </p>
        <p>
          <strong>❌ 不能这么说：「国内也能找类似岗」。</strong>
          国内 LLM 厂商（智谱 / Moonshot / 百川 / MiniMax）招聘里几乎没有 FDE / Solutions Engineer 编制——中国 to-B 客户期待「免费部署 / 售前送服务」，没付费意愿支撑这类驻场角色。这条 narrative <strong>主要适用于有出海规划的学员</strong>。
        </p>
        <p>
          <strong>学员可能问：「国内为什么没有这种岗？」</strong>
          诚实答：to-B 商业模式不同。中国客户买 SaaS 期待免费部署支持；美国客户接受 vendor 派人驻场+独立计费——所以美国 vendor 才招得起这类岗。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
