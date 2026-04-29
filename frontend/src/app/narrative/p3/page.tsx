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
      <MethodologyBox>
        <p>
          <strong>5 家厂商：</strong>OpenAI ({oai?.total}) / Anthropic ({anth?.total}) / xAI / Cohere / DeepMind，全部直接抓自官方 ATS（Greenhouse / Ashby），共 {d.summary.total_jobs} 条 JD。这些 vendor 自己挂的岗位最干净——不像 LinkedIn 有大量再发布噪音。
        </p>
        <p>
          <strong>5 类客户端岗位（按 title 正则首匹配）：</strong>
        </p>
        <ul className="list-disc list-inside text-xs space-y-1 ml-2">
          <li><code className="bg-white px-1 rounded">forward deployed</code> → FDE</li>
          <li><code className="bg-white px-1 rounded">solutions engineer / solution architect</code> → Solutions</li>
          <li><code className="bg-white px-1 rounded">deployment / implementation / onboarding</code> → Deploy</li>
          <li><code className="bg-white px-1 rounded">applied (engineer / engineering / ai)</code> → Applied</li>
          <li><code className="bg-white px-1 rounded">customer success / customer engineer / technical success</code> → Customer</li>
        </ul>
        <p>
          <strong>「首匹配」</strong>意思是一个 title 只算一类，不重复计数。
          <strong>这是保守估计</strong>——更宽泛的 query（如 `title ~* &apos;applied&apos;`）会把 &quot;Applied Research Scientist&quot; 也算进来，得到「20%」。我们只算明确客户端的，所以是「~17%」。
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

      <MechanismBox>
        <p>
          <strong>LLM 落地是脏活：</strong>客户公司没有 ML 团队，但他们买了 OpenAI/Anthropic API 之后需要：① 评估什么场景能用 LLM，② 设计 Agent / RAG / 微调方案，③ 在客户的数据/系统里实际部署，④ 持续支持优化。这 4 步技术深度差别很大，但都需要工程师能直接和客户业务团队对话——不是写论文的研究员，也不是只画线框图的 PM。
        </p>
        <p>
          <strong>Palantir 教科书：</strong>FDE 这个角色在 Palantir 已经验证了 20 年——派工程师驻场客户公司，把通用平台改造成客户业务工具。OpenAI 招 FDE 时，明显是在抄 Palantir 的剧本。这个角色 base 比纯研究低，但有 carry / equity 上行。
        </p>
        <p>
          <strong>早期市场抢人：</strong>171 个岗位散落在 OpenAI/Anthropic 手里，对应到一个高度新颖的角色——既懂技术又能客户对话的人，市面上极少。Google/Microsoft 也在做但没像 OpenAI 这么极端开放招聘。所以这是个早期抢人窗口。
        </p>
      </MechanismBox>

      <CaveatBox>
        <p>
          <strong>1. 国内厂商基本无对应编制。</strong>
          智谱 / Moonshot / 百川 / MiniMax 招聘里几乎没有 FDE / Solutions Engineer 这类 title——中国 to-B 客户期待「免费部署 / 售前送服务」，没付费意愿支撑这类驻场角色。如果学员目标是国内市场，这条 narrative 不适用。
        </p>
        <p>
          <strong>2. 这是高门槛岗位。</strong>
          典型招聘描述里要求「6+ 年 SWE/MLE 经验 + 客户沟通 + 解决方案构建」——不是入门级。让学员一上来去申请 FDE 不现实。这条 narrative 适合作为「3-5 年职业方向感知」教学，不是「明天就能转行」。
        </p>
        <p>
          <strong>3. 所有数据来自官方 ATS，没含猎头转发。</strong>
          实际市场上还有更多类似岗位散落在 LinkedIn 等平台（被 Cognizant/Accenture 类咨询公司转发），但量级与品质都比不上 vendor_official。没纳入这个统计。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
