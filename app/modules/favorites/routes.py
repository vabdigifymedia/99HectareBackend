from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.favorites.controller import FavoriteController
from app.modules.favorites.schemas import FavoriteCreate
from app.modules.properties.models import Property
from app.modules.properties.schemas import PropertyResponse
from app.modules.users.models import User



router = APIRouter(prefix="/favorites", tags=["favorites"])

def get_controller(db: Annotated[AsyncSession, Depends(get_db)]) -> FavoriteController:
    return FavoriteController(db)


@router.get(
    "/{id}",
    response_model=SuccessResponse[PropertyResponse],
    status_code=status.HTTP_200_OK,
    summary="Get favorite by ID",
    description="Retrieve a favorite by its ID",
)
async def get_favorite(
    id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: FavoriteController = Depends(get_controller),
):
    return await controller.get_by_id(current_user=current_user, property_id=id)

@router.delete(
    "/{id}",
    response_model=SuccessResponse[PropertyResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete favorite",
    description="Delete a favorite",
)
async def delete_favorite(
    id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: FavoriteController = Depends(get_controller),
):
    return await controller.delete_favorite(current_user=current_user, property_id=id)

@router.post(
    "/",
    response_model=SuccessResponse[PropertyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create favorite",
    description="Create a new favorite",
)
async def create_favorite(
    data: FavoriteCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: FavoriteController = Depends(get_controller),
):
    return await controller.create_favorite(current_user=current_user, data=data)

@router.get(
    "/",
    response_model=SuccessResponse[list[PropertyResponse]],
    status_code=status.HTTP_200_OK,
    summary="List favorites",
    description="Retrieve a list of favorites",
)
async def list_favorites(
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: FavoriteController = Depends(get_controller),
):
    return await controller.list_favorites(current_user=current_user)
    
@router.get(
    "/count",
    response_model=SuccessResponse[int],
    status_code=status.HTTP_200_OK,
    summary="Get total count of favorites",
    description="Retrieve the total count of favorites for a user",
)
async def get_total_count(
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: FavoriteController = Depends(get_controller),
):
    return await controller.get_total_count(current_user=current_user)


