#!/usr/bin/env python3
"""Pull AI-relevant interview-experience posts from 牛客 (#14).

Pipeline:
  1. fetch sitemap1.xml — every public post URL is in there
  2. take the most recent N URLs (sitemap is roughly chronological)
  3. concurrent HTTPS GET each, extract __INITIAL_STATE__
  4. filter by title keywords (AI / 算法 / LLM / ML / 产品经理 / 校招 / 秋招 / 春招 / 实习)
  5. LLM-parse hits to ApplicantProfile fields, upsert into DB

Subsequent runs are idempotent (UPSERT on (source, source_record_id)).

Usage:
    cd backend && .venv/bin/python scripts/collect_nowcoder_posts.py
    cd backend && .venv/bin/python scripts/collect_nowcoder_posts.py --max-urls 500 --concurrency 10
"""
from __future__ import annotations

import argparse
import asyncio
import datetime
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from sqlalchemy.dialects.postgresql import insert

from app.database import async_session
from app.models.applicant_profile import ApplicantProfile
from app.services.llm import llm_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
SITEMAP_URL = "https://www.nowcoder.com/sitemap1.xml"
SITEMAP_LOC_RE = re.compile(r"<loc>([^<]+/discuss/\d+)[^<]*</loc>")
INITIAL_STATE_RE = re.compile(
    r"window\.__INITIAL_STATE__=(\{.+?\});\(function", re.DOTALL
)
HTML_TAG_RE = re.compile(r"<[^>]+>")

# Title keywords that strongly suggest an interview / offer / campus post
# relevant to aijobfit's roles. Skip everything else.
RELEVANT_TITLE_RE = re.compile(
    r"AI|LLM|ML|算法|机器学习|深度学习|大模型|多模态|"
    r"产品经理|后端|前端|全栈|java|golang|python|c\+\+|"
    r"面经|面试|校招|秋招|春招|实习|offer|内推",
    re.I,
)

EXTRACT_PROMPT = """\
你是面经/求职帖结构化提取引擎。读完帖子标题 + 内容，输出以下 JSON。

字段定义：
- school：学校名称（如"清华大学"），如未明确写填 null
- school_tier："985" / "211" / "double-first"(双一流) / "international"(海外) / "other" / null
- major：专业名称（如"计算机科学"、"软件工程"），未提则 null
- degree："bachelor"(本科) / "master"(硕士) / "phd"(博士) / null
- graduation_year：毕业年份（4 位数字），未提则 null
- years_experience：工作经验年数（应届写 0），未提则 null
- company：投/面/拿 offer 的公司名称，未提则 null
- role_title：具体岗位名称（如"算法工程师"、"AI 产品经理"、"LLM 应用开发"），未提则 null
- offer_status："offered"(已拿 offer) / "rejected"(已挂) / "interviewing"(面试中) / "unknown"
- compensation_disclosed：自爆薪资折算成 RMB 月薪的整数（如年包 35w → 29167），未提或不可换算则 null
- market："domestic"(国内岗位) / "international"(海外岗位) / null

严格输出以下 JSON，不要添加任何额外文字：
{
  "school": "string | null",
  "school_tier": "985 | 211 | double-first | international | other | null",
  "major": "string | null",
  "degree": "bachelor | master | phd | null",
  "graduation_year": "int | null",
  "years_experience": "int | null",
  "company": "string | null",
  "role_title": "string | null",
  "offer_status": "offered | rejected | interviewing | unknown",
  "compensation_disclosed": "int | null",
  "market": "domestic | international | null"
}"""


def html_to_text(html: str | None) -> str:
    if not html:
        return ""
    return HTML_TAG_RE.sub(" ", html).replace("&nbsp;", " ").strip()


async def load_sitemap_urls(client: httpx.AsyncClient, max_urls: int) -> list[str]:
    resp = await client.get(SITEMAP_URL, timeout=30)
    resp.raise_for_status()
    urls = SITEMAP_LOC_RE.findall(resp.text)
    # Latest-first — sitemap is chronological.
    urls = list(reversed(urls))
    return urls[:max_urls]


async def fetch_post(
    client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore
) -> dict | None:
    async with sem:
        try:
            resp = await client.get(url, timeout=20)
            if resp.status_code != 200:
                return None
            m = INITIAL_STATE_RE.search(resp.text)
            if not m:
                return None
            import json
            try:
                state = json.loads(m.group(1))
            except json.JSONDecodeError:
                return None
            cd = (
                state.get("prefetchData", {})
                .get("2", {})
                .get("ssrCommonData", {})
                .get("contentData", {})
            )
            # contentData always carries a showMessage key; only treat the
            # post as missing when title/content are both empty.
            if not cd or not (cd.get("title") or cd.get("content")):
                return None
            ub = cd.get("userBrief") or {}
            return {
                "id": cd.get("id"),
                "url": url,
                "title": cd.get("title") or "",
                "content_html": cd.get("content"),
                "content_text": html_to_text(cd.get("content")),
                "create_time_ms": cd.get("createTime"),
                "user": {
                    "education": ub.get("educationInfo"),
                    "major": ub.get("secondMajorName"),
                    "auth_display": ub.get("authDisplayInfo"),
                    "work_time": ub.get("workTime"),
                },
            }
        except Exception as e:
            logger.debug("fetch fail %s: %s", url, str(e)[:120])
            return None


