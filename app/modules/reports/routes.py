from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.reports.controller import ReportController
from app.modules.reports.schemas import ReportCreate, ReportResponse
from app.modules.users.models import User

router = APIRouter(prefix="/reports", tags=["reports"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportController:
    return ReportController(db)


@router.post(
    "",
    response_model=SuccessResponse[ReportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a report",
    description="Submit a complaint/report regarding a property, agent, builder, or user.",
)
async def create_report(
    body: ReportCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: ReportController = Depends(get_controller),
):
    report = await controller.create_report(reporter_id=current_user.id, data=body)
    return SuccessResponse(
        message="Report submitted successfully",
        data=report,
    )


@router.get(
    "/my",
    response_model=SuccessResponse[list[ReportResponse]],
    summary="Get my submitted reports",
    description="Retrieve all reports submitted by the authenticated user.",
)
async def get_my_reports(
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: ReportController = Depends(get_controller),
):
    reports = await controller.get_my_reports(reporter_id=current_user.id)
    return SuccessResponse(
        message="User reports retrieved successfully",
        data=reports,
    )
