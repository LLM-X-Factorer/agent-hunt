#!/usr/bin/env python3
"""Generate AI-powered insights, JD samples, personas, and learning paths.

Reads from the database + calls Gemini API, outputs static JSON files
to frontend/public/data/ for Cloudflare Pages deployment.

Usage:
    cd backend && .venv/bin/python scripts/generate_insights.py
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import async_session
from app.models.job import Job
from app.models.skill import Skill
from app.services.llm import llm_json, llm_text
from app.services.skill_extractor import extractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "data"

DEFAULT_TEXT_SYSTEM = "你是一个资深的 AI 行业分析师，用中文输出。"
DEFAULT_JSON_SYSTEM = "你是一个资深的 AI 行业分析师。严格输出 JSON，不要添加任何额外文字。"


async def text_call(prompt: str, system: str = "", temperature: float = 0.7) -> str:
    return await llm_text(prompt, system=system or DEFAULT_TEXT_SYSTEM, temperature=temperature)


async def json_call(prompt: str, system: str = "") -> dict | list:
    return await llm_json(prompt, system=system or DEFAULT_JSON_SYSTEM, temperature=0.3)


async def load_stats(db: AsyncSession) -> dict:
    """Load key statistics for Gemini prompts."""
    jobs = (await db.execute(select(Job).where(Job.parse_status == "parsed"))).scalars().all()
    skills = (await db.execute(
        select(Skill).where(Skill.total_count > 0).order_by(Skill.total_count.desc())
    )).scalars().all()

    domestic = [j for j in jobs if j.market == "domestic"]
    international = [j for j in jobs if j.market == "international"]

    def avg_salary(job_list):
        sals = [s for j in job_list if (s := j.salary_mid_cny_monthly) is not None]
        return int(sum(sals) / len(sals)) if sals else 0

    return {
        "total_jobs": len(jobs),
        "domestic_jobs": len(domestic),
        "international_jobs": len(international),
        "domestic_avg_salary": avg_salary(domestic),
        "international_avg_salary": avg_salary(international),
        "top_skills": [
            {"name": s.canonical_name, "total": s.total_count,
             "domestic": s.domestic_count, "international": s.international_count}
            for s in skills[:20]
        ],
        "domestic_top5": [s.canonical_name for s in sorted(skills, key=lambda x: x.domestic_count, reverse=True)[:5]],
        "international_top5": [s.canonical_name for s in sorted(skills, key=lambda x: x.international_count, reverse=True)[:5]],
    }


async def generate_insights(stats: dict) -> dict:
    """Generate AI narrative insights for each page."""
    logger.info("Generating AI insights...")

    stats_text = json.dumps(stats, ensure_ascii=False, indent=2)

    insights = {}
    prompts = {
        "dashboard": f"""基于以下 AI Agent 岗位市场数据，写一段 200-300 字的市场总览洞察。
要求：用通俗易懂的语言，指出最关键的发现，给求职者实用建议。不要罗列数据，要讲故事。

数据：
{stats_text}""",

        "skills": f"""基于以下数据，写一段 200 字的技能图谱解读。
重点：哪些技能是必修课？哪些是加分项？国内外有什么差异？

Top 20 技能：{json.dumps(stats['top_skills'], ensure_ascii=False)}""",

        "salary": f"""基于以下数据，写一段 200 字的薪资分析解读。
国内平均月薪 ¥{stats['domestic_avg_salary']}，国际平均月薪 ¥{stats['international_avg_salary']}（折合人民币）。
重点：薪资差距的原因，什么技能/经验能拿高薪。""",

        "gaps": f"""基于以下数据，写一段 200 字的跨市场差异解读。
