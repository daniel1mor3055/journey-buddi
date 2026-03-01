from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://journeybuddi:localdev@localhost:5432/journeybuddi"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-production"
    magic_link_secret: str = "change-me-magic-link-secret"
    resend_api_key: str = ""
    from_email: str = "noreply@journeybuddi.com"
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    openweathermap_api_key: str = ""

    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_claims_email: str = "mailto:admin@journeybuddi.com"

    access_token_expire_days: int = 30
    magic_link_expire_minutes: int = 15

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
