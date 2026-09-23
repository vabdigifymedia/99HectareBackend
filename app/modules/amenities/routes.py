from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.modules.amenities.models import Amenity
from app.modules.amenities.schemas import AmenityResponse

router = APIRouter(prefix="/amenities", tags=["amenities"])


@router.get(
    "",
    response_model=SuccessResponse[list[AmenityResponse]],
    summary="List all amenities",
)
async def list_amenities(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Amenity).where(Amenity.is_active.is_(True)).order_by(Amenity.category, Amenity.name)
    )
    amenities = list(result.scalars().all())
    return SuccessResponse(
        message="Amenities retrieved successfully",
        data=amenities,
    )
