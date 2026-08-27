# Task 1: Project configuration — reads all environment variables
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # GitHub
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO_CAP: int = 15

    # Gemini LLM
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    GEMINI_FALLBACK_MODEL: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.0-flash-lite")
    USE_LLM_MOCK: bool = os.getenv("USE_LLM_MOCK", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_REFRESH_SECRET: str = os.getenv("JWT_REFRESH_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    # Scheduler
    SCHEDULER_SECRET: str = os.getenv("SCHEDULER_SECRET", "")

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # App limits
    MAX_TARGET_ROLES_PER_USER: int = 3
    CACHE_TTL_SECONDS: int = 900  # 15 minutes


settings = Settings()
