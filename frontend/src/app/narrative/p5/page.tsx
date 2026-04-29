"use client";

import { useEffect, useState } from "react";
import { NarrativeLayout } from "@/components/narrative-layout";
import {
  CaveatBox, MechanismBox, MethodologyBox, SectionHeader,
} from "@/components/narrative-bits";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Ghost {
  company: string;
  title: string;
  variant_count: number;
  markets: string[];
  platforms: string[];
}

interface Stats {
  p5_ghost: {
    intl_ghost_clusters: number;
    intl_total_jobs: number;
    intl_ghost_pct: number;
    domestic_ghost_clusters: number;
    domestic_total_jobs: number;
    domestic_ghost_pct: number;
    intl_to_domestic_ratio: number;
    top_ghost_listings: Ghost[];
  };
}

interface QualitySignals {
  overall: { repost_ratio: number; reposted: number; total: number };
  by_platform: { platform: string; total: number; reposted: number; repost_ratio: number }[];
  top_reposting_companies?: { company: string; reposted: number; total: number }[];
}

export default function P5() {
  const [s, setS] = useState<Stats | null>(null);
  const [q, setQ] = useState<QualitySignals | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/data/narrative-stats.json").then((r) => r.json()),
      fetch("/data/jobs-quality-signals.json").then((r) => r.json()),
    ]).then(([a, b]) => { setS(a); setQ(b); });
  }, []);

  if (!s || !q) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const g = s.p5_ghost;

  return (
    <NarrativeLayout
      index={5}
      title="预期管理 · 幽灵岗"
      headline="海外幽灵岗集中度是国内的 3 倍"
      metric={`${g.intl_to_domestic_ratio}×`}
      metricSub={`海外 ${g.intl_ghost_pct}% · 国内 ${g.domestic_ghost_pct}%（占总 JD 比）`}
      oneLiner="学员看 LinkedIn 发现海外岗位多，建议先打 30% 折扣。海外 AI 招聘里同公司同岗位重复发布远多于国内——Deloitte 一个 Full Stack Engineer 标题挂了 19 次，Meta 同样的 PM 标题 17 次。岗位数量不等于实际 hiring slot。"
      copyText="海外 LinkedIn 上同公司同岗位重复发布是国内的 3 倍。Deloitte 的 Full Stack Engineer 挂了 19 次，Meta 的 PM 17 次。海外岗位数量 ≠ hiring slot——建议先打 30% 折扣。"
      dataSource={`Ghost cluster 定义：同 company + 同 title 出现 ≥ 5 次。海外 ${g.intl_ghost_clusters} 簇 / ${g.intl_total_jobs.toLocaleString()} 总 JD = ${g.intl_ghost_pct}%；国内 ${g.domestic_ghost_clusters} 簇 / ${g.domestic_total_jobs.toLocaleString()} 总 JD = ${g.domestic_ghost_pct}%。`}
      deepLink={{ href: "/report", label: "完整洞察报告（数据看板）" }}
      prev={{ href: "/narrative/p4", label: "论断 4 · 跨市场套利" }}
    >
      <MethodologyBox title="📐 这个数字哪来的（学员问就这么答）">
        <p>
          <strong>什么算「幽灵岗」：</strong>同一家公司同一个岗位标题，在采集窗口内出现 5 次或以上。比如 Deloitte 一个「Full Stack Engineer」标题挂了 19 次——这不能 100% 证明岗位是假的（可能是不同部门都需要类似人），但 5 次重发已经远超正常的「下架重发」频率。
        </p>
        <p>
          <strong>分子分母：</strong>海外端采了 LinkedIn / Indeed / 大厂官网共 5,477 条 AI 相关 JD，里面有 30 个这种重发集群（占 0.55%）。国内端采了 Boss / 猎聘 / 拉勾 / 国内大厂共 2,771 条，只 5 个集群（占 0.18%）。海外集中度大约是国内 3 倍。
        </p>
        <p>
          <strong>这是上限估计，不是确证。</strong>「同公司同标题重复」是<strong>嫌疑信号</strong>，不能等同于「岗位是假的」。但 19 次、17 次这种极端值，几乎可以确定是单一岗位反复发布。
        </p>
      </MethodologyBox>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">海外（LinkedIn / Indeed / vendor）</p>
            <p className="text-3xl font-bold text-rose-500">{g.intl_ghost_pct}%</p>
            <p className="text-xs text-gray-500">
              {g.intl_ghost_clusters} 个幽灵岗簇 / {g.intl_total_jobs.toLocaleString()} 总 JD
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 space-y-2">
            <p className="text-xs text-gray-500">国内（Boss / Liepin / Lagou / vendor）</p>
            <p className="text-3xl font-bold text-emerald-600">{g.domestic_ghost_pct}%</p>
            <p className="text-xs text-gray-500">
              {g.domestic_ghost_clusters} 个幽灵岗簇 / {g.domestic_total_jobs.toLocaleString()} 总 JD
            </p>
          </CardContent>
        </Card>
      </div>

      <SectionHeader>幽灵岗 Top 10（按重复发布次数）</SectionHeader>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">同 company + title 出现 ≥ 5 次的簇</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            按重复次数降序。注意 platforms / markets 字段——绝大多数集中在 LinkedIn + 海外。
          </p>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="py-2 pr-4">公司</th>
                  <th className="py-2 pr-4">岗位标题</th>
                  <th className="py-2 pr-4 text-right">重复</th>
                  <th className="py-2 pr-4">市场</th>
                  <th className="py-2">平台</th>
                </tr>
              </thead>
              <tbody>
                {g.top_ghost_listings.map((row, i) => (
                  <tr key={i} className="border-b last:border-0 text-gray-700">
                    <td className="py-2 pr-4 font-medium">{row.company}</td>
                    <td className="py-2 pr-4">{row.title}</td>
                    <td className="py-2 pr-4 text-right tabular-nums">{row.variant_count}×</td>
                    <td className="py-2 pr-4 text-xs text-gray-500">{row.markets.join("/")}</td>
                    <td className="py-2 text-xs text-gray-500">{row.platforms.join("/")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {q.top_reposting_companies && q.top_reposting_companies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">补充：刷岗最严重的公司（按 reposted 数）</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
              {q.top_reposting_companies.slice(0, 10).map((c, i) => (
                <div key={i} className="flex justify-between border-b py-1.5 last:border-0">
                  <span className="font-medium text-gray-700">{c.company}</span>
                  <span className="text-gray-500 tabular-nums">
                    {c.reposted} 重发 / {c.total} 总 ({(c.reposted / c.total * 100).toFixed(0)}%)
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <MechanismBox title="🧠 为什么会这样（一句话讲透）">
        <p className="text-base font-medium">
          海外公司被 LinkedIn 的产品逻辑逼着刷岗，国内 Boss 反作弊更严。
        </p>
        <p>
          <strong>LinkedIn Jobs 按「最近 24 小时新岗」排序。</strong>公司不重发就掉出可见区——产品在逼公司刷岗，不是公司主动作恶。同时美国大公司 HR 部门考核「岗位活跃度」（挂越多看上去人才管线越健康），下架重发是 KPI 动作。两者叠加 → 海外幽灵岗多。
        </p>
        <p>
          <strong>Boss 直聘 / 猎聘对同账户重复发岗有限流。</strong>同 title + company 重发会被算法打压，国内刷岗成本更高，所以集中度低。
        </p>
        <p className="bg-amber-100 border-l-4 border-amber-400 p-3 rounded">
          <strong>给学员的实用建议：</strong>看到「美国 AI 工程师 5,000 个 active jobs」时，先打 0.6× 折扣去掉幽灵岗 + 转发噪音；再打 0.7× 折扣考虑签证摩擦。最终大约 <strong>40% 才是真正可申请的岗位</strong>——所以 5,000 看上去多，实际能投的只有 2,000。
        </p>
      </MechanismBox>

      <CaveatBox title="⚠️ 给学员讲的时候要说清楚">
        <p>
          <strong>✅ 这个数字适合讲：</strong>「海外岗位看着多 ≠ 实际 hiring 机会多」——给学员一个心理预期管理。投海外岗时建议精准投递，看公司 / 团队 / JD 描述差异，而不是海投。
        </p>
        <p>
          <strong>❌ 不能这么说：「国内招聘市场更健康」。</strong>
          国内招聘平台反爬严，Boss / 拉勾单次只能拿前几页——可能国内也有大量幽灵岗只是我们采不到。这个 0.18% 是「采集到的样本里」的比例，不是市场全貌。
        </p>
        <p>
          <strong>❌ 不能这么说：「看到 Meta 17 个 PM 重发，所以 Meta 不靠谱」。</strong>
          Meta 17 个 PM 同标题<strong>可能确实是 17 个不同部门</strong>——FB Apps、Reality Labs、AI、Infra 各招 PM。无法 100% 区分单一岗位反复发布 vs 真的多个部门同标题。这个 3× 是<strong>上限估计</strong>。
        </p>
        <p>
          <strong>学员可能问：「投了海外岗几个月没回应，是不是都是幽灵岗？」</strong>
          诚实答：幽灵岗只解释了一部分（顶多 30-40%）。剩下的没回应原因更多是：① 公司优先内部 referral；② 海外签证倾向本地候选人；③ JD 描述虚高，实际偏好资深 senior。建议精准投 + 找 referral，不是单纯多投。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
