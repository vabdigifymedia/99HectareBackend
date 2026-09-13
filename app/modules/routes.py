from fastapi import APIRouter

from app.modules.auth.routes import router as auth_router
from app.modules.favorites.routes import router as favorite_router
from app.modules.inquiries.routes import router as inquiry_router
from app.modules.locations.routes import router as locations_router
from app.modules.properties.routes import router as property_router
from app.modules.visits.routes import router as visit_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(locations_router)
router.include_router(property_router)
router.include_router(favorite_router)
router.include_router(inquiry_router)
router.include_router(visit_router)