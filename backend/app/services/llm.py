# Shared LLM client for OpenRouter (OpenAI-compatible).
# Used by jd_parser, generate_insights, generate_report.
# Switch model with AH_LLM_MODEL — see app/config.py for examples.
from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        if not settings.openrouter_api_key:
            raise RuntimeError("AH_OPENROUTER_API_KEY is not set; cannot call LLM.")
        # Tight timeout — OpenAI SDK defaults to 600s, which made backfills
        # hang on dropped upstream connections. 60s is plenty for short JD
        # prompts; failed requests get retried by the caller's batch logic.
        _client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.openrouter_api_key,
            timeout=60.0,
            max_retries=1,
        )
    return _client


async def llm_text(
    prompt: str,
    system: str = "",
    temperature: float = 0.7,
    model: str | None = None,
) -> str:
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=model or settings.llm_model,
        messages=messages,
        temperature=temperature,
    )
    return (response.choices[0].message.content or "").strip()


async def llm_json(
    prompt: str,
    system: str = "",
    temperature: float = 0.3,
    model: str | None = None,
) -> dict | list:
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=model or settings.llm_model,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    text = (response.choices[0].message.content or "").strip()
    return json.loads(text)
