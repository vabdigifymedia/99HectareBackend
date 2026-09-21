from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app import models  # noqa: F401 - Register all models with SQLAlchemy
from sqlalchemy.exc import IntegrityError
from app.common.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    integrity_exception_handler,
)
from app.common.exceptions import AppException
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.modules.routes import router as routes
from sqlalchemy.orm import configure_mappers

# Ensure all SQLAlchemy relationships are configured across all registered models
configure_mappers()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────

app.include_router(routes, prefix="/api/v1")
from app.modules.admin.routes import router as admin_router  # noqa: E402
app.include_router(admin_router)


# ── Exception Handlers ─────────────────────────────────────────────

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)



@app.get("/")
async def root():
    return {"message": "Real Estate API running"}


@app.get("/db-test")
async def db_test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return {"database": result.scalar()}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
