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
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://99-hectare.vercel.app",
        "https://99-hectare-three.vercel.app/",
        "https://99-hectare-pru5e87ex-vabit-digify-media.vercel.app",
    ],
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
@app.get("/api/v1/db-test")
async def db_test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return {"database": result.scalar()}


@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/v1/system/status")
@app.get("/system/status")
async def system_status():
    import time
    try:
        import redis.asyncio as aioredis
    except ImportError:
        aioredis = None

    status = {
        "api": {
            "status": "online",
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "cors_origins": settings.cors_origins_list,
        },
        "database": {"status": "unknown"},
        "redis": {"status": "unknown"},
        "auth": {"status": "unknown"},
        "demo_accounts": [
            {
                "role": "buyer",
                "email": "aditya.mehta@example.com",
                "password": "password123",
                "name": "Aditya Mehta",
            },
            {
                "role": "agent",
                "email": "vikram.sharma@horizonrealty.in",
                "password": "password123",
                "name": "Vikram Sharma",
            },
            {
                "role": "admin",
                "email": "admin@99hectares.com",
                "password": "admin123",
                "name": "Platform Administrator",
            },
        ],
    }

    # 1. Database check
    t0 = time.time()
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_latency_ms = round((time.time() - t0) * 1000, 2)

            user_count_res = await session.execute(text("SELECT count(*) FROM users"))
            user_count = user_count_res.scalar() or 0

            tables_res = await session.execute(
                text(
                    "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
                )
            )
            table_count = tables_res.scalar() or 0

            status["database"] = {
                "status": "connected",
                "latency_ms": db_latency_ms,
                "tables_count": table_count,
                "users_count": user_count,
            }
    except Exception as e:
        status["database"] = {
            "status": "error",
            "error": str(e),
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }

    # 2. Redis check
    t1 = time.time()
    if aioredis:
        try:
            r = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=1.5)
            await r.ping()
            redis_latency_ms = round((time.time() - t1) * 1000, 2)
            await r.aclose()
            status["redis"] = {
                "status": "connected",
                "latency_ms": redis_latency_ms,
            }
        except Exception as e:
            status["redis"] = {
                "status": "offline_or_error",
                "error": str(e),
                "latency_ms": round((time.time() - t1) * 1000, 2),
            }
    else:
        status["redis"] = {"status": "package_not_installed"}

    # 3. Auth configuration check
    try:
        from app.core.security import create_access_token, decode_token

        test_token = create_access_token(
            subject="diagnostic-ping", claims={"role": "system"}
        )
        payload = decode_token(test_token)
        status["auth"] = {
            "status": "healthy",
            "algorithm": settings.JWT_ALGORITHM,
            "access_token_expire_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
            "token_verification": "passed"
            if payload.get("sub") == "diagnostic-ping"
            else "failed",
        }
    except Exception as e:
        status["auth"] = {
            "status": "error",
            "error": str(e),
        }

    return status
