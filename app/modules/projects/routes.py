from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginatedResponse
from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.projects.controller import ProjectController
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.modules.users.models import User

router = APIRouter(prefix="/projects", tags=["projects"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectController:
    return ProjectController(db)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    summary="List and search projects with filters",
)
async def list_projects(
    controller: ProjectController = Depends(get_controller),
    search: str | None = Query(None, description="Search in project name, description, address"),
    builder_id: int | None = Query(None),
    city_id: int | None = Query(None),
    locality_id: int | None = Query(None),
    status: str | None = Query(None),
    project_type: str | None = Query(None),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    sort_by: str = Query("newest", description="Sort by newest, price_asc, price_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
):
    filters = {
        "search": search,
        "builder_id": builder_id,
        "city_id": city_id,
        "locality_id": locality_id,
        "status": status,
        "project_type": project_type,
        "min_price": min_price,
        "max_price": max_price,
    }
    items, total = await controller.list_projects(
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
    )
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
    response_model=SuccessResponse[ProjectDetailResponse],
    summary="Get project details by ID or slug",
)
async def get_project(
    id: str,
    controller: ProjectController = Depends(get_controller),
):
    proj = await controller.get_project(id)
    return SuccessResponse(
        message="Project retrieved successfully",
        data=proj,
    )


@router.post(
    "",
    response_model=SuccessResponse[ProjectDetailResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
    body: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: ProjectController = Depends(get_controller),
):
    proj = await controller.create_project(body)
    return SuccessResponse(
        message="Project created successfully",
        data=proj,
    )
