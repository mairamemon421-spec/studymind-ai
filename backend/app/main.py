"""StudyMind AI — FastAPI application entry point."""
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db

settings = get_settings()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    # Startup: auto-create tables only for SQLite (local dev).
    # For Supabase/PostgreSQL, schema is managed via supabase_setup.sql.
    if settings.use_sqlite:
        await init_db()
    else:
        print("[Startup] Skipping init_db() - Supabase schema managed via supabase_setup.sql")
    print(f"[Startup] {settings.APP_NAME} started")
    print(f"   Database: {'SQLite' if settings.use_sqlite else 'PostgreSQL'}")
    print(f"   Gemini:   {'Connected' if settings.has_gemini else 'Mock mode'}")
    yield
    # Shutdown
    print(f"[Shutdown] {settings.APP_NAME} shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Agent AI Study Planner & Tutor",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def exception_logging_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception during request {request.url.path}: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)}
        )


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.routers import auth, subjects, plans, tutor, quiz, logs, export, progress  # noqa: E402

app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(plans.router)
app.include_router(tutor.router)
app.include_router(quiz.router)
app.include_router(logs.router)
app.include_router(export.router)
app.include_router(progress.router)


@app.get("/")
async def root():
    return {"message": "StudyMind AI API is running"}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "database": "sqlite" if settings.use_sqlite else "postgresql",
        "gemini": "connected" if settings.has_gemini else "mock",
    }
