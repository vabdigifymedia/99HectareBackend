from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.users.controller import UserController
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserController:
    return UserController(db)


@router.get(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="Get current user profile",
    description="Retrieve the profile of the currently logged-in user.",
)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return SuccessResponse(
        message="Profile retrieved successfully",
        data=current_user,
    )


@router.put(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="Update current user profile",
    description="Update profile information of the current logged-in user.",
)
async def update_my_profile(
    body: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: UserController = Depends(get_controller),
):
    updated = await controller.update_user(user_id=current_user.id, data=body)
    return SuccessResponse(
        message="Profile updated successfully",
        data=updated,
    )


@router.get(
    "/{id}",
    response_model=SuccessResponse[UserResponse],
    summary="Get user by ID",
    description="Retrieve public profile of a user by ID.",
)
async def get_user_by_id(
    id: int,
    controller: UserController = Depends(get_controller),
):
    user = await controller.get_by_id(user_id=id)
    return SuccessResponse(
        message="User retrieved successfully",
        data=user,
    )
