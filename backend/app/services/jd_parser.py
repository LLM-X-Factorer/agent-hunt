# JD structured parsing via OpenRouter (OpenAI-compatible) — bilingual zh/en.
# Default model: z-ai/glm-5.1. Switchable via AH_LLM_MODEL.
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.schemas.job import ParsedJD
from app.services.llm import llm_json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
你是一个专业的 JD（职位描述）结构化解析引擎。
你的任务是将原始 JD 文本解析为标准化的 JSON 格式。

关键规则：
1. 技能名称统一使用英文标准名（例：大模型 → LLM，朗链 → LangChain，通义千问 → Qwen）
2. 薪资统一转换为人民币月薪（如遇美元年薪，按 7.25 汇率 /12 换算；欧元按 7.90/12）
3. 如果信息缺失，对应字段填 null，不要猜测
4. required_skills 只包含 JD 明确要求的技能
5. preferred_skills 包含"加分项"、"优先"、"nice to have"的技能
6. market 根据公司所在地和语言判断：中国大陆公司为 "domestic"，其他为 "international"
7. company_size: "startup"(< 50 人), "mid"(50-500), "large"(500-5000), "enterprise"(> 5000)
8. industry: 根据公司业务和岗位内容判断所属行业，必须从以下选项中选择：
   "internet"(互联网/SaaS/软件), "finance"(金融/银行/保险), "healthcare"(医疗/生物/制药),
   "manufacturing"(制造/工业/硬件), "retail"(零售/电商), "education"(教育/培训),
   "media"(媒体/内容/游戏), "consulting"(咨询/企业服务), "automotive"(汽车/自动驾驶),
   "energy"(能源/环保), "telecom"(通信/运营商), "government"(政府/公共事业), "other"
9. experience_requirement: 根据"经验要求"分桶，必须从以下选择：
   "fresh"(应届/在校/0 经验), "0-1y"(0-1 年), "1-3y", "3-5y", "5y+"
10. internship_friendly: 是否接受实习生 / 在校生（true/false/null）
11. is_campus: 是否明确标注"校招"/"校园招聘"/"应届生招聘"（true/false/null）
12. role_type: 岗位是 AI 原生还是 AI 增强型传统岗位
    - "ai_native": 算法/ML/LLM 工程师、AI 产品、AI Agent 开发、AI 销售等以 AI 为主体的岗位
    - "ai_augmented_traditional": 主体是传统专业（电气/医疗/金融/制造/会计...）但要求 AI 技能。例如「电气工程师 + 深度学习」「医疗影像分析师」「智能制造工艺工程师」「量化研究员」
13. base_profession: 仅当 role_type = "ai_augmented_traditional" 时填写传统岗位名（如"电气工程师"、"医生"、"会计"、"金融分析师"、"机械工程师"）；ai_native 时填 null

严格输出以下 JSON，不要添加任何额外文字：
{
  "title": "string | null",
  "company_name": "string | null",
  "company_size": "startup | mid | large | enterprise | null",
  "location": "string | null",
  "market": "domestic | international",
  "industry": "internet | finance | healthcare | manufacturing | retail | education | media | consulting | automotive | energy | telecom | government | other | null",
  "work_mode": "onsite | remote | hybrid | null",
  "salary_min_rmb": "int | null",
  "salary_max_rmb": "int | null",
  "salary_currency_original": "CNY | USD | EUR | null",
  "experience_min_years": "int | null",
  "experience_max_years": "int | null",
  "education": "bachelor | master | phd | any | null",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "responsibilities": ["string"],
  "language": "zh | en | mixed",
  "experience_requirement": "fresh | 0-1y | 1-3y | 3-5y | 5y+ | null",
  "internship_friendly": "bool | null",
  "is_campus": "bool | null",
  "role_type": "ai_native | ai_augmented_traditional | null",
  "base_profession": "string | null"
}"""


async def parse_jd(raw_content: str) -> ParsedJD:
    """Parse a single raw JD text into structured fields."""
    data = await llm_json(raw_content, system=SYSTEM_PROMPT, temperature=0.1)
    return ParsedJD(**data)


async def parse_job_by_id(db: AsyncSession, job_id) -> Job:
    """Load a job from DB, parse its raw_content, and save structured fields."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one()

    try:
        parsed = await parse_jd(job.raw_content)

        job.title = parsed.title
        job.company_name = parsed.company_name
        job.company_size = parsed.company_size
        job.location = parsed.location
        job.market = parsed.market
        job.industry = parsed.industry
        job.work_mode = parsed.work_mode
        job.salary_min = parsed.salary_min_rmb
        job.salary_max = parsed.salary_max_rmb
        job.salary_currency = parsed.salary_currency_original
        job.experience_min = parsed.experience_min_years
        job.experience_max = parsed.experience_max_years
        job.education = parsed.education
        job.required_skills = parsed.required_skills
        job.preferred_skills = parsed.preferred_skills
        job.responsibilities = parsed.responsibilities
        job.language = parsed.language
        job.experience_requirement = parsed.experience_requirement
        job.internship_friendly = parsed.internship_friendly
        job.is_campus = parsed.is_campus
        job.role_type = parsed.role_type
        job.base_profession = parsed.base_profession
        job.parse_status = "parsed"

        from datetime import datetime, timezone
        job.parsed_at = datetime.now(timezone.utc)

    except Exception:
        logger.exception("Failed to parse job %s", job_id)
        job.parse_status = "failed"

    await db.commit()
    await db.refresh(job)
    return job
