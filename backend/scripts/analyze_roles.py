#!/usr/bin/env python3
"""Cluster jobs by role type and produce per-role skill profiles.

Groups jobs into role archetypes via keyword matching on title,
then computes detailed profiles: required vs preferred skills,
experience range, salary range, education, top companies.

Usage:
    cd backend && .venv/bin/python scripts/analyze_roles.py
"""
import asyncio
import json
import re
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.job import Job
from app.services.skill_extractor import extractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "data"

# ── Role classification rules ──────────────────────────────────────
# Each rule: (role_id, display_name_cn, display_name_en, title_regex_pattern)
# Order matters — first match wins.

DOMESTIC_ROLES = [
    # ── 排除非 AI 岗位噪声 ──
    ("_noise", "非AI岗位",
     re.compile(r"^(会计|行政|HR|办公室文员|法务|财务|前台|出纳|审计)$|"
                r"^(SSC|共享服务|内控管理专家)$", re.I)),
    # ── AI 技术岗 ──
    ("ai_engineer", "AI/LLM 工程师",
     re.compile(r"AI.*工程师|LLM.*Engineer|AI Engineer|AI.*开发|Agent.*工程|AIGC.*开发|大模型.*工程|"
                r"AI 全栈|AI全栈|LLM Engineer|AI Senior Engineer|AI应用|Manager, AI Engineer|"
                r"Senior AI|AI Software|人工智能.*工程|AI Agent.*Engineer|AI Agent.*Developer|"
                r"Agent.*Developer|LLM.*Expert|LLM.*Application|AI.*Architect|"
                r"智能体.*研发|智能体.*构建|AI Agent|开发岗.*智能体|AI座舱应用|"
                r"AI 技术经理|AI.*全栈|AIGC.*设计", re.I)),
    ("algorithm", "算法工程师/研究员",
     re.compile(r"算法|Algorithm|NLP|CV|机器学习|深度学习|推荐.*算法|搜索.*算法|"
                r"多模态.*算法|模型.*策略|量化.*研究|Applied Scientist|Scientist|Research|"
                r"Machine Learning|ML Engineer|工业AI算法|AI Drug Discovery", re.I)),
    ("product_manager", "AI 产品经理",
     re.compile(r"产品经理|Product Manager|产品专家|产品.*解决方案|AIGC产品|"
                r"产品负责人|Product Owner|产品总监|Product.*Digital|产品策划", re.I)),
    ("operations", "AI 运营/训练师",
     re.compile(r"运营|训练师|标注|Prompt|内容.*策略|AIGC.*运营|"
                r"Content Push|MarTech|营销.*技术", re.I)),
    ("autonomous", "自动驾驶/智能座舱",
     re.compile(r"自动驾驶|智能座舱|Autonomous|自动化测试.*驾驶|ADS|ADAS", re.I)),
    ("smart_manufacturing", "智能制造/工业AI",
     re.compile(r"智能制造|工业.*智能|产线|MES|工业AI|制造.*工程|机器人.*产线|"
                r"工业软件", re.I)),
    ("data", "数据分析/数据科学",
     re.compile(r"数据.*分析|数据.*科学|Data.*Analyst|Data.*Scientist|BI|"
                r"数据.*工程|统计.*编程|数据.*挖掘|投资分析|量化投资|量化交易", re.I)),
    ("sales_bd", "AI 销售/商务",
     re.compile(r"销售|Sales|商务|BD|客户.*成功|解决方案.*销售|Customer Acquisition", re.I)),
    ("ai_transformation", "AI 转型/咨询",
     re.compile(r"AIT|AI业务改造|AI转型|数字化转型|AI.*顾问|AI.*咨询|"
                r"企业AI|咨询.*经理|AI交付|AI.*PMO|AI.*项目管理|流程.*建构", re.I)),
    ("leadership", "AI 管理/战略",
     re.compile(r"总监|Director|VP|负责人|CTO|CEO|Head of|战略|"
                r"合伙人|总经理|联合创始", re.I)),
    ("medical_ai", "医疗AI专岗",
     re.compile(r"医疗AI|临床|药物|医学|Health.*AI|理赔", re.I)),
    ("customer_service", "智能客服",
     re.compile(r"智能客服|客服.*产品|客服.*运营|AI客服", re.I)),
    ("education_ai", "AI 教育",
     re.compile(r"教育.*人工智能|AI.*教育|智能教育|AI教育", re.I)),
    ("risk_compliance", "AI 风控/合规",
     re.compile(r"风控|内控|合规|Risk|Compliance", re.I)),
]

