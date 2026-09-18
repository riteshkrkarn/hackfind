from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./hackfind.db"
    api_port: int = 8002
    agent_cron_minutes: int = 60
    use_seed_source: bool = False
    cors_origins: str = "http://localhost:3000"
    http_timeout_seconds: float = 20.0
    user_agent: str = (
        "HackfindBot/0.1 (+https://github.com/hackfind; personal hackathon finder)"
    )

    # Comma-separated builtin adapters to enable
    enabled_builtin_sources: str = "devpost,devfolio,mlh,hackerearth"

    # File-based generic sources (JSON array or {"sources": [...]})
    sources_file: str = "sources.json"

    # Tavily web search discovery
    tavily_api_key: str = ""
    tavily_enabled: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
