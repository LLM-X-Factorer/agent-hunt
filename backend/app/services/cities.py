"""City normalization and tier classification.

Used by export scripts that need to slice jobs by Chinese city tier
(一线 / 新一线 / 其他 / 海外 / 远程). Extracted out of
``export_graduate_friendly.py`` so multiple export scripts can share it.
"""
from __future__ import annotations

import re

# Match canonical city prefix at the start of a `Job.location` string,
# stripping suffixes like "市" / "·南山区" / "-海淀区".
CITY_NORMALIZE_RE = re.compile(
    r"^(北京|上海|深圳|杭州|成都|广州|南京|武汉|西安|苏州|天津|厦门|郑州|香港|台北|新加坡|吉隆坡|远程)"
)

# State codes / countries / chrome that show up in scraped location strings.
NOISE_TOKENS = {
    "ca", "ny", "wa", "tx", "ma", "il", "nj", "co", "ga", "fl", "va", "or",
    "az", "nc", "pa", "mn", "oh", "mi", "mo", "ut", "tn", "md", "wi",
    "us", "usa", "uk", "canada", "remote", "hybrid", "onsite", "on", "qc",
    "and", "nan", "none",
}


def normalize_city(raw: str | None) -> str | None:
    """Map "北京市" / "深圳·南山区" → canonical city; drop state codes / noise."""
    if not raw:
        return None
    raw = raw.strip().replace("·", " ").rstrip(",.;")
    if not raw or raw.lower() in NOISE_TOKENS:
        return None

    m = CITY_NORMALIZE_RE.match(raw)
    if m:
        return m.group(1)
    if raw.endswith("市") and len(raw) <= 6:
        return raw[:-1]
    if any("一" <= ch <= "鿿" for ch in raw):
        return raw[:6] if len(raw) > 6 else raw

    if len(raw) < 3:
        return None
    return raw


_CITY_SPLIT_LATIN_RE = re.compile(r"\s*[,/|;]\s*")
_CITY_SPLIT_CN_RE = re.compile(r"[、，]")


def split_locations(loc: str | None) -> list[str]:
    """A single Job.location can be "北京、上海" or "San Francisco, CA, Seattle, WA" —
    return canonical city tokens after dropping state abbrevs / noise."""
    if not loc:
        return []
    has_cn = any("一" <= ch <= "鿿" for ch in loc)
    parts = (_CITY_SPLIT_CN_RE.split(loc) if has_cn else _CITY_SPLIT_LATIN_RE.split(loc))
    return [c for p in parts if (c := normalize_city(p))]


# China city tiering reference (新一线榜 + 国家统计 spec). We collapse to 4
# tiers because aijobfit's salary slice only needs that resolution — adding
# tier-3/4 cities adds noise without changing the user-facing answer.
TIER_1 = {"北京", "上海", "广州", "深圳"}
TIER_NEW_1 = {
    "杭州", "成都", "武汉", "南京", "苏州", "西安", "重庆", "天津",
    "长沙", "青岛", "郑州", "宁波", "东莞", "沈阳", "合肥",
}
REMOTE_TOKENS = {"远程", "Remote", "remote", "Anywhere", "anywhere"}


def city_tier(city: str | None) -> str:
    """Coarse tier bucket: 一线 / 新一线 / 其他国内 / 海外 / 远程 / 未知."""
    if not city:
        return "未知"
    if city in REMOTE_TOKENS:
        return "远程"
    if city in TIER_1:
        return "一线"
    if city in TIER_NEW_1:
        return "新一线"
    if any("一" <= ch <= "鿿" for ch in city):
        return "其他国内"
    return "海外"