国内 Top 5：{stats['domestic_top5']}
国际 Top 5：{stats['international_top5']}
重点：差异背后的原因，对求职者的启示。""",
    }

    for key, prompt in prompts.items():
        insights[f"{key}_insight"] = await text_call(prompt)
        logger.info("  Generated %s insight", key)
        await asyncio.sleep(2)

    return insights


async def generate_job_samples(db: AsyncSession) -> dict:
    """Extract representative JD samples grouped by skill."""
    logger.info("Extracting JD samples...")

    skills = (await db.execute(
        select(Skill).where(Skill.total_count > 0).order_by(Skill.total_count.desc())
    )).scalars().all()
    top_skill_ids = [s.id for s in skills[:15]]

    jobs = (await db.execute(select(Job).where(Job.parse_status == "parsed"))).scalars().all()

    samples = {}
    for sid in top_skill_ids:
        skill = next(s for s in skills if s.id == sid)
        matching = []
        for job in jobs:
            all_skills = (job.required_skills or []) + (job.preferred_skills or [])
            normalized = [extractor.normalize(r) for r in all_skills]
            if sid in normalized and job.title:
                matching.append(job)

        # Pick up to 3 diverse samples (mix domestic + international)
        domestic = [j for j in matching if j.market == "domestic"][:2]
        international = [j for j in matching if j.market == "international"][:2]
        selected = (domestic + international)[:3]

        if selected:
            samples[sid] = {
                "skill_name": skill.canonical_name,
                "jobs": [
                    {
                        "title": j.title,
                        "company": j.company_name or "未知",
                        "location": j.location or "未知",
                        "market": "国内" if j.market == "domestic" else "国际",
                        "salary": f"¥{j.salary_min // 1000}k-{j.salary_max // 1000}k/月"
                        if j.salary_min and j.salary_max else "面议",
                        "skills": (j.required_skills or [])[:8],
                        "snippet": (j.raw_content or "")[:300],
                    }
                    for j in selected
                ],
            }

    return samples


async def generate_personas(stats: dict) -> list:
    """Generate job personas using Gemini."""
    logger.info("Generating personas...")

    prompt = f"""基于以下 AI Agent 工程师市场数据，生成 3 个典型岗位画像的 JSON 数组。

数据摘要：
- 国内 {stats['domestic_jobs']} 条 JD，平均月薪 ¥{stats['domestic_avg_salary']}
- 国际 {stats['international_jobs']} 条 JD，平均月薪 ¥{stats['international_avg_salary']}（折合人民币）
- 国内热门技能：{stats['domestic_top5']}
- 国际热门技能：{stats['international_top5']}

要求生成 3 个画像：
1. 国内 AI Agent 工程师（典型）
2. 国际 AI Agent 工程师（典型）
3. 远程 AI Agent 工程师（新兴）

每个画像 JSON 格式：
{{
  "id": "domestic_typical",
  "title": "画像名称",
  "subtitle": "一句话描述",
  "market": "国内/国际/远程",
  "core_skills": ["技能1", "技能2", ...],
  "salary_range": "薪资范围",
  "experience": "经验要求",
  "education": "学历要求",
  "company_types": "典型公司类型",
  "work_mode": "工作模式",
  "day_in_life": "一天的工作描述（100字）",
  "key_insight": "关键洞察（一句话）"
}}"""

    return await json_call(prompt)


async def generate_learning_paths(stats: dict) -> list:
    """Generate learning path recommendations using Gemini."""
    logger.info("Generating learning paths...")

    prompt = f"""基于以下 AI Agent 工程师市场数据，生成 4 条学习路径的 JSON 数组。

市场热门技能：
- 国内：{stats['domestic_top5']}
- 国际：{stats['international_top5']}
- 全局 Top 10：{[s['name'] for s in stats['top_skills'][:10]]}

要求 4 条路径：
1. Python 后端工程师 → AI Agent 工程师
2. 前端工程师 → AI Agent 全栈工程师
3. 应届生 → AI Agent 工程师入门
4. 国内工程师 → 出海/国际岗位

每条路径 JSON 格式：
{{
  "id": "python_to_agent",
  "title": "路径名称",
  "subtitle": "一句话描述",
  "target_audience": "适合谁",
  "assumed_skills": ["已有技能1", "已有技能2"],
  "target_role": "目标岗位",
  "duration": "预计学习周期",
  "steps": [
    {{
      "order": 1,
      "title": "步骤标题",
      "description": "详细说明（50-80字）",
      "skills": ["要学的技能"],
      "resources_hint": "推荐学习资源方向"
    }}
  ],
  "key_advice": "最重要的一条建议"
}}"""

    return await json_call(prompt)


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_session() as db:
        stats = await load_stats(db)
        logger.info("Loaded stats: %d jobs, %d skills", stats["total_jobs"], len(stats["top_skills"]))

        # 1. AI Insights
        insights = await generate_insights(stats)
        (OUTPUT_DIR / "insights.json").write_text(
            json.dumps(insights, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Written insights.json")

        # 2. JD Samples
        samples = await generate_job_samples(db)
        (OUTPUT_DIR / "job-samples.json").write_text(
            json.dumps(samples, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Written job-samples.json (%d skills)", len(samples))

        # 3. Personas
        personas = await generate_personas(stats)
        (OUTPUT_DIR / "personas.json").write_text(
            json.dumps(personas, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Written personas.json")

        await asyncio.sleep(2)

        # 4. Learning Paths
        paths = await generate_learning_paths(stats)
        (OUTPUT_DIR / "learning-paths.json").write_text(
            json.dumps(paths, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Written learning-paths.json")

    logger.info("All insights generated!")


if __name__ == "__main__":
    asyncio.run(main())
