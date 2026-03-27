from __future__ import annotations

import hashlib
import logging

from jobspy import scrape_jobs

from app.collectors.base import BaseCollector
from app.collectors.registry import register
from app.schemas.job import JobImportRequest

logger = logging.getLogger(__name__)

SITE_TO_PLATFORM = {
    "linkedin": "linkedin",
    "indeed": "indeed",
    "glassdoor": "glassdoor",
}


class JobSpyCollector(BaseCollector):

    def __init__(self, site: str):
        self._site = site
        self._platform_id = SITE_TO_PLATFORM[site]

    @property
    def platform_id(self) -> str:
        return self._platform_id

    async def collect(
        self, keyword: str, max_pages: int = 5
    ) -> list[JobImportRequest]:
        results_wanted = max_pages * 20

        logger.info(
            "JobSpy collecting from %s: keyword=%r, results_wanted=%d",
            self._site, keyword, results_wanted,
        )

        df = scrape_jobs(
            site_name=[self._site],
            search_term=keyword,
            results_wanted=results_wanted,
            linkedin_fetch_description=True,
            description_format="markdown",
            verbose=0,
        )

        if df is None or df.empty:
            logger.warning("No results from %s for %r", self._site, keyword)
            return []

        jobs: list[JobImportRequest] = []
        for _, row in df.iterrows():
            job_url = str(row.get("job_url", "")) or ""
            description = str(row.get("description", "")) or ""

            if not description or len(description) < 10:
                continue

            platform_job_id = _make_job_id(job_url, description)

            raw_parts = []
            for field in ("title", "company", "city", "state", "job_type"):
                val = row.get(field)
                if val and str(val) != "nan":
                    raw_parts.append(f"{field}: {val}")

            salary = _format_salary(row)
            if salary:
                raw_parts.append(f"salary: {salary}")

            raw_parts.append(f"\n{description}")
            raw_content = "\n".join(raw_parts)

            jobs.append(JobImportRequest(
                platform_id=self._platform_id,
                platform_job_id=platform_job_id,
                source_url=job_url or None,
                raw_content=raw_content,
                language="en",
            ))

        logger.info("Collected %d jobs from %s", len(jobs), self._site)
        return jobs


def _make_job_id(job_url: str, description: str) -> str:
    if job_url:
        return hashlib.md5(job_url.encode()).hexdigest()[:16]
    return hashlib.md5(description.encode()).hexdigest()[:16]


def _format_salary(row) -> str | None:
    min_amt = row.get("min_amount")
    max_amt = row.get("max_amount")
    interval = row.get("interval")

    if min_amt and str(min_amt) != "nan":
        parts = []
        if str(min_amt) != "nan":
            parts.append(str(int(float(min_amt))))
        if max_amt and str(max_amt) != "nan":
            parts.append(str(int(float(max_amt))))
        salary = " - ".join(parts)
        if interval and str(interval) != "nan":
            salary += f" / {interval}"
        return salary
    return None


# Register collectors for each supported site
linkedin_collector = register(JobSpyCollector("linkedin"))
indeed_collector = register(JobSpyCollector("indeed"))
glassdoor_collector = register(JobSpyCollector("glassdoor"))
