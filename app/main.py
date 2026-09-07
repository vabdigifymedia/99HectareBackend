from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import AsyncSessionLocal

from app.common.exception_handlers import app_exception_handler, generic_exception_handler
from app.common.exceptions import AppException
from app.core.config import settings
from app.modules.routes import router as routes

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

# ── Exception Handlers ─────────────────────────────────────────────

app.add_exception_handler(AppException, app_exception_handler)
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