INTERNATIONAL_ROLES = [
    # ── 排除非 AI 岗位噪声 ──
    ("_noise", "Non-AI Noise",
     re.compile(r"Probability Tutor|Building Maintenance|Civil Engineer|"
                r"Scheduling Engineer|Security.*(?!AI)|Technician$|"
                r"Account Executive|Venture.*Analyst$", re.I)),
    # ── AI 技术岗 ──
    ("ml_scientist", "ML Scientist / Researcher",
     re.compile(r"Scientist|Researcher|Research", re.I)),
    ("ml_engineer", "ML/AI Engineer",
     re.compile(r"Machine Learning.*Engineer|ML.*Engineer|AI.*Engineer|"
                r"AI/ML|ML Specialist|Python AI|AI Software|AI-ML|"
                r"MLE[,\s]|Sr\. MLE", re.I)),
    ("sde", "Software Engineer",
     re.compile(r"Software.*Engineer|Software.*Dev|Full Stack|Backend|Frontend|"
                r"SDE|SWE|Developer|Engineer I |Engineer –", re.I)),
    ("product_manager", "Product Manager",
     re.compile(r"Product Manager|Product Owner|Product Lead|Product Operations", re.I)),
    ("data", "Data Scientist / Analyst",
     re.compile(r"Data Scientist|Data Analyst|Data Engineer|Analytics|"
                r"Data.*Acquisition|Data & AI", re.I)),
    ("architect", "Solutions Architect",
     re.compile(r"Architect|Solutions|Customer Engineer", re.I)),
    ("autonomous", "Autonomous Vehicles",
     re.compile(r"Autonomous|Self.Driving|AV |Robotics", re.I)),
    ("sales_bd", "AI Sales / BD",
     re.compile(r"Sales.*Leader|Sales.*Manager|Partner.*Lead|Partner.*Development|"
                r"Enablement|ProServe|AI Sales|Data.*Sales", re.I)),
    ("leadership", "Engineering Leadership",
     re.compile(r"Director|VP|CTO|CEO|CAIO|Head of|Manager.*Engineer|Engineering Manager|"
                r"Lead.*Engineer|Principal|Senior.*Manager|Co-Founder|"
                r"Digital Transformation|Professor", re.I)),
    ("intern_newgrad", "Intern / New Grad",
     re.compile(r"Intern|New Grad|Entry Level|Junior|Recent Grad|Accelerator|Summer 202|"
                r"0-2 Years", re.I)),
    ("finance_ops", "Finance / Operations",
     re.compile(r"Finance Manager|Payment.*Network|Risk Analyst|Consultant|"
                r"Design Technolog", re.I)),
]


def classify_job(title: str, rules: list) -> str:
    if not title:
        return "other"
    for role_id, _, pattern in rules:
        if pattern.search(title):
            return role_id
    return "other"


