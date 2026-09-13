from typing import Annotated

from fastapi import APIRouter , Depends , status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.visits.controller import VisitController
from app.modules.visits.schemas import (
    VisitCreate,
    VisitListResponse,
    VisitResponse,
    VisitStatusUpdate,
    VisitUpdate
)
from app.modules.visits.service import VisitService
from app.modules.users.models import User

router = APIRouter(prefix="/visits" , tags=["visits"])

def get_controller(
    db: Annotated[AsyncSession , Depends(get_db)]
) -> VisitController:
    return VisitController(db)

@router.post(
    "",
    response_model=SuccessResponse[VisitResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new visit",
    description="Submit a request to schedule a visit for a property or unit. This will be forwarded to the agent or builder for confirmation.",
)
async def create_visit(
    body: VisitCreate,
    current_user: Annotated[User , Depends(get_current_active_user)],
    controller: VisitController = Depends(get_controller),
):
    return await controller.create_visit(user_id=current_user.id , data=body)

@router.get(
    "/{id}",
    response_model=SuccessResponse[VisitResponse],
    status_code=status.HTTP_200_OK,
    summary="Get visit by ID",
    description="Retrieve the details of a specific visit using its ID.",
)
async def get_visit_by_id(
    id: int,
    current_user: Annotated[User , Depends(get_current_active_user)],
    controller: VisitController = Depends(get_controller),
):
    visit = await controller.get_visit_by_id(id)
    if not visit:
        raise NotFoundException(f"Visit with ID {id} not found")
    return SuccessResponse(
        message="Visit retrieved successfully",
        data=visit,
    )

@router.get(
    "/user/{user_id}",
    response_model=SuccessResponse[list[VisitResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get user's visits",
    description="Retrieve all visits scheduled by or for a specific user.",
)
async def get_visits_by_user(
    user_id: int,
    current_user: Annotated[User , Depends(get_current_active_user)],
    controller: VisitController = Depends(get_controller),
):
    return await controller.get_visits_by_user(user_id)

@router.get(
    "/agent/{agent_id}",
    response_model=SuccessResponse[VisitListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get agent's Visits",
    description="Retrieve all visits scheduled by or for a speacific agent "
)
async def get_visits_by_agent(
    agent_id:int,
    current_user:Annotated[User , Depends(get_current_active_user)],
    controller:VisitController = Depends(get_controller),
):
    return await controller.get_visits_by_agent(agent_id)

@router.patch(
    "/{id}/status",
    response_model=SuccessResponse[VisitResponse],
    status_code=status.HTTP_200_OK,
    summary="Update visit status",
    description="Update the status of a visit (e.g., confirmed, cancelled, completed). This should be used by agents or admins.",
)
async def update_visit_status(
    id: int,
    status: VisitStatusUpdate,
    current_user: Annotated[User , Depends(get_current_active_user)],
    controller:VisitController = Depends(get_controller),
):
    return await controller.update_visit_status(id , status , current_user)

@router.delete(
    "/{id}",
    response_model=SuccessResponse[str],
    status_code=status.HTTP_200_OK,
    summary="Delete visit",
    description="Delete a visit request. This can only be done by the user who created the visit.",
)
async def delete_visit(
    id: int,
    current_user: Annotated[User , Depends(get_current_active_user)],
    controller:VisitController = Depends(get_controller),
):
    return await controller.delete_visit(id)
