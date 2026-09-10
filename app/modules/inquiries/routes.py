from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.modules.inquiries.controller import InquiryController
from app.modules.inquiries.schemas import (
    InquiryCreate,
    InquiryResponse,
    InquiryUpdate,
)
from app.modules.inquiries.service import InquiryService
from app.modules.users.models import User

router = APIRouter(prefix="/inquiries", tags=["inquiries"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InquiryController:
    return InquiryController(service=InquiryService(db))


# ── Create Inquiry ───────────────────────────────────────────────────


@router.post(
    "",
    response_model=SuccessResponse[InquiryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create inquiry",
    description="Submit an inquiry for a property, project, agent, or builder.",
)
async def create_inquiry(
    body: InquiryCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    inquiry = await controller.createInquiry(user_id=current_user.id, data=body)
    return SuccessResponse(
        message="Inquiry submitted successfully",
        data=inquiry,
    )


# ── Get My Inquiries ─────────────────────────────────────────────────


@router.get(
    "/my",
    response_model=SuccessResponse[list[InquiryResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get my inquiries",
    description="Retrieve all inquiries submitted by the current authenticated user.",
)
async def get_my_inquiries(
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    inquiries = await controller.getMyInquiries(user_id=current_user.id)
    return SuccessResponse(
        message="User inquiries retrieved successfully",
        data=inquiries,
    )


# ── Get Agent Inquiries ──────────────────────────────────────────────


@router.get(
    "/agent/{agent_id}",
    response_model=SuccessResponse[list[InquiryResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get inquiries for an agent",
    description="Retrieve all inquiries received by a specific agent.",
)
async def get_agent_inquiries(
    agent_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    inquiries = await controller.getAgentInquiries(agent_id=agent_id)
    return SuccessResponse(
        message="Agent inquiries retrieved successfully",
        data=inquiries,
    )


# ── Get Builder Inquiries ────────────────────────────────────────────


@router.get(
    "/builder/{builder_id}",
    response_model=SuccessResponse[list[InquiryResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get inquiries for a builder",
    description="Retrieve all inquiries received by a specific builder.",
)
async def get_builder_inquiries(
    builder_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    inquiries = await controller.getBuilderInquiries(builder_id=builder_id)
    return SuccessResponse(
        message="Builder inquiries retrieved successfully",
        data=inquiries,
    )


# ── Get All Inquiries ────────────────────────────────────────────────


@router.get(
    "",
    response_model=SuccessResponse[list[InquiryResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get all inquiries",
    description="Retrieve all inquiries in the system.",
)
async def get_all_inquiries(
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    inquiries = await controller.getAllInquiries()
    return SuccessResponse(
        message="All inquiries retrieved successfully",
        data=inquiries,
    )


# ── Get Inquiry by ID ────────────────────────────────────────────────


@router.get(
    "/{id}",
    response_model=SuccessResponse[InquiryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get inquiry by ID",
    description="Retrieve details of a specific inquiry by its ID.",
)
async def get_inquiry(
    id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    inquiry = await controller.getInquiry(inquiry_id=id)
    if not inquiry:
        raise NotFoundException(f"Inquiry with ID {id} not found")

    return SuccessResponse(
        message="Inquiry retrieved successfully",
        data=inquiry,
    )


# ── Get Inquiry Status ───────────────────────────────────────────────


@router.get(
    "/{id}/status",
    response_model=SuccessResponse[str],
    status_code=status.HTTP_200_OK,
    summary="Get inquiry status",
    description="Retrieve the current status of an inquiry.",
)
async def get_inquiry_status(
    id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    status_val = await controller.inquiryStaus(inquiry_id=id)
    if status_val is None:
        raise NotFoundException(f"Inquiry with ID {id} not found")

    return SuccessResponse(
        message="Inquiry status retrieved successfully",
        data=status_val,
    )


# ── Update Inquiry ───────────────────────────────────────────────────


@router.patch(
    "/{id}",
    response_model=SuccessResponse[InquiryResponse],
    status_code=status.HTTP_200_OK,
    summary="Update inquiry",
    description="Update the status or message of an inquiry.",
)
async def update_inquiry(
    id: int,
    body: InquiryUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    updated = await controller.updateInquiry(inquiry_id=id, data=body)
    if not updated:
        raise NotFoundException(f"Inquiry with ID {id} not found")

    return SuccessResponse(
        message="Inquiry updated successfully",
        data=updated,
    )


# ── Delete Inquiry ───────────────────────────────────────────────────


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete inquiry",
    description="Delete an inquiry by its ID.",
)
async def delete_inquiry(
    id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    controller: InquiryController = Depends(get_controller),
):
    deleted = await controller.deleteInquiry(inquiry_id=id)
    if not deleted:
        raise NotFoundException(f"Inquiry with ID {id} not found")

    return SuccessResponse(
        message="Inquiry deleted successfully",
    )