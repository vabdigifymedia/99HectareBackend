from fastapi import APIRouter

from app.modules.auth.routes import router as auth_router
from app.modules.properties.routes import router as property_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(property_router)