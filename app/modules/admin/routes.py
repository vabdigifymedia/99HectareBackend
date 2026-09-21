from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import PaginatedResponse
from app.common.responses import SuccessResponse
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.admin.controller import AdminController
from app.modules.admin.models import Admin
from app.modules.admin.schemas import (
    InquiryAdminActionRequest,
    PropertyRejectRequest,
    ReportResolveRequest,
    VerificationUpdateRequest,
)
from app.modules.agents.schemas import AgentResponse
from app.modules.builders.schemas import BuilderResponse
from app.modules.inquiries.schemas import InquiryResponse
from app.modules.properties.schemas import PropertyDetailResponse, PropertyResponse
from app.modules.reports.schemas import ReportResponse
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def get_controller(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminController:
    return AdminController(db)


# ── GET /admin/users ──────────────────────────────────────────────────


@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse],
    summary="Admin list all users",
    description="Retrieve all registered users with role/status filters and pagination.",
)
async def admin_list_users(
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    role: str | None = Query(None, description="Filter by user role (buyer, agent, builder, admin)"),
    is_active: bool | None = Query(None),
    is_verified: bool | None = Query(None),
    search: str | None = Query(None, description="Search name, email, or phone"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    filters = {
        "role": role,
        "is_active": is_active,
        "is_verified": is_verified,
        "search": search,
    }
    items, total = await controller.get_users(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ── GET /admin/properties ─────────────────────────────────────────────


@router.get(
    "/properties",
    response_model=PaginatedResponse[PropertyResponse],
    summary="Admin list all properties",
    description="Retrieve all properties across all statuses (draft, pending, active, rejected, sold).",
)
async def admin_list_properties(
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    status_filter: str | None = Query(None, alias="status"),
    property_type: str | None = Query(None),
    listing_type: str | None = Query(None),
    agent_id: int | None = Query(None),
    builder_id: int | None = Query(None),
    owner_id: int | None = Query(None),
    is_verified: bool | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    filters = {
        "status": status_filter,
        "property_type": property_type,
        "listing_type": listing_type,
        "agent_id": agent_id,
        "builder_id": builder_id,
        "owner_id": owner_id,
        "is_verified": is_verified,
        "search": search,
    }
    items, total = await controller.get_properties(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ── PATCH /admin/properties/{id}/approve ──────────────────────────────


@router.patch(
    "/properties/{id}/approve",
    response_model=SuccessResponse[PropertyDetailResponse],
    summary="Approve property listing",
    description="Admin approves and publishes a property listing.",
)
async def admin_approve_property(
    id: int,
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
):
    prop = await controller.approve_property(admin=current_admin, property_id=id)
    return SuccessResponse(
        message="Property approved and published successfully",
        data=prop,
    )


# ── PATCH /admin/properties/{id}/reject ───────────────────────────────


@router.patch(
    "/properties/{id}/reject",
    response_model=SuccessResponse[PropertyDetailResponse],
    summary="Reject property listing",
    description="Admin rejects a property listing.",
)
async def admin_reject_property(
    id: int,
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    body: PropertyRejectRequest | None = None,
):
    reason = body.reason if body else None
    prop = await controller.reject_property(admin=current_admin, property_id=id, reason=reason)
    return SuccessResponse(
        message="Property rejected successfully",
        data=prop,
    )


# ── PATCH /admin/agents/{id}/verify ───────────────────────────────────


@router.patch(
    "/agents/{id}/verify",
    response_model=SuccessResponse[AgentResponse],
    summary="Verify agent profile",
    description="Admin verifies an agent profile.",
)
async def admin_verify_agent(
    id: int,
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    body: VerificationUpdateRequest | None = None,
):
    status_val = body.verification_status if body else "VERIFIED"
    agent = await controller.verify_agent(admin=current_admin, agent_id=id, status=status_val)
    return SuccessResponse(
        message="Agent verified successfully",
        data=agent,
    )


# ── PATCH /admin/builders/{id}/verify ─────────────────────────────────


@router.patch(
    "/builders/{id}/verify",
    response_model=SuccessResponse[BuilderResponse],
    summary="Verify builder profile",
    description="Admin verifies a builder profile.",
)
async def admin_verify_builder(
    id: int,
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    body: VerificationUpdateRequest | None = None,
):
    status_val = body.verification_status if body else "VERIFIED"
    builder = await controller.verify_builder(admin=current_admin, builder_id=id, status=status_val)
    return SuccessResponse(
        message="Builder verified successfully",
        data=builder,
    )


# ── GET /admin/reports ────────────────────────────────────────────────


@router.get(
    "/reports",
    response_model=PaginatedResponse[ReportResponse],
    summary="Admin list reports",
    description="Retrieve all submitted complaints and reports.",
)
async def admin_list_reports(
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    status_filter: str | None = Query(None, alias="status"),
    reason: str | None = Query(None),
    property_id: int | None = Query(None),
    agent_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    filters = {
        "status": status_filter,
        "reason": reason,
        "property_id": property_id,
        "agent_id": agent_id,
    }
    items, total = await controller.get_reports(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ── PATCH /admin/reports/{id}/resolve ─────────────────────────────────


@router.patch(
    "/reports/{id}/resolve",
    response_model=SuccessResponse[ReportResponse],
    summary="Resolve report",
    description="Admin marks a report as resolved with optional resolution notes.",
)
async def admin_resolve_report(
    id: int,
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    body: ReportResolveRequest | None = None,
):
    notes = body.admin_notes if body else None
    resolved = await controller.resolve_report(admin=current_admin, report_id=id, admin_notes=notes)
    return SuccessResponse(
        message="Report resolved successfully",
        data=resolved,
    )


# ── Inquiries Gatekeeper & Middle-Payment Routes ──────────────────────


@router.get(
    "/inquiries",
    response_model=PaginatedResponse[InquiryResponse],
    summary="Admin view all inquiries (leads)",
    description=(
        "Admin panel view of all user leads/inquiries with full contact info and payment/approval status."
    ),
)
async def admin_list_inquiries(
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    status_filter: str | None = Query(None, alias="status"),
    is_admin_approved: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await controller.get_inquiries(
        status=status_filter,
        is_admin_approved=is_admin_approved,
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


@router.patch(
    "/inquiries/{id}/approve",
    response_model=SuccessResponse[InquiryResponse],
    summary="Admin approve inquiry / confirm middle payment",
    description=(
        "Confirms middle payment or manual agreement, unlocking full buyer contact details for the agent/owner."
    ),
)
async def admin_approve_inquiry(
    id: int,
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    body: InquiryAdminActionRequest | None = None,
):
    notes = body.admin_notes if body else None
    approved = await controller.approve_inquiry(admin=current_admin, inquiry_id=id, admin_notes=notes)
    return SuccessResponse(
        message="Inquiry approved successfully. Buyer contact details are now unlocked for the recipient.",
        data=approved,
    )


@router.patch(
    "/inquiries/{id}/reject",
    response_model=SuccessResponse[InquiryResponse],
    summary="Admin reject inquiry",
    description="Rejects lead inquiry.",
)
async def admin_reject_inquiry(
    id: int,
    current_admin: Annotated[Admin, Depends(get_current_admin)],
    controller: AdminController = Depends(get_controller),
    body: InquiryAdminActionRequest | None = None,
):
    reason = body.admin_notes if body else None
    rejected = await controller.reject_inquiry(admin=current_admin, inquiry_id=id, reason=reason)
    return SuccessResponse(
        message="Inquiry rejected by admin",
        data=rejected,
    )
