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
      <MethodologyBox>
        <p>
          <strong>「幽灵岗」怎么定义的：</strong>同一个 company + 同一个 title 在采集窗口内出现 ≥ 5 次（variant_count ≥ 5），就算一个「幽灵岗簇」。这不能 100% 证明岗位是假的——可能是部门多坑都需要同样人，或者 LinkedIn 发岗后下架重发。但 5 次 + 时间窗口已经超过正常重发频率。
        </p>
        <p>
          <strong>分母选取：</strong>海外 5,477 条 JD（vendor_official + LinkedIn + Indeed + HN/GitHub）；国内 2,771 条（Boss + Liepin + Lagou + 国内 vendor）。各自找 ≥ 5 次重复的 cluster。
        </p>
        <p>
          <strong>重发率（更宽松信号）：</strong>采集到的 8,634 条 JD 里整体 repost_ratio = {(q.overall.repost_ratio * 100).toFixed(1)}%（即 {q.overall.reposted.toLocaleString()} 条是被重复见过的）。但重发本身不一定是幽灵——是同 company+title 大量重复才是幽灵。
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

      <MechanismBox>
        <p>
          <strong>HR KPI 驱动：</strong>美国大公司 HR 部门考核「岗位活跃度」（active job postings）——挂越多看上去 talent pipeline 越健康。下架重发是常规动作，不是欺诈。但对求职者制造了「岗位真多」的错觉。
        </p>
        <p>
          <strong>LinkedIn 产品设计：</strong>LinkedIn Jobs 按「最近 24 小时新岗」排序，公司若不重发岗位就掉出可见区。这是产品强迫公司刷岗，不是公司主动作恶。
        </p>
        <p>
          <strong>国内 Boss 反作弊更严：</strong>Boss 直聘 / 猎聘对同账户重复发岗有限流（同 title + company 重发会被打压）。国内市场刷岗成本更高，所以幽灵岗集中度低。但这不等于国内 hiring 健康——可能只是噪音被平台过滤掉了，候选人看到的是「干净版」。
        </p>
        <p>
          <strong>给学员的 30% 折扣：</strong>看到 LinkedIn 上「美国 AI 工程师 5,000 个 active jobs」时，按 0.6× 算实际 hiring slot 数（去掉幽灵 + 转发噪音），按 0.7× 进一步折现 visa 摩擦——大约剩 0.4× 是真正可申请的岗位。
        </p>
      </MechanismBox>

      <CaveatBox>
        <p>
          <strong>1. 国内幽灵岗未必真的少。</strong>
          国内主流招聘平台反爬严，Boss / Lagou 单次只能拿到分页前几页。可能国内也有大量幽灵岗只是我们采不到——这个 0.18% 的数字是「采集到的样本里」的比例，不是市场全貌。
        </p>
        <p>
          <strong>2. ≥ 5 次重复门槛是任意选的。</strong>
          换成 ≥ 3 次会显著放大数字（更多公司命中），换成 ≥ 10 次会缩到只剩 Deloitte / Meta 等几家。这个 0.55% / 0.18% 是基于 5 次门槛——在合理范围内调整不影响 3× 这个量级。
        </p>
        <p>
          <strong>3. 不是所有重复都是幽灵岗。</strong>
          Meta 同样的 PM 标题 17 个，可能确实是 17 个不同部门的相同 title。但如果 Deloitte 一个 Full Stack 重发 19 次，更可能是单一岗位反复发布。无法 100% 区分，所以这个数字是上限估计。
        </p>
      </CaveatBox>
    </NarrativeLayout>
  );
}
