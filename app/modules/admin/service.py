from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.admin.models import Admin
from app.modules.admin.repository import AdminRepository
from app.modules.agents.models import Agent
from app.modules.agents.repository import AgentRepository
from app.modules.builders.models import Builder
from app.modules.builders.repository import BuilderRepository
from app.modules.inquiries.schemas import (
    InquiryAdminApproveRequest,
    InquiryAdminRejectRequest,
    InquiryResponse,
)
from app.modules.inquiries.service import InquiryService
from app.modules.properties.models import Property
from app.modules.properties.repository import PropertyRepository
from app.modules.reports.models import Report
from app.modules.reports.service import ReportService
from app.modules.users.models import User
from app.modules.users.service import UserService


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdminRepository(db)
        self.user_service = UserService(db)
        self.property_repo = PropertyRepository(db)
        self.agent_repo = AgentRepository(db)
        self.builder_repo = BuilderRepository(db)
        self.report_service = ReportService(db)
        self.inquiry_service = InquiryService(db)

    # ── Users Management ──────────────────────────────────────────────

    async def get_users(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        return await self.user_service.list_users(filters=filters, page=page, page_size=page_size)

    # ── Properties Management ─────────────────────────────────────────

    async def get_properties(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Property], int]:
        offset = (max(1, page) - 1) * page_size
        return await self.property_repo.list_properties(
            filters=filters,
            offset=offset,
            limit=page_size,
            sort_by="newest",
        )

    async def approve_property(
        self,
        admin: Admin,
        property_id: int,
    ) -> Property:
        prop = await self.property_repo.get_by_id(property_id)
        if not prop:
            raise NotFoundException(f"Property with ID {property_id} not found")

        prop.status = "ACTIVE"
        prop.is_verified = True
        prop.is_active = True
        prop.published_at = datetime.now(timezone.utc)

        await self.property_repo.update(prop)
        await self.repo.log_action(
            admin_id=admin.id,
            action="APPROVE_PROPERTY",
            entity_type="Property",
            entity_id=property_id,
            description="Property approved and published by admin",
        )
        await self.db.commit()

        detailed = await self.property_repo.get_by_id_detailed(property_id)
        return detailed or prop

    async def reject_property(
        self,
        admin: Admin,
        property_id: int,
        reason: str | None = None,
    ) -> Property:
        prop = await self.property_repo.get_by_id(property_id)
        if not prop:
            raise NotFoundException(f"Property with ID {property_id} not found")

        prop.status = "REJECTED"
        prop.is_verified = False
        prop.is_active = False

        await self.property_repo.update(prop)
        await self.repo.log_action(
            admin_id=admin.id,
            action="REJECT_PROPERTY",
            entity_type="Property",
            entity_id=property_id,
            description=reason or "Property rejected by admin",
        )
        await self.db.commit()

        detailed = await self.property_repo.get_by_id_detailed(property_id)
        return detailed or prop

    # ── Agents & Builders Verification ────────────────────────────────

    async def verify_agent(
        self,
        admin: Admin,
        agent_id: int,
        status: str = "VERIFIED",
    ) -> Agent:
        agent = await self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundException(f"Agent with ID {agent_id} not found")

        agent.verification_status = status
        agent.is_active = True
        if agent.user:
            agent.user.is_verified = True

        await self.agent_repo.update(agent)
        await self.repo.log_action(
            admin_id=admin.id,
            action="VERIFY_AGENT",
            entity_type="Agent",
            entity_id=agent_id,
            description=f"Agent verification status set to {status}",
        )
        await self.db.commit()
        return agent

    async def verify_builder(
        self,
        admin: Admin,
        builder_id: int,
        status: str = "VERIFIED",
    ) -> Builder:
        builder = await self.builder_repo.get_by_id(builder_id)
        if not builder:
            raise NotFoundException(f"Builder with ID {builder_id} not found")

        builder.verification_status = status
        builder.is_active = True
        if builder.user:
            builder.user.is_verified = True

        await self.builder_repo.update(builder)
        await self.repo.log_action(
            admin_id=admin.id,
            action="VERIFY_BUILDER",
            entity_type="Builder",
            entity_id=builder_id,
            description=f"Builder verification status set to {status}",
        )
        await self.db.commit()
        return builder

    # ── Reports Management ────────────────────────────────────────────

    async def get_reports(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Report], int]:
        return await self.report_service.list_reports(filters=filters, page=page, page_size=page_size)

    async def resolve_report(
        self,
        admin: Admin,
        report_id: int,
        admin_notes: str | None = None,
    ) -> Report:
        resolved = await self.report_service.resolve_report(
            report_id=report_id,
            admin_id=admin.id,
            admin_notes=admin_notes,
        )
        await self.repo.log_action(
            admin_id=admin.id,
            action="RESOLVE_REPORT",
            entity_type="Report",
            entity_id=report_id,
            description=admin_notes or "Report marked as resolved",
        )
        await self.db.commit()
        return resolved

    # ── Inquiries & Middle-Payment Management ─────────────────────────

    async def get_inquiries(
        self,
        status: str | None = None,
        is_admin_approved: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[InquiryResponse], int]:
        return await self.inquiry_service.list_admin_inquiries(
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
        approved = await self.inquiry_service.approve_inquiry(
            inquiry_id=inquiry_id,
            data=InquiryAdminApproveRequest(admin_notes=admin_notes),
        )
        if not approved:
            raise NotFoundException(f"Inquiry with ID {inquiry_id} not found")

        await self.repo.log_action(
            admin_id=admin.id,
            action="APPROVE_INQUIRY",
            entity_type="Inquiry",
            entity_id=inquiry_id,
            description=admin_notes or "Inquiry approved; lead unlocked for agent/owner",
        )
        await self.db.commit()
        return approved

    async def reject_inquiry(
        self,
        admin: Admin,
        inquiry_id: int,
        reason: str | None = None,
    ) -> InquiryResponse:
        rejected = await self.inquiry_service.reject_inquiry(
            inquiry_id=inquiry_id,
            data=InquiryAdminRejectRequest(reason=reason),
        )
        if not rejected:
            raise NotFoundException(f"Inquiry with ID {inquiry_id} not found")

        await self.repo.log_action(
            admin_id=admin.id,
            action="REJECT_INQUIRY",
            entity_type="Inquiry",
            entity_id=inquiry_id,
            description=reason or "Inquiry rejected by admin",
        )
        await self.db.commit()
        return rejected
