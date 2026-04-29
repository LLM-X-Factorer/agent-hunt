#!/usr/bin/env python3
"""Rule-based backfill of jobs.role_type for entries that escaped the LLM pipeline.

Why we need this: ~2,500 parsed jobs (mostly community_github_hiring +
community_hn_wih + a few vendor crawls) shipped with role_type=NULL because
the LLM run hit OpenRouter quota during ingest. The narrative pages care
about labeled-jobs fraction, so we want to label these without burning
$5+ of LLM tokens.

The rule set is deliberately conservative — when the title alone is
unambiguous, label it; when it's ambiguous, leave NULL so the LLM can
re-process later if budget allows. False positives are worse than nulls
here because role_type drives the entire narrative.

Usage:
    cd backend && .venv/bin/python scripts/backfill_role_type_rules.py --dry-run
    cd backend && .venv/bin/python scripts/backfill_role_type_rules.py --apply
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, update

from app.database import async_session
from app.models.job import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Title patterns — order matters: NULL_TITLE first (kills support-roles),
# then AI_NATIVE (positive signal), then AI_AUGMENTED (composite).
# ---------------------------------------------------------------------------

# Support / non-AI roles: these never count as ai_native even at AI-native
# companies (HRBP at OpenAI is still HR, not AI engineering).
NULL_TITLE_RE = re.compile(
    # English support roles
    r"\b(hrbp|hris|hr |hr,|payroll|recruiter|recruiting|talent acquisition|"
    r"talent partner|"
    r"chief financial|cfo|cmo|coo|treasurer|accountant|accounting|"
    r"office manager|admin|administrative|receptionist|"
    r"legal counsel|paralegal|"
    r"facilities|janitor|security guard|"
    r"content writer|content marketing|seo specialist|copywriter|"
    r"social media manager|community manager|brand manager|"
    r"business development|overseas sales|"
    r"sales (manager|director|specialist|representative|engineer|associate)|"
    r"account (manager|executive|director)|"
    r"investor relations|public relations|"
    r"marketing manager|marketing specialist|"
    r"customer success manager|"
    r"graphic designer|visual designer|ui designer|ux designer|"
    r"product designer|designer$"
    r")\b"
    # Chinese support roles — note: \b doesn't work between Chinese chars,
    # so use either start/end anchors or contains-style match.
    r"|(?:^|[^a-zA-Z一-鿿])(?:"
    r"hrbp|hr实习生|hr 实习生|hris|"
    r"行政|前台|出纳|招聘|人事|财务|法务|会计|审计|秘书|内勤|"
    r"销售|海外销售|渠道运营|渠道|商务经理|国际销售|生态销售|"
    r"业务拓展|投资部|投资者关系|公关|品牌|营销|"
    r"内容运营|内容审核|创意策划|"
    r"投放|广告|seo|kol|达人|直播|"
    r"采购|物流|供应链|内控|总账|薪酬|"
    r"司机|保洁|保安|秘书|助理|助理实习生|"
    r"客户投诉|客服专员|客户经理|"
    r"项目经理|交付项目经理|"
    r"高校合作|校园大使|"
    r"ui设计|ux设计|视觉设计|平面设计|品牌设计|"
    r"市场实习生|市场与内容|公共事务|公关专家"
    r")(?=$|[^a-zA-Z一-鿿])"
    # Plain Chinese title-anchored support roles
    r"|^(?:行政|前台|出纳|招聘|人事|财务|法务|会计|审计|秘书|内勤|"
    r"hr|hrbp|hrm|司机|保洁|保安|客服专员)",
    re.IGNORECASE,
)

# AI-native strong signals — these titles are unambiguously about AI as the
# primary subject of the role.
AI_NATIVE_TITLE_RE = re.compile(
    r"\b("
    # English ML/AI engineering
    r"machine learning|deep learning|computer vision|"
    r"\bml\b|\bllm\b|large language model|generative ai|gen ?ai|"
    r"\bnlp\b|natural language processing|"
    r"reinforcement learning|recommender|recsys|"
    r"research scientist|research engineer|applied scientist|"
    r"applied ai|applied ml|applied research|"
    r"data scientist|data science|"
    r"\bai engineer|ai/ml|ai researcher|ai scientist|"
    r"ai engineering|ai team|ai product|ai platform|"
    r"prompt engineer|forward deployed|solutions engineer|"
    r"robotics engineer|autonomous|self.driving|"
    r"speech (recognition|synthesis)|"
    r"perception engineer|sensor fusion|slam engineer|"
    r"foundation model|model training|model inference|"
    r"\bmlops|ml infrastructure|ml platform|"
    r"chief ai officer|head of ai|head of ml|"
    # Chinese
    r"算法|大模型|机器学习|深度学习|"
    r"人工智能.*工程师|"
    r"ai 工程师|ai工程师|"
    r"ai 应用|ai应用|ai 产品|ai产品|ai 解决方案|ai解决方案|"
    r"ai 销售|ai销售|ai 商务|ai商务|"
    r"aigc|生成式 ai|生成式ai|"
    r"计算机视觉|自然语言处理|强化学习|"
    r"搜索推荐|推荐算法|风控算法|策略算法|"
    r"多模态|具身智能|"
    r"\bagent\b|prompt 工程"
    r")",
    re.IGNORECASE,
)

# AI-augmented_traditional: traditional profession + AI skills required.
# Conservative — only fires on titles that explicitly compose two domains.
AI_AUGMENTED_TITLE_RE = re.compile(
    r"\b("
    r"quantitative (researcher|analyst|developer)|quant (researcher|developer)|"
    r"medical imaging.*ai|medical.*deep learning|"
    r"drug discovery.*ai|computational biology.*ml|bioinformatics.*ml|"
    r"electrical engineer.*ai|mechanical engineer.*ml|"
    r"trading (engineer|developer).*(ml|ai)"
    r")"
    r"|("
    # Chinese: 「专业 + AI/ML/深度学习」组合
    r"医疗.{0,4}(ai|算法|深度学习)|"
    r"医疗影像|临床.{0,4}(ai|算法)|"
    r"工业.{0,4}(ai|算法)|智能制造|"
    r"工艺.{0,4}(ai|算法|深度学习)|"
    r"金融.{0,4}(算法|风控|量化)|"
    r"量化.{0,4}(研究|开发|策略)|"
    r"风控.{0,4}(建模|策略|算法)|"
    r"教育.{0,4}(ai|算法)|"
    r"汽车.{0,4}(ai|算法|自动驾驶)"
    r")",
    re.IGNORECASE,
)

# Companies that are AI-native by definition — generic SDE/PM titles at
# these get bumped to ai_native (a "Software Engineer Intern" at OpenAI
# is still working on AI products).
AI_NATIVE_COMPANIES = {
    "openai", "anthropic", "xai", "cohere", "deepmind",
    "mistral", "ai21", "stability ai", "stability.ai",
    "midjourney", "runway", "perplexity", "character.ai",
    "inflection ai", "scale ai", "huggingface", "hugging face",
    "groq", "together ai", "fireworks ai", "modal labs",
    "智谱ai", "智谱", "moonshot", "月之暗面", "百川", "baichuan",
    "minimax", "stepfun", "阶跃星辰", "01.ai", "零一万物",
    "deepseek",
}


# Vendor platforms that already curate AI-native job listings — anything
# at these vendors is an AI company, the only question is whether the title
# describes an AI/product role or a support function.
AI_NATIVE_VENDOR_PLATFORMS = {
    "vendor_openai", "vendor_anthropic", "vendor_xai", "vendor_cohere",
    "vendor_deepmind", "vendor_zhipuai", "vendor_minimax", "vendor_moonshot",
    "vendor_baichuan",
}

# GitHub hiring repos pre-filter to AI/ML/Data categories at ingest time —
# remaining NULL after first-pass rule are AI-relevant by construction.
GITHUB_HIRING_PLATFORM = "community_github_hiring"

# Vendor-internal AI product / engineering signals — when these show up in
# titles at AI-native vendors, mark ai_native (covers MaaS / GLM / 推理 / 训练 etc.).
AI_VENDOR_PRODUCT_RE = re.compile(
    r"\b(maas|glm|deepseek|llama)\b|"
    r"(大模型|推理|训练|算法|强化学习|后训练|预训练|基座模型|"
    r"solutions architect|solution architect|解决方案|架构师|"
    r"infra|sre|运维|训练框架|推理框架|"
    r"ai native|ai\-native|api销售|api 销售|"
    r"开发者|developer relations|生态|eco system|ecosystem)",
    re.IGNORECASE,
)

# Non-AI engineering domains that sometimes leak through GitHub hiring's
# "AI/ML/Data" category — pure mechanical / civil / geological / aerospace
# work without ML, mark NULL.
NON_AI_ENGINEERING_RE = re.compile(
    r"\b("
    r"gis intern|geographic information systems|geological|geophysics|"
    r"nuclear (analysis|engineering|technician|operations)|"
    r"mechanical engineer|civil engineer|structural engineer|"
    r"chemical engineer|petroleum engineer|materials engineer|"
    r"aerospace engineer|aeronautical|"
    r"welding|surveyor|construction|"
    r"engine controls|gas integrity|pipeline|"
    r"electrical engineering tech|nuclear physics|"
    r"protein analytics|laboratory technician"
    r")\b",
    re.IGNORECASE,
)

# Bioinformatics / computational biology — these are ai_augmented_traditional
# (biology background + ML tools).
BIO_AUGMENTED_RE = re.compile(
    r"\b(bioinformatics|computational biology|drug discovery|genomics .*ml)\b",
    re.IGNORECASE,
)


def is_ai_native_company(company: str | None) -> bool:
    if not company:
        return False
    c = company.lower().strip()
    return any(c == name or c.startswith(name + " ") or name in c for name in AI_NATIVE_COMPANIES)


def classify(
    title: str | None,
    company: str | None,
    platform_id: str | None = None,
) -> str | None:
    """Return ai_native / ai_augmented_traditional / None.

    Order: explicit support-role kill → ai_native title → ai_augmented (skipped
    for AI-native companies, where 「量化」 means model quantization, not finance)
    → ai_native company override → leave NULL.
    """
    if not title:
        return None

    t = title.strip()
    if NULL_TITLE_RE.search(t):
        return None

    ai_native_co = is_ai_native_company(company) or platform_id in AI_NATIVE_VENDOR_PLATFORMS

    # Bio + ML composite (always wins over native — even at AI companies it's
    # really a biology role with ML).
    if BIO_AUGMENTED_RE.search(t):
        return "ai_augmented_traditional"

    if AI_NATIVE_TITLE_RE.search(t):
        return "ai_native"

    # Augmented rule must not fire at AI-native companies — the regex's
    # 「量化 / 风控」 trigger words mean different things at OpenAI vs a bank.
    if not ai_native_co and AI_AUGMENTED_TITLE_RE.search(t):
        return "ai_augmented_traditional"

    # Vendor-internal AI product / infra signals at AI-native vendors.
    if ai_native_co and AI_VENDOR_PRODUCT_RE.search(t):
        return "ai_native"

    # Generic technical title at AI-native company → ai_native. Anyone shipping
    # at OpenAI / 智谱 etc. is contributing to the AI product whether they're
    # called "iOS Engineer" or "DBA". Note: no \b before Chinese tokens since
    # word-boundary doesn't fire between CJK chars.
    if ai_native_co and (
        re.search(
            r"\b(software engineer|backend|frontend|full.?stack|"
            r"systems engineer|infrastructure|platform|product manager|"
            r"ios engineer|android engineer|web engineer|mobile engineer|"
            r"dba|sre|devops|security engineer|network engineer|"
            r"qa engineer|test engineer|data engineer|database engineer|"
            r"research engineer|reliability engineer|"
            r"graduate engineer|engineering manager|principal engineer|staff engineer|"
            r"architect)\b", t, re.IGNORECASE,
        )
        or re.search(
            r"(产品经理|工程师|开发|研发|架构师|"
            r"测试开发|数据开发|数据研发|数据分析师|数据专家|"
            r"系统研发|应用研发|平台研发|基础设施|"
            r"网络架构|服务器|网络|安全|风控|通信|"
            r"前端|后端|全栈|爬虫|"
            r"医疗|医学|"
            r"产品研究员|产品实习生|技术内容|"
            r"运营专家|平台运营|产品运营|"
            r"aminer|kimi|glm|maas|"
            r"科技平台|科研平台|"
            r"技术支持|海外技术)", t, re.IGNORECASE,
        )
    ):
        return "ai_native"

    # GitHub hiring is pre-filtered to AI/ML/Data at ingest — anything left
    # NULL but without a clear non-AI engineering signal should be ai_native.
    # If the title carries an explicit AI keyword (even fused with a non-AI
    # domain like "AI in Nuclear Physics"), the AI side wins.
    if platform_id == GITHUB_HIRING_PLATFORM:
        if re.search(r"\b(ai|ml|llm|aiml)\b", t, re.IGNORECASE):
            return "ai_native"
        if NON_AI_ENGINEERING_RE.search(t):
            return None
        return "ai_native"

    return None


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="actually UPDATE rows; otherwise dry-run only")
    args = parser.parse_args()

    async with async_session() as db:
        rows = (await db.execute(
            select(Job).where(
                Job.parse_status == "parsed",
                Job.role_type.is_(None),
                Job.title.isnot(None),
            )
        )).scalars().all()

    logger.info("loaded %d parsed jobs missing role_type", len(rows))

    predictions: dict[str, str | None] = {}
    counter: Counter = Counter()
    by_platform: dict[str, Counter] = {}

    for j in rows:
        rt = classify(j.title, j.company_name, j.platform_id)
        predictions[str(j.id)] = rt
        counter[rt] += 1
        by_platform.setdefault(j.platform_id, Counter())[rt] += 1

    logger.info("=== overall prediction distribution ===")
    for k, v in counter.most_common():
        logger.info("  %-30s %d", str(k), v)

    logger.info("=== per-platform distribution ===")
    for plat, ctr in sorted(by_platform.items(), key=lambda kv: -sum(kv[1].values())):
        total = sum(ctr.values())
        nat = ctr.get("ai_native", 0)
        aug = ctr.get("ai_augmented_traditional", 0)
        nul = ctr.get(None, 0)
        logger.info(
            "  %-30s total=%4d  ai_native=%4d  augmented=%3d  null=%4d",
            plat, total, nat, aug, nul,
        )

    if not args.apply:
        # Dry-run: dump 30 samples per predicted bucket so a human can sanity
        # check before flipping the switch.
        logger.info("\n=== sample predictions (60 random) ===")
        bucket_samples: dict[str | None, list] = {"ai_native": [], "ai_augmented_traditional": [], None: []}
        for j in rows:
            rt = predictions[str(j.id)]
            if len(bucket_samples[rt]) < 20:
                bucket_samples[rt].append(j)
        for bucket, samples in bucket_samples.items():
            logger.info("\n  -- predicted %s --", str(bucket))
            for j in samples:
                logger.info(
                    "    [%s] %s | %s",
                    j.platform_id,
                    (j.company_name or "-")[:25],
                    (j.title or "-")[:80],
                )
        logger.info("\nDry-run only. Re-run with --apply to write to DB.")
        return

    # Apply: only UPDATE rows where prediction is non-null. Keep rows we
    # couldn't classify as NULL so a future LLM run picks them up.
    confident = [(jid, rt) for jid, rt in predictions.items() if rt is not None]
    logger.info("applying %d updates (skipping %d uncertain)",
                len(confident), len(predictions) - len(confident))

    async with async_session() as db:
        for jid, rt in confident:
            await db.execute(
                update(Job).where(Job.id == jid).values(role_type=rt)
            )
        await db.commit()

    logger.info("done.")


if __name__ == "__main__":
    asyncio.run(main())