def title_relevant(title: str) -> bool:
    return bool(RELEVANT_TITLE_RE.search(title or ""))


async def parse_post(post: dict) -> dict | None:
    user = post.get("user") or {}
    prompt = (
        f"作者教育背景: {user.get('education') or '?'} / {user.get('major') or '?'}\n"
        f"作者认证显示: {user.get('auth_display') or '?'}\n"
        f"工作年份: {user.get('work_time') or '?'}\n\n"
        f"标题: {post['title']}\n\n"
        f"内容:\n{post['content_text'][:3000]}"
    )
    try:
        return await asyncio.wait_for(
            llm_json(prompt, system=EXTRACT_PROMPT, temperature=0.1),
            timeout=45,
        )
    except Exception as e:
        logger.debug("LLM parse fail for %s: %s", post.get("id"), str(e)[:120])
        return None


def to_row(post: dict, parsed: dict) -> dict:
    create_ms = post.get("create_time_ms")
    posted = (
        datetime.datetime.fromtimestamp(create_ms / 1000).date()
        if create_ms else None
    )
    return {
        "source": "nowcoder",
        "source_record_id": str(post["id"]),
        "source_url": post["url"],
        "school": parsed.get("school"),
        "school_tier": parsed.get("school_tier"),
        "major": parsed.get("major"),
        "degree": parsed.get("degree"),
        "graduation_year": parsed.get("graduation_year"),
        "years_experience": parsed.get("years_experience"),
        "company": parsed.get("company"),
        "role_title": parsed.get("role_title"),
        "role_id": None,  # filled later by export_applicant_profiles via title classifier
        "market": parsed.get("market") or "domestic",  # 牛客 user base is mostly 国内
        "offer_status": parsed.get("offer_status"),
        "compensation_disclosed": parsed.get("compensation_disclosed"),
        "title": post["title"][:500],
        "raw_text": post["content_text"][:8000],
        "parsed_json": parsed,
        "posted_date": posted,
    }


async def upsert_rows(rows: list[dict]) -> None:
    if not rows:
        return
    async with async_session() as db:
        stmt = insert(ApplicantProfile).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_applicant_source_record",
            set_={
                "school": stmt.excluded.school,
                "school_tier": stmt.excluded.school_tier,
                "major": stmt.excluded.major,
                "degree": stmt.excluded.degree,
                "graduation_year": stmt.excluded.graduation_year,
                "years_experience": stmt.excluded.years_experience,
                "company": stmt.excluded.company,
                "role_title": stmt.excluded.role_title,
                "market": stmt.excluded.market,
                "offer_status": stmt.excluded.offer_status,
                "compensation_disclosed": stmt.excluded.compensation_disclosed,
                "title": stmt.excluded.title,
                "raw_text": stmt.excluded.raw_text,
                "parsed_json": stmt.excluded.parsed_json,
                "posted_date": stmt.excluded.posted_date,
            },
        )
        await db.execute(stmt)
        await db.commit()


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-urls", type=int, default=2000)
    parser.add_argument("--fetch-concurrency", type=int, default=8)
    parser.add_argument("--llm-concurrency", type=int, default=20)
    args = parser.parse_args()

    headers = {"User-Agent": UA, "Accept": "text/html"}
    async with httpx.AsyncClient(headers=headers) as client:
        urls = await load_sitemap_urls(client, args.max_urls)
        logger.info("sitemap: %d candidate URLs", len(urls))

        fetch_sem = asyncio.Semaphore(args.fetch_concurrency)
        posts: list[dict] = []
        for i in range(0, len(urls), 100):
            batch = urls[i : i + 100]
            results = await asyncio.gather(
                *[fetch_post(client, u, fetch_sem) for u in batch]
            )
            posts.extend([p for p in results if p])
            logger.info(
                "fetched %d/%d (kept %d)",
                min(i + 100, len(urls)), len(urls), len(posts),
            )

    relevant = [p for p in posts if title_relevant(p["title"])]
    logger.info(
        "relevant by title: %d / %d (%.1f%%)",
        len(relevant), len(posts),
        100 * len(relevant) / max(1, len(posts)),
    )

    llm_sem = asyncio.Semaphore(args.llm_concurrency)
    rows: list[dict] = []
    failed = 0

    async def run_one(p):
        async with llm_sem:
            parsed = await parse_post(p)
            return p, parsed

    for i in range(0, len(relevant), 50):
        batch = relevant[i : i + 50]
        out = await asyncio.gather(*[run_one(p) for p in batch])
        batch_rows = []
        for p, parsed in out:
            if not parsed:
                failed += 1
                continue
            batch_rows.append(to_row(p, parsed))
        await upsert_rows(batch_rows)
        rows.extend(batch_rows)
        logger.info(
            "parsed %d/%d (rows so far=%d, failed=%d)",
            min(i + 50, len(relevant)), len(relevant), len(rows), failed,
        )

    logger.info("done — upserted %d applicant_profiles", len(rows))


if __name__ == "__main__":
    asyncio.run(main())
