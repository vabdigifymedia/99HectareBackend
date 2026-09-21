from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginatedResponse
from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_agent
from app.modules.agents.controller import AgentController
from app.modules.agents.schemas import (
    AgentBulkPropertyCreate,
    AgentBulkPropertyResponse,
    AgentProfileCreate,
    AgentResponse,
    AgentUpdate,
)
from app.modules.properties.schemas import PropertyCreate, PropertyDetailResponse, PropertyResponse
from app.modules.users.models import User

router = APIRouter(prefix="/agents", tags=["agents"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentController:
    return AgentController(db)


# ── Profile Management ────────────────────────────────────────────────


@router.post(
    "",
    response_model=SuccessResponse[AgentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create or initialize agent profile",
    description="Initialize an agent profile for the authenticated user.",
)
async def create_agent_profile(
    body: AgentProfileCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: AgentController = Depends(get_controller),
):
    agent = await controller.create_profile(current_user=current_user, data=body)
    return SuccessResponse(
        message="Agent profile created successfully",
        data=agent,
    )


@router.get(
    "/me",
    response_model=SuccessResponse[AgentResponse],
    summary="Get current agent profile",
    description="Retrieve the profile of the currently logged-in agent.",
)
async def get_my_agent_profile(
    current_user: Annotated[User, Depends(require_agent)],
    controller: AgentController = Depends(get_controller),
):
    agent = await controller.get_by_user_id(user_id=current_user.id)
    return SuccessResponse(
        message="Agent profile retrieved successfully",
        data=agent,
    )


@router.put(
    "/me",
    response_model=SuccessResponse[AgentResponse],
    summary="Update current agent profile",
    description="Update the profile details of the currently logged-in agent.",
)
async def update_my_agent_profile(
    body: AgentUpdate,
    current_user: Annotated[User, Depends(require_agent)],
    controller: AgentController = Depends(get_controller),
):
    agent = await controller.update_profile(current_user=current_user, data=body)
    return SuccessResponse(
        message="Agent profile updated successfully",
        data=agent,
    )


# ── Agent Listings & Bulk Creation ────────────────────────────────────


@router.get(
    "/me/properties",
    response_model=PaginatedResponse[PropertyResponse],
    summary="Get my property listings",
    description="Retrieve all properties listed by the currently authenticated agent.",
)
async def get_my_properties(
    current_user: Annotated[User, Depends(require_agent)],
    controller: AgentController = Depends(get_controller),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await controller.get_my_properties(
        current_user=current_user,
        status=status_filter,
        page=page,
        page_size=page_size,
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


@router.post(
    "/me/properties",
    response_model=SuccessResponse[PropertyDetailResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Agent creates single property",
    description="Allows authenticated agent to add a new property listing.",
)
async def create_agent_property(
    body: PropertyCreate,
    current_user: Annotated[User, Depends(require_agent)],
    controller: AgentController = Depends(get_controller),
):
    prop = await controller.create_property(current_user=current_user, data=body)
    return SuccessResponse(
        message="Property created successfully by agent",
        data=prop,
    )


@router.post(
    "/me/properties/bulk",
    response_model=SuccessResponse[AgentBulkPropertyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Agent adds multiple properties in bulk",
    description="Allows an authenticated agent to submit and create multiple property listings at once.",
)
async def create_bulk_properties(
    body: AgentBulkPropertyCreate,
    current_user: Annotated[User, Depends(require_agent)],
    controller: AgentController = Depends(get_controller),
):
    created = await controller.create_bulk_properties(current_user=current_user, data=body)
    return SuccessResponse(
        message=f"Successfully created {len(created)} properties",
        data=AgentBulkPropertyResponse(
            created_count=len(created),
            properties=created,
        ),
    )


@router.post(
    "/properties/bulk",
    response_model=SuccessResponse[AgentBulkPropertyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Alias: Agent adds multiple properties in bulk",
    description="Alias endpoint for bulk property creation by authenticated agents.",
)
async def create_bulk_properties_alias(
    body: AgentBulkPropertyCreate,
    current_user: Annotated[User, Depends(require_agent)],
    controller: AgentController = Depends(get_controller),
):
    return await create_bulk_properties(body=body, current_user=current_user, controller=controller)


# ── Public Agent Directory ────────────────────────────────────────────


@router.get(
    "",
    response_model=PaginatedResponse[AgentResponse],
    summary="List agents with filters and pagination",
    description="Public directory listing for agents.",
)
async def list_agents(
    controller: AgentController = Depends(get_controller),
    search: str | None = Query(None, description="Search agency name, description, license, or phone"),
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
    items, total = await controller.list_agents(filters=filters, page=page, page_size=page_size)
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
    response_model=SuccessResponse[AgentResponse],
    summary="Get agent by ID",
    description="Retrieve public profile of an agent by ID.",
)
async def get_agent(
    id: int,
    controller: AgentController = Depends(get_controller),
):
    agent = await controller.get_by_id(agent_id=id)
    return SuccessResponse(
        message="Agent retrieved successfully",
        data=agent,
    )


@router.get(
    "/{id}/properties",
    response_model=PaginatedResponse[PropertyResponse],
    summary="Get properties of an agent",
    description="Retrieve active public properties listed by an agent.",
)
async def get_agent_properties(
    id: int,
    controller: AgentController = Depends(get_controller),
    status_filter: str | None = Query("ACTIVE", alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await controller.get_agent_properties(
        agent_id=id,
        status=status_filter,
        page=page,
        page_size=page_size,
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
