"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";

const NARRATIVES = [
  {
    id: "p1",
    title: "市场基本盘",
    headline: "传统行业 AI 增强需求 = 互联网的 3.4×",
    metric: "3.4×",
    summary:
      "国内招聘市场里，医疗 / 制造 / 汽车 / 金融 / 教育的 AI 增强需求加起来是互联网行业的 3.4 倍。市面所有 AI 课程都在教程序员转 AI 程序员——传统行业用 AI 这条赛道无人覆盖。",
  },
  {
    id: "p2",
    title: "薪资反直觉",
    headline: "医疗/制造/金融的 AI 增强岗，比互联网高 20%",
    metric: "+20%",
    summary:
      "学员心里默认「互联网 = 高薪」。但在 AI 增强方向，互联网 25k；医疗 / 制造 / 金融 30k；能源 48k——传统行业反向溢价。",
  },
  {
    id: "p3",
    title: "新岗位品类",
    headline: "OpenAI / Anthropic 工程师里 ~17% 是「桥梁工程师」",
    metric: "171",
    summary:
      "Forward Deployed / Solutions / Applied / Implementation Engineer——把 LLM 落地到客户业务。OpenAI 一家就 110 个，Anthropic 61 个。国内课程市场零覆盖。",
  },
  {
    id: "p4",
    title: "跨市场套利",
    headline: "海外 AI 增强是国内的 4.6×",
    metric: "4.6×",
    summary:
      "AI 原生海外是国内 3.96 倍；AI 增强海外是国内 4.6 倍。出海做 AI 增强反而比出海做算法的套利空间更大——传统行业 + AI + 海外是三重叠加。",
  },
  {
    id: "p5",
    title: "预期管理",
    headline: "海外幽灵岗集中度是国内 3×",
    metric: "3×",
    summary:
      "海外岗位「同公司同标题重复发」远多于国内。Deloitte 一个 Full Stack 标题挂 19 次，Meta 同样 PM 标题 17 次。海外岗位数量 ≠ hiring slot，建议先打 30% 折扣。",
  },
];

export default function NarrativePage() {
  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">叙事手册</h1>
        <p className="text-gray-600">
          基于 8000+ 条真实 JD 数据提炼的 5 条市场判断。每条都有完整数据、对比基线和业务复述话术——让任何业务人员都能讲清 AI 招聘市场。
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {NARRATIVES.map((n, i) => (
          <Link key={n.id} href={`/narrative/${n.id}`} className="group">
            <Card className="h-full transition-all group-hover:border-indigo-300 group-hover:shadow-md">
              <CardContent className="p-6 space-y-3 h-full flex flex-col">
                <div className="flex items-baseline gap-2">
                  <span className="text-xs text-gray-400 font-mono">论断 {i + 1}</span>
                  <span className="text-xs text-indigo-600 font-medium">· {n.title}</span>
                </div>
                <div className="text-3xl font-bold text-indigo-600">{n.metric}</div>
                <h2 className="text-base font-semibold leading-snug">{n.headline}</h2>
                <p className="text-sm text-gray-600 leading-relaxed flex-1">{n.summary}</p>
                <div className="text-xs text-indigo-600 font-medium pt-2 border-t group-hover:text-indigo-800">
                  查看完整数据 →
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="bg-gray-50 rounded-lg p-6 text-sm text-gray-600 space-y-2">
        <p className="font-medium text-gray-900">使用说明</p>
        <p>
          每条论断的详情页都包含：① 大标题（一句话结论）② 关键数字（招生展示用）③ 支撑数据图表 ④ 60 字业务复述话术（一键复制）⑤ 数据来源 + 深度看板链接。
        </p>
        <p>所有数据从后端 export 脚本生成的 JSON 静态读取，无后端依赖。</p>
      </div>
    </div>
  );
}
