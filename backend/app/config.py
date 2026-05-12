# Application configuration via environment variables.
from pathlib import Path

from pydantic_settings import BaseSettings

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = {
        "env_prefix": "AH_",
        "env_file": str(_PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
    }

    # --- Database ---
    # AH_DATABASE_URL_OVERRIDE wins when set (cloud-hosted Postgres like
    # Supabase / Neon). Format: postgresql://user:pass@host:5432/db
    # When empty, fall back to the host/user/password split fields used
    # by docker-compose local dev.
    database_url_override: str = ""
    postgres_user: str = "agent_hunt"
    postgres_password: str = "agent_hunt_dev"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "agent_hunt"

    @staticmethod
    def _coerce_async_url(url: str) -> str:
        """Ensure the asyncpg driver prefix even if pasted as `postgresql://`."""
        if url.startswith("postgresql+asyncpg://"):
            return url
        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url[len("postgresql://"):]
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://"):]
        return url

    @staticmethod
    def _coerce_sync_url(url: str) -> str:
        if url.startswith("postgresql+asyncpg://"):
            return "postgresql://" + url[len("postgresql+asyncpg://"):]
        if url.startswith("postgres://"):
            return "postgresql://" + url[len("postgres://"):]
        return url

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self._coerce_async_url(self.database_url_override)
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations."""
        if self.database_url_override:
            return self._coerce_sync_url(self.database_url_override)
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # --- Redis ---
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # --- LLM provider (OpenAI-compatible) ---
    # Two-key system so we can switch hosts without renaming env vars:
    #   AH_LLM_API_KEY     — preferred (provider-agnostic name)
    #   AH_OPENROUTER_API_KEY — legacy fallback (kept so existing .env works)
    # Examples:
    #   DeepSeek direct: AH_LLM_BASE_URL=https://api.deepseek.com, AH_LLM_MODEL=deepseek-chat
    #   OpenRouter:      AH_LLM_BASE_URL=https://openrouter.ai/api/v1, AH_LLM_MODEL=deepseek/deepseek-v3.2-exp
    llm_api_key: str = ""
    openrouter_api_key: str = ""  # legacy
    llm_model: str = "deepseek-chat"
    llm_base_url: str = "https://api.deepseek.com"

    @property
    def effective_llm_api_key(self) -> str:
        return self.llm_api_key or self.openrouter_api_key

    # Legacy Gemini settings — kept for compare_llm_providers.py only.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # --- App ---
    debug: bool = False
    api_prefix: str = "/api/v1"

    # --- Currency conversion (fixed rates, CNY as base) ---
    usd_to_cny: float = 7.25
    eur_to_cny: float = 7.90


settings = Settings()
