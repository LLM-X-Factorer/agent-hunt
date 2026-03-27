from __future__ import annotations

from app.collectors.base import BaseCollector

_collectors: dict[str, BaseCollector] = {}


def register(collector: BaseCollector) -> BaseCollector:
    _collectors[collector.platform_id] = collector
    return collector


def get_collector(platform_id: str) -> BaseCollector:
    try:
        return _collectors[platform_id]
    except KeyError:
        available = ", ".join(sorted(_collectors)) or "(none)"
        raise ValueError(
            f"No collector registered for '{platform_id}'. Available: {available}"
        )


def list_collectors() -> dict[str, BaseCollector]:
    return dict(_collectors)
