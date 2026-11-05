# Task 1: FastAPI application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from models.database import init_db
    init_db()
    yield
    # Shutdown (nothing needed)


app = FastAPI(
    title="SkillProof API",
    description="GitHub behavioral analysis and developer readiness verification",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # locked to explicit origins via CORS_ORIGINS env var
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Scheduler-Secret"],
    max_age=600,  # preflight cache: 10 minutes
)

# Import and include all routers
from auth.router import router as auth_router
from routers.analysis import router as analysis_router
from routers.target_roles import router as target_roles_router
from routers.chat import router as chat_router
from routers.notifications import router as notifications_router
from routers.share import router as share_router
from routers.public_profile import router as public_profile_router
from routers.scheduler import router as scheduler_router
from routers.jobs import router as jobs_router
from routers.settings import router as settings_router

app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(target_roles_router)
app.include_router(chat_router)
app.include_router(notifications_router)
app.include_router(share_router)
app.include_router(public_profile_router)
app.include_router(scheduler_router)
app.include_router(jobs_router)
app.include_router(settings_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "SkillProof API",
    }


@app.get("/health")
def render_health():
    """Render.com health-check endpoint — must return 200 for the service to stay up."""
    return {"status": "ok"}
