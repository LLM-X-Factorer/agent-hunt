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


# OpenRouter reserves max_tokens worth of credit upfront. The OpenAI SDK
# doesn't send this field by default, so the provider falls back to the
# model's max (65535 for deepseek-v3.2-exp) — which 402s when the account
# balance drops below ~$0.20 even for tiny JSON responses. Explicit caps
# keep small structured tasks runnable on low credit balances.
DEFAULT_MAX_TOKENS_TEXT = 4000
# Structured JSON outputs sit between tiny labels (~150 tokens) and full
# JD parses (~1500 tokens). 2000 covers the heavy case; callers with smaller
# expected output (e.g. backfill_quality_labels) can pass a tighter cap.
DEFAULT_MAX_TOKENS_JSON = 2000


async def llm_text(
    prompt: str,
    system: str = "",
    temperature: float = 0.7,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS_TEXT,
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
        max_tokens=max_tokens,
    )
    return (response.choices[0].message.content or "").strip()


async def llm_json(
    prompt: str,
    system: str = "",
    temperature: float = 0.3,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS_JSON,
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
        max_tokens=max_tokens,
    )
    text = (response.choices[0].message.content or "").strip()
    return json.loads(text)
