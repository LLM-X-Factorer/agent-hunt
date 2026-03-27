"use client";

import { useEffect, useState } from "react";
import { api, type Persona, type LearningPath } from "@/lib/api";
import { skillLabel } from "@/lib/labels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function InsightsPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.personas(), api.learningPaths()]).then(([p, l]) => {
      setPersonas(p);
      setPaths(l);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-400">加载中...</div>;

  const activePath = paths.find((p) => p.id === selectedPath);

  return (
    <div className="space-y-8">
      {/* Personas */}
      <div>
        <h1 className="text-2xl font-bold">岗位画像</h1>
        <p className="text-gray-500 mt-1">基于真实 JD 数据凝练的典型岗位画像</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {personas.map((p) => (
          <Card key={p.id} className="flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  p.market === "国内" ? "bg-red-100 text-red-700"
                  : p.market === "国际" ? "bg-blue-100 text-blue-700"
                  : "bg-green-100 text-green-700"
                }`}>
                  {p.market}
                </span>
                <span className="text-xs text-gray-400">{p.work_mode}</span>
              </div>
              <CardTitle className="text-lg">{p.title}</CardTitle>
              <p className="text-sm text-gray-500">{p.subtitle}</p>
            </CardHeader>
            <CardContent className="flex-1 space-y-3 text-sm">
              <div>
                <p className="text-gray-500 mb-1">核心技能</p>
                <div className="flex flex-wrap gap-1">
                  {p.core_skills.map((sk) => (
                    <Badge key={sk} variant="secondary" className="text-xs">
                      {skillLabel(sk)}
                    </Badge>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div><span className="text-gray-500">薪资范围</span><br /><span className="font-medium">{p.salary_range}</span></div>
                <div><span className="text-gray-500">经验要求</span><br /><span className="font-medium">{p.experience}</span></div>
                <div><span className="text-gray-500">学历要求</span><br /><span className="font-medium">{p.education}</span></div>
                <div><span className="text-gray-500">公司类型</span><br /><span className="font-medium">{p.company_types}</span></div>
              </div>
              <div className="border-t pt-3">
                <p className="text-gray-500 mb-1">一天的工作</p>
                <p className="text-gray-700 text-xs leading-relaxed">{p.day_in_life}</p>
              </div>
              <div className="bg-indigo-50 rounded p-2 text-xs text-indigo-700">
                💡 {p.key_insight}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Learning Paths */}
      <div className="pt-4">
        <h2 className="text-2xl font-bold">学习路径推荐</h2>
        <p className="text-gray-500 mt-1">选择你的起点，获取个性化的技能学习建议</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {paths.map((p) => (
          <Card
            key={p.id}
            className={`cursor-pointer transition-all ${
              selectedPath === p.id ? "border-indigo-400 ring-2 ring-indigo-100" : "hover:border-gray-300"
            }`}
            onClick={() => setSelectedPath(selectedPath === p.id ? null : p.id)}
          >
            <CardContent className="pt-5">
              <p className="font-medium text-sm">{p.title}</p>
              <p className="text-xs text-gray-500 mt-1">{p.subtitle}</p>
              <p className="text-xs text-gray-400 mt-2">适合：{p.target_audience}</p>
              <p className="text-xs text-gray-400">周期：{p.duration}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {activePath && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">{activePath.title}</CardTitle>
            <p className="text-sm text-gray-500">
              目标：{activePath.target_role} · 已有技能：{activePath.assumed_skills.join(", ")}
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activePath.steps.map((step) => (
                <div key={step.order} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-sm font-bold">
                      {step.order}
                    </div>
                    {step.order < activePath.steps.length && (
                      <div className="w-0.5 flex-1 bg-indigo-100 mt-1" />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <p className="font-medium text-sm">{step.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{step.description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {step.skills.map((sk) => (
                        <Badge key={sk} variant="outline" className="text-xs">
                          {skillLabel(sk)}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-xs text-gray-400 mt-1">📚 {step.resources_hint}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 bg-amber-50 rounded-lg p-4 text-sm text-amber-800">
              ⭐ <strong>最重要的建议：</strong>{activePath.key_advice}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
