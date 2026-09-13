from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.modules.locations.controller import LocationController
from app.modules.locations.schemas import (
    CityResponse,
    CountryResponse,
    LocalityResponse,
    StateResponse,
    SubLocalityResponse,
)

router = APIRouter(prefix="/locations", tags=["locations"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LocationController:
    return LocationController(db)


@router.get(
    "/countries",
    response_model=SuccessResponse[list[CountryResponse]],
    summary="List all countries",
)
async def list_countries(
    controller: LocationController = Depends(get_controller),
):
    countries = await controller.get_countries()
    return SuccessResponse(data=countries)


@router.get(
    "/states",
    response_model=SuccessResponse[list[StateResponse]],
    summary="List states",
)
async def list_states(
    country_id: int | None = Query(None, description="Filter states by country ID"),
    controller: LocationController = Depends(get_controller),
):
    states = await controller.get_states(country_id=country_id)
    return SuccessResponse(data=states)


@router.get(
    "/cities",
    response_model=SuccessResponse[list[CityResponse]],
    summary="List cities",
)
async def list_cities(
    state_id: int | None = Query(None, description="Filter cities by state ID"),
    search: str | None = Query(None, description="Search cities by name"),
    controller: LocationController = Depends(get_controller),
):
    cities = await controller.get_cities(state_id=state_id, search=search)
    return SuccessResponse(data=cities)


@router.get(
    "/localities",
    response_model=SuccessResponse[list[LocalityResponse]],
    summary="List localities",
)
async def list_localities(
    city_id: int | None = Query(None, description="Filter localities by city ID"),
    search: str | None = Query(None, description="Search localities by name"),
    controller: LocationController = Depends(get_controller),
):
    localities = await controller.get_localities(city_id=city_id, search=search)
    return SuccessResponse(data=localities)


@router.get(
    "/sub-localities",
    response_model=SuccessResponse[list[SubLocalityResponse]],
    summary="List sub-localities",
)
async def list_sub_localities(
    locality_id: int | None = Query(
        None, description="Filter sub-localities by locality ID"
    ),
    search: str | None = Query(None, description="Search sub-localities by name"),
    controller: LocationController = Depends(get_controller),
):
    sub_localities = await controller.get_sub_localities(
        locality_id=locality_id, search=search
    )
    return SuccessResponse(data=sub_localities)