def build_role_profile(jobs: list[Job]) -> dict:
    """Build a detailed profile for a group of jobs."""
    required_skills: Counter = Counter()
    preferred_skills: Counter = Counter()
    salaries = []
    experience_mins = []
    experience_maxs = []
    educations: Counter = Counter()
    companies: Counter = Counter()
    work_modes: Counter = Counter()
    sample_titles: list[str] = []
    industries: Counter = Counter()

    seen_titles = set()
    for j in jobs:
        # Skills — normalize
        for raw in (j.required_skills or []):
            sid = extractor.normalize(raw)
            if sid:
                required_skills[sid] += 1
        for raw in (j.preferred_skills or []):
            sid = extractor.normalize(raw)
            if sid:
                preferred_skills[sid] += 1

        sal_mid = j.salary_mid_cny_monthly
        if sal_mid is not None:
            salaries.append(sal_mid)

        if j.experience_min is not None:
            experience_mins.append(j.experience_min)
        if j.experience_max is not None:
            experience_maxs.append(j.experience_max)

        educations[j.education or "unspecified"] += 1
        work_modes[j.work_mode or "unknown"] += 1

        if j.company_name:
            companies[j.company_name] += 1
        if j.industry:
            industries[j.industry] += 1

        if j.title and j.title not in seen_titles:
            seen_titles.add(j.title)
            if len(sample_titles) < 8:
                sample_titles.append(j.title)

    # Remove preferred skills that are also in required (show only the delta)
    preferred_only = Counter()
    for sid, cnt in preferred_skills.items():
        if sid not in required_skills:
            preferred_only[sid] = cnt

    profile = {
        "job_count": len(jobs),
        "sample_titles": sample_titles,
        "required_skills": [
            {"skill_id": s, "count": c}
            for s, c in required_skills.most_common(10)
        ],
        "preferred_skills": [
            {"skill_id": s, "count": c}
            for s, c in preferred_only.most_common(10)
        ],
        "salary": None,
        "experience": None,
        "education": dict(educations.most_common()),
        "work_mode": dict(work_modes.most_common()),
        "top_companies": [name for name, _ in companies.most_common(5)],
        "top_industries": [
            {"industry": ind, "count": cnt}
            for ind, cnt in industries.most_common(5)
        ],
    }

    if salaries:
        salaries.sort()
        profile["salary"] = {
            "min": salaries[0],
            "max": salaries[-1],
            "median": int(median(salaries)),
            "avg": int(sum(salaries) / len(salaries)),
            "p25": salaries[len(salaries) // 4],
            "p75": salaries[len(salaries) * 3 // 4],
            "sample_size": len(salaries),
        }

    if experience_mins:
        profile["experience"] = {
            "min_range": [min(experience_mins), max(experience_mins)],
            "median_min": int(median(experience_mins)),
            "avg_min": round(sum(experience_mins) / len(experience_mins), 1),
            "sample_size": len(experience_mins),
        }

    return profile


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_session() as db:
        result = await db.execute(
            select(Job).where(Job.parse_status == "parsed", Job.title.isnot(None))
        )
        all_jobs = result.scalars().all()
        logger.info("Total parsed jobs with title: %d", len(all_jobs))

        for market, rules in [("domestic", DOMESTIC_ROLES), ("international", INTERNATIONAL_ROLES)]:
            market_jobs = [j for j in all_jobs if j.market == market]
            logger.info("\n%s: %d jobs", market.upper(), len(market_jobs))

            # Classify
            role_groups: dict[str, list] = defaultdict(list)
            for j in market_jobs:
                role_id = classify_job(j.title, rules)
                role_groups[role_id].append(j)

            # Build role name mapping
            role_names = {r_id: name for r_id, name, _ in rules}
            role_names["other"] = "其他" if market == "domestic" else "Other"

            # Print classification summary
            for role_id, jobs in sorted(role_groups.items(), key=lambda x: -len(x[1])):
                name = role_names.get(role_id, role_id)
                logger.info("  %-30s %4d jobs", name, len(jobs))

            # Build profiles (skip noise and tiny groups)
            profiles = []
            for role_id, jobs in sorted(role_groups.items(), key=lambda x: -len(x[1])):
                if role_id == "_noise" or len(jobs) < 3:
                    continue
                profile = build_role_profile(jobs)
                profile["role_id"] = role_id
                profile["role_name"] = role_names.get(role_id, role_id)
                profiles.append(profile)

            # Write output
            filename = f"roles-{market}.json"
            path = OUTPUT_DIR / filename
            path.write_text(
                json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            logger.info("Written %s (%d roles)", filename, len(profiles))

    logger.info("\nRole analysis complete!")


if __name__ == "__main__":
    asyncio.run(main())
