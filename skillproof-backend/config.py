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
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    GEMINI_FALLBACK_MODEL: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite")
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

    # CORS — in production set this to your exact Vercel URL, e.g.:
    # CORS_ORIGINS=https://skillproof.vercel.app
    # Multiple origins: CORS_ORIGINS=https://skillproof.vercel.app,https://www.skillproof.app
    CORS_ORIGINS: list = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]

    # App limits
    MAX_TARGET_ROLES_PER_USER: int = 3
    CACHE_TTL_SECONDS: int = 1800  # 30 minutes — avoids re-fetch on re-analyze


settings = Settings()
