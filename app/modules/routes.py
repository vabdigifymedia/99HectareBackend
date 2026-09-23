from fastapi import APIRouter

from app.modules.admin.routes import router as admin_router
from app.modules.agents.routes import router as agents_router
from app.modules.amenities.routes import router as amenities_router
from app.modules.auth.routes import router as auth_router
from app.modules.builders.routes import router as builders_router
from app.modules.favorites.routes import router as favorite_router
from app.modules.inquiries.routes import router as inquiry_router
from app.modules.locations.routes import router as locations_router
from app.modules.projects.routes import router as projects_router
from app.modules.properties.routes import router as property_router
from app.modules.reports.routes import router as reports_router
from app.modules.users.routes import router as users_router
from app.modules.visits.routes import router as visit_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(locations_router)
router.include_router(property_router)
router.include_router(projects_router)
router.include_router(amenities_router)
router.include_router(favorite_router)
router.include_router(inquiry_router)
router.include_router(visit_router)
router.include_router(agents_router)
router.include_router(builders_router)
router.include_router(reports_router)
router.include_router(users_router)
router.include_router(admin_router)