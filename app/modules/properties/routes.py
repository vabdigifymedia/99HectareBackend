from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginatedResponse
from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.amenities.schemas import AmenityResponse
from app.modules.media.schemas import PropertyMediaResponse
from app.modules.properties.controller import PropertyController
from app.modules.properties.schemas import (
    PropertyAmenitiesAssignRequest,
    PropertyCreate,
    PropertyDetailResponse,
    PropertyMediaCreateInput,
    PropertyResponse,
    PropertyUpdate,
)
from app.modules.users.models import User

router = APIRouter(prefix="/properties", tags=["properties"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PropertyController:
    return PropertyController(db)


# ── Create Property ───────────────────────────────────────────────────


@router.post(
    "",
    response_model=SuccessResponse[PropertyDetailResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new property listing",
    description=(
        "Create a property listing supporting 99acres flows:\n"
        "- USER Flow: Individual owner listing directly linked to owner_id.\n"
        "- AGENT Flow: Broker listing linked to agent_id and optional owner_id.\n"
        "- BUILDER Flow: Builder listing linked to builder_id and validated project_id.\n"
        "- ADMIN Flow: Full administrative assignment."
    ),
)
async def create_property(
    body: PropertyCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: PropertyController = Depends(get_controller),
):
    prop = await controller.create_property(current_user=current_user, data=body)
    return SuccessResponse(
        message="Property created successfully",
        data=prop,
    )


# ── List / Search Properties ──────────────────────────────────────────


@router.get(
    "",
    response_model=PaginatedResponse[PropertyResponse],
    summary="List and search properties with filters",
    description="Search and filter properties with 99acres-style parameters.",
)
async def list_properties(
    controller: PropertyController = Depends(get_controller),
    search: str | None = Query(
        None,
        description="Search in title, description, address, landmark",
    ),
    property_type: str | None = Query(None, description="e.g. apartment, villa, plot"),
    listing_type: str | None = Query(None, description="e.g. SALE, RENT"),
    property_status: str | None = Query(
        None, alias="status", description="e.g. ACTIVE, DRAFT, SOLD"
    ),
    city_id: int | None = Query(None),
    locality_id: int | None = Query(None),
    state_id: int | None = Query(None),
    sub_locality_id: int | None = Query(None),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    bedrooms: int | None = Query(None, ge=0),
    bathrooms: int | None = Query(None, ge=0),
    furnishing_status: str | None = Query(None),
    builder_id: int | None = Query(None),
    project_id: int | None = Query(None),
    agent_id: int | None = Query(None),
    owner_id: int | None = Query(None),
    is_featured: bool | None = Query(None),
    is_verified: bool | None = Query(None),
    sort_by: str = Query(
        "newest",
        pattern="^(newest|price_asc|price_desc|area_asc|area_desc)$",
        description="Sort ordering",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    filters = {
        "search": search,
        "property_type": property_type,
        "listing_type": listing_type,
        "status": property_status,
        "city_id": city_id,
        "locality_id": locality_id,
        "state_id": state_id,
        "sub_locality_id": sub_locality_id,
        "min_price": min_price,
        "max_price": max_price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "furnishing_status": furnishing_status,
        "builder_id": builder_id,
        "project_id": project_id,
        "agent_id": agent_id,
        "owner_id": owner_id,
        "is_featured": is_featured,
        "is_verified": is_verified,
    }
    items, total = await controller.list_properties(
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


# ── Get Property By ID ────────────────────────────────────────────────


@router.get(
    "/{id}",
    response_model=SuccessResponse[PropertyDetailResponse],
    summary="Get property details by ID",
    description="Retrieve full property details including media, amenities, and owner/agent/project summaries.",
)
async def get_property(
    id: int,
    controller: PropertyController = Depends(get_controller),
):
    prop = await controller.get_property(property_id=id)
    return SuccessResponse(
        message="Property retrieved successfully",
        data=prop,
    )


# ── Update Property ───────────────────────────────────────────────────


@router.put(
    "/{id}",
    response_model=SuccessResponse[PropertyDetailResponse],
    summary="Update an existing property",
    description="Update property details. Authorized for owner, listing agent, builder, or admin.",
)
async def update_property(
    id: int,
    body: PropertyUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: PropertyController = Depends(get_controller),
):
    updated = await controller.update_property(
        property_id=id, current_user=current_user, data=body
    )
    return SuccessResponse(
        message="Property updated successfully",
        data=updated,
    )


# ── Delete Property ───────────────────────────────────────────────────


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    summary="Delete a property",
    description="Delete property listing. Authorized for owner, listing agent, builder, or admin.",
)
async def delete_property(
    id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: PropertyController = Depends(get_controller),
):
    await controller.delete_property(property_id=id, current_user=current_user)
    return SuccessResponse(message="Property deleted successfully")


# ── Property Media ────────────────────────────────────────────────────


@router.post(
    "/{id}/media",
    response_model=SuccessResponse[PropertyMediaResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add media to property",
    description="Attach an image, video, floorplan, or brochure to the property.",
)
async def add_property_media(
    id: int,
    body: PropertyMediaCreateInput,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: PropertyController = Depends(get_controller),
):
    media = await controller.add_media(
        property_id=id, current_user=current_user, data=body
    )
    return SuccessResponse(
        message="Media added successfully",
        data=media,
    )


# ── Property Amenities ────────────────────────────────────────────────


@router.post(
    "/{id}/amenities",
    response_model=SuccessResponse[list[AmenityResponse]],
    summary="Assign amenities to property",
    description="Associate a list of amenity IDs with the property.",
)
async def assign_property_amenities(
    id: int,
    body: PropertyAmenitiesAssignRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: PropertyController = Depends(get_controller),
):
    amenities = await controller.assign_amenities(
        property_id=id,
        current_user=current_user,
        amenity_ids=body.amenity_ids,
    )
    return SuccessResponse(
        message="Amenities updated successfully",
        data=amenities,
    )
