#!/usr/bin/env python3
"""Generate a structured AI job market insight report using Gemini.

Reads full dataset from DB, computes stats, then generates a narrative report
with industry deep-dives, cross-domain career advice, and trend analysis.

Usage:
    cd backend && .venv/bin/python scripts/generate_report.py
"""
import asyncio
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from google import genai
from google.genai import types
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database import async_session
from app.models.job import Job
from app.models.skill import Skill
from app.services.skill_extractor import extractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "data"


def gemini_call(prompt: str, system: str = "", max_tokens: int = 8000) -> str:
    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system or (
                "你是一位资深的 AI 行业分析师和职业规划专家。"
                "你擅长将数据转化为有洞察力的叙事，帮助求职者做出职业决策。"
                "用中文输出，语言生动有温度，避免学术化表达。"
                "引用具体数据来支撑你的观点。"
            ),
            temperature=0.7,
        ),
    )
    return response.text.strip()


async def collect_full_stats(db: AsyncSession) -> dict:
    """Collect comprehensive stats for report generation."""
    jobs = (await db.execute(
        select(Job).where(Job.parse_status == "parsed")
    )).scalars().all()

    skills = (await db.execute(
        select(Skill).where(Skill.total_count > 0).order_by(Skill.total_count.desc())
    )).scalars().all()

    # Basic counts
    domestic = [j for j in jobs if j.market == "domestic"]
    international = [j for j in jobs if j.market == "international"]

    # Industry breakdown
    industry_stats = defaultdict(lambda: {
        "count": 0, "domestic": 0, "international": 0,
        "salaries": [], "skills": defaultdict(int),
        "titles": [], "companies": set(),
    })

    for j in jobs:
        if not j.industry:
            continue
        ind = industry_stats[j.industry]
        ind["count"] += 1
        if j.market == "domestic":
            ind["domestic"] += 1
        else:
            ind["international"] += 1
        if j.salary_min and j.salary_max:
            ind["salaries"].append((j.salary_min + j.salary_max) // 2)
        if j.title:
            ind["titles"].append(j.title)
        if j.company_name:
            ind["companies"].add(j.company_name)
        for raw in (j.required_skills or []) + (j.preferred_skills or []):
            sid = extractor.normalize(raw)
            if sid:
                ind["skills"][sid] += 1

    # Format for prompt
    industry_summary = {}
    for ind_name, data in sorted(industry_stats.items(), key=lambda x: x[1]["count"], reverse=True):
        avg_sal = int(sum(data["salaries"]) / len(data["salaries"])) if data["salaries"] else 0
        top_skills = sorted(data["skills"].items(), key=lambda x: x[1], reverse=True)[:8]
        sample_titles = list(set(data["titles"]))[:10]
        industry_summary[ind_name] = {
            "total": data["count"],
            "domestic": data["domestic"],
            "international": data["international"],
            "avg_salary": avg_sal,
            "top_skills": [{"id": s, "count": c} for s, c in top_skills],
            "sample_titles": sample_titles,
            "unique_companies": len(data["companies"]),
        }

    def avg_salary(job_list):
        sals = [(j.salary_min + j.salary_max) // 2 for j in job_list if j.salary_min and j.salary_max]
        return int(sum(sals) / len(sals)) if sals else 0

    return {
        "total_jobs": len(jobs),
        "domestic_total": len(domestic),
        "international_total": len(international),
        "domestic_avg_salary": avg_salary(domestic),
        "international_avg_salary": avg_salary(international),
        "industries": industry_summary,
        "top_skills_global": [
            {"name": s.canonical_name, "id": s.id, "total": s.total_count,
             "domestic": s.domestic_count, "international": s.international_count}
            for s in skills[:25]
        ],
    }


async def generate_report(stats: dict) -> dict:
    """Generate the full narrative report in sections."""
    stats_json = json.dumps(stats, ensure_ascii=False, indent=2)

    report = {}

    # Section 1: 全景概览
    logger.info("Generating section 1: overview...")
    report["overview"] = gemini_call(f"""
基于以下 AI 岗位市场全量数据，写一篇"AI 岗位市场全景概览"（400-500字）。

要求：
- 开篇用一个引人注目的发现抓住读者
- 分析 AI 岗位在各行业的渗透现状（不只是互联网！）
- 指出国内外市场的核心差异
- 给出一个整体判断：AI 岗位的格局正在怎样变化
- 让一个非技术读者也能看懂

数据：
{stats_json}
""")
    await asyncio.sleep(3)

    # Section 2: 行业深度分析
    logger.info("Generating section 2: industry deep-dives...")
    industries_text = json.dumps(stats["industries"], ensure_ascii=False, indent=2)
    report["industry_deep_dive"] = gemini_call(f"""
基于以下各行业 AI 岗位数据，为每个重点行业（岗位数 >= 10 的行业）写一段深度分析（每个行业 150-200 字）。

每个行业需要包含：
1. 这个行业为什么需要 AI？解决什么痛点？
2. 典型岗位长什么样？（引用 sample_titles 中的真实职位名）
3. 需要什么技能组合？和纯互联网 AI 岗位有什么不同？
4. 入门门槛如何？适合什么背景的人？
5. 薪资水平和发展前景

行业数据：
{industries_text}
""")
    await asyncio.sleep(3)

    # Section 3: 跨界求职指南
    logger.info("Generating section 3: career transition guide...")
    report["career_guide"] = gemini_call(f"""
基于以下 AI 岗位市场数据，写一份"跨界求职指南"（500-600字），面向以下 4 类人群：

1. **金融从业者**想转 AI：该怎么切入？
2. **医疗/生物背景**想做 AI：有什么独特优势？
3. **产品经理/运营**想转 AI 方向：不会写代码怎么办？
4. **应届毕业生**想进入 AI + 传统行业：该选什么赛道？

每类人群写 120-150 字，要具体、可执行、有温度。引用数据中的真实岗位和技能需求。

数据摘要：
- 行业分布：{json.dumps({k: v["total"] for k, v in stats["industries"].items()}, ensure_ascii=False)}
- 各行业平均薪资：{json.dumps({k: v["avg_salary"] for k, v in stats["industries"].items()}, ensure_ascii=False)}
- 全局 Top 10 技能：{json.dumps([s["name"] for s in stats["top_skills_global"][:10]], ensure_ascii=False)}
""")
    await asyncio.sleep(3)

    # Section 4: 趋势判断
    logger.info("Generating section 4: trend analysis...")
    report["trends"] = gemini_call(f"""
基于以下数据，写一篇"AI 岗位趋势判断"（300-400字）。

需要回答：
1. 哪些行业的 AI 需求正在**爆发**？为什么？
2. 哪些行业的 AI 需求可能**被高估**？
3. 未来 1-2 年，什么样的人才最稀缺？
4. 给求职者的一句话建议

注意：要有观点，要敢下判断，不要面面俱到。数据支撑你的观点。

数据：
- 总岗位数 {stats["total_jobs"]}，国内 {stats["domestic_total"]}，国际 {stats["international_total"]}
- 行业分布：{json.dumps({k: v["total"] for k, v in stats["industries"].items()}, ensure_ascii=False)}
- 国内平均月薪 ¥{stats["domestic_avg_salary"]}，国际 ¥{stats["international_avg_salary"]}
""")

    # Section 5: 核心发现 (bullet points)
    logger.info("Generating section 5: key findings...")
    report["key_findings"] = gemini_call(f"""
基于以下数据，提炼 8-10 条最有价值的核心发现，每条一句话（30-50字）。

要求：
- 每条发现要让人"哇，原来是这样"
- 数据驱动，不说空话
- 涵盖行业、技能、薪资、国内外差异多个维度

数据：
{stats_json}
""")

    return report


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_session() as db:
        # Re-normalize first
        from app.services.skill_extractor import normalize_all_jobs
        norm_result = await normalize_all_jobs(db)
        logger.info("Normalized: %s", norm_result)

        stats = await collect_full_stats(db)
        logger.info(
            "Stats: %d jobs, %d industries, %d skills",
            stats["total_jobs"], len(stats["industries"]), len(stats["top_skills_global"]),
        )

        report = await generate_report(stats)

        # Save report
        (OUTPUT_DIR / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Written report.json")

        # Also save raw stats for potential frontend use
        (OUTPUT_DIR / "full-stats.json").write_text(
            json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Written full-stats.json")

    logger.info("Report generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
