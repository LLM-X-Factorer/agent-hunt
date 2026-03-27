from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.job import JobImportRequest


class BaseCollector(ABC):

    @property
    @abstractmethod
    def platform_id(self) -> str:
        ...

    @abstractmethod
    async def collect(
        self, keyword: str, max_pages: int = 5
    ) -> list[JobImportRequest]:
        ...
