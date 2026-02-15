from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve project root for SQLite default path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB = f"sqlite:///{_PROJECT_ROOT / 'finance_tracker.db'}"


class Settings(BaseSettings):
    APP_NAME: str = "Finance Tracker"
    DEBUG: bool = False

    # Database — defaults to SQLite so it works on any laptop with zero setup.
    # Set DATABASE_URL env var to use PostgreSQL in production.
    DATABASE_URL: str = _DEFAULT_DB

    # Auth
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Anthropic — optional, can also be set per-user via Settings page
    ANTHROPIC_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
