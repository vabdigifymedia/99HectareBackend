from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.models import Admin
from app.modules.admin.service import AdminService
from app.modules.agents.models import Agent
from app.modules.builders.models import Builder
from app.modules.inquiries.schemas import InquiryResponse
from app.modules.properties.models import Property
from app.modules.reports.models import Report
from app.modules.users.models import User


class AdminController:
    def __init__(self, db: AsyncSession):
        self.service = AdminService(db)

    async def get_users(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        return await self.service.get_users(filters=filters, page=page, page_size=page_size)

    async def get_properties(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Property], int]:
        return await self.service.get_properties(filters=filters, page=page, page_size=page_size)

    async def approve_property(
        self,
        admin: Admin,
        property_id: int,
    ) -> Property:
        return await self.service.approve_property(admin=admin, property_id=property_id)

    async def reject_property(
        self,
        admin: Admin,
        property_id: int,
        reason: str | None = None,
    ) -> Property:
        return await self.service.reject_property(admin=admin, property_id=property_id, reason=reason)

    async def verify_agent(
        self,
        admin: Admin,
        agent_id: int,
        status: str = "VERIFIED",
    ) -> Agent:
        return await self.service.verify_agent(admin=admin, agent_id=agent_id, status=status)

    async def verify_builder(
        self,
        admin: Admin,
        builder_id: int,
        status: str = "VERIFIED",
    ) -> Builder:
        return await self.service.verify_builder(admin=admin, builder_id=builder_id, status=status)

    async def get_reports(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Report], int]:
        return await self.service.get_reports(filters=filters, page=page, page_size=page_size)

    async def resolve_report(
        self,
        admin: Admin,
        report_id: int,
        admin_notes: str | None = None,
    ) -> Report:
        return await self.service.resolve_report(admin=admin, report_id=report_id, admin_notes=admin_notes)

    async def get_inquiries(
        self,
        status: str | None = None,
        is_admin_approved: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[InquiryResponse], int]:
        return await self.service.get_inquiries(
            status=status,
            is_admin_approved=is_admin_approved,
            page=page,
            page_size=page_size,
        )

    async def approve_inquiry(
        self,
        admin: Admin,
        inquiry_id: int,
        admin_notes: str | None = None,
    ) -> InquiryResponse:
        return await self.service.approve_inquiry(admin=admin, inquiry_id=inquiry_id, admin_notes=admin_notes)

    async def reject_inquiry(
        self,
        admin: Admin,
        inquiry_id: int,
        reason: str | None = None,
    ) -> InquiryResponse:
        return await self.service.reject_inquiry(admin=admin, inquiry_id=inquiry_id, reason=reason)
