from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginatedResponse
from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import require_builder
from app.modules.builders.controller import BuilderController
from app.modules.builders.schemas import BuilderResponse, BuilderUpdate
from app.modules.users.models import User

router = APIRouter(prefix="/builders", tags=["builders"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BuilderController:
    return BuilderController(db)


@router.get(
    "/me",
    response_model=SuccessResponse[BuilderResponse],
    summary="Get current builder profile",
    description="Retrieve the profile of the currently authenticated builder.",
)
async def get_my_builder_profile(
    current_user: Annotated[User, Depends(require_builder)],
    controller: BuilderController = Depends(get_controller),
):
    builder = await controller.get_by_user_id(user_id=current_user.id)
    return SuccessResponse(
        message="Builder profile retrieved successfully",
        data=builder,
    )


@router.put(
    "/me",
    response_model=SuccessResponse[BuilderResponse],
    summary="Update current builder profile",
    description="Update profile details for the authenticated builder.",
)
async def update_my_builder_profile(
    body: BuilderUpdate,
    current_user: Annotated[User, Depends(require_builder)],
    controller: BuilderController = Depends(get_controller),
):
    builder = await controller.update_profile(current_user=current_user, data=body)
    return SuccessResponse(
        message="Builder profile updated successfully",
        data=builder,
    )


@router.get(
    "",
    response_model=PaginatedResponse[BuilderResponse],
    summary="List builders",
    description="Public list of builders with filters and pagination.",
)
async def list_builders(
    controller: BuilderController = Depends(get_controller),
    search: str | None = Query(None),
    is_active: bool | None = Query(True),
    is_featured: bool | None = Query(None),
    verification_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    filters = {
        "search": search,
        "is_active": is_active,
        "is_featured": is_featured,
        "verification_status": verification_status,
    }
    items, total = await controller.list_builders(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{id}",
    response_model=SuccessResponse[BuilderResponse],
    summary="Get builder by ID",
    description="Retrieve public profile of a builder by ID.",
)
async def get_builder(
    id: int,
    controller: BuilderController = Depends(get_controller),
):
    builder = await controller.get_by_id(builder_id=id)
    return SuccessResponse(
        message="Builder retrieved successfully",
        data=builder,
    )
