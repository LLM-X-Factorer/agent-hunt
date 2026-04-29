"""Currency normalization for salary aggregation.

The ``jobs.salary_min/max`` columns store *raw* parsed values along with
``salary_currency``. International JDs typically quote *annual* foreign-
currency totals (USD/EUR/GBP per year), while domestic JDs quote *monthly*
RMB. Cross-market comparisons must convert both to a common unit before
aggregation, otherwise USD/year gets misread as CNY/month and the ratio
inflates by ~12×.

This module provides ``to_cny_monthly`` — the only conversion path the
narrative export scripts use. The exchange rates here are coarse 2026
spot rates; we don't need precision for what's already a noisy salary
range field. Rates centralized so we update them in one place.
"""
from __future__ import annotations

# Spot rates as of 2026-04 (rough — salary ranges are inherently noisy).
EXCHANGE_RATES_TO_CNY: dict[str, float] = {
    "CNY": 1.0,
    "USD": 7.2,
    "EUR": 7.8,
    "GBP": 9.0,
    "CAD": 5.3,
    "AUD": 4.8,
    "CHF": 8.0,
    "SGD": 5.4,
    "HKD": 0.92,
    "JPY": 0.05,
    "INR": 0.087,
}

# A CNY value below this is monthly; above → assume annual (parser misfire).
# 200k/月 ≈ 2.4M/年 — the upper end for Chinese AI senior positions is real,
# but values stored above this are almost always annual ranges that slipped through.
DOMESTIC_MONTHLY_CAP_CNY = 200_000


def to_cny_monthly(value: int | float, currency: str | None) -> float | None:
    """Convert a single salary value to CNY/month.

    Heuristic:
      * Foreign currency (USD/EUR/GBP/...): the raw is annual → ÷12 then × FX.
      * CNY: monthly if < 200k, else annual (÷12).
      * Unknown currency: returned as-is, treated as CNY/month.
    """
    if value is None:
        return None
    cur = (currency or "CNY").upper()
    if cur == "CNY":
        return value / 12.0 if value > DOMESTIC_MONTHLY_CAP_CNY else float(value)
    rate = EXCHANGE_RATES_TO_CNY.get(cur)
    if rate is None:
        return float(value)  # unknown currency: be conservative, no conversion
    return value * rate / 12.0


def midpoint_cny_monthly(
    salary_min: int | None,
    salary_max: int | None,
    currency: str | None,
) -> float | None:
    """Midpoint of a salary range, normalized to CNY/month."""
    if salary_min is None or salary_max is None:
        return None
    a = to_cny_monthly(salary_min, currency)
    b = to_cny_monthly(salary_max, currency)
    if a is None or b is None:
        return None
    return (a + b) / 2.0
