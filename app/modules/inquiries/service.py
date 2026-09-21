from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inquiries.models import Inquiry
from app.modules.inquiries.repository import InquiryRepository
from app.modules.inquiries.schemas import (
    InquiryAdminApproveRequest,
    InquiryAdminRejectRequest,
    InquiryCreate,
    InquiryResponse,
    InquiryUpdate,
)
from app.modules.users.models import User


class InquiryService:

    def __init__(self, db: AsyncSession):
        self.repository = InquiryRepository(db)

    @staticmethod
    def _mask_inquiry(inquiry: Inquiry) -> InquiryResponse:
        return InquiryResponse(
            id=inquiry.id,
            user_id=inquiry.user_id,
            property_id=inquiry.property_id,
            project_id=inquiry.project_id,
            agent_id=inquiry.agent_id,
            builder_id=inquiry.builder_id,
            name=f"Lead #{inquiry.id} (Pending Admin Approval)",
            email=None,
            phone=None,
            message="New lead received. Contact details are hidden until admin confirms verification/middle payment.",
            status=inquiry.status,
            source=inquiry.source,
            is_admin_approved=False,
            admin_notes=None,
            created_at=inquiry.created_at,
            updated_at=inquiry.updated_at,
        )

    def format_inquiry_for_user(
        self,
        inquiry: Inquiry,
        current_user: User | None = None,
    ) -> InquiryResponse:
        if current_user and current_user.role == "admin":
            return InquiryResponse.model_validate(inquiry)

        if current_user and inquiry.user_id == current_user.id:
            return InquiryResponse.model_validate(inquiry)

        if inquiry.is_admin_approved:
            return InquiryResponse.model_validate(inquiry)

        return self._mask_inquiry(inquiry)

    async def create_inquiry(
        self,
        user_id: int,
        data: InquiryCreate,
    ) -> InquiryResponse:
        inquiry = await self.repository.create(
            user_id=user_id,
            data=data,
        )
        return InquiryResponse.model_validate(inquiry)

    async def get_inquiry(
        self,
        inquiry_id: int,
        current_user: User | None = None,
    ) -> InquiryResponse | None:
        inquiry = await self.repository.get_by_id(inquiry_id)
        if not inquiry:
            return None
        return self.format_inquiry_for_user(inquiry, current_user)

    async def get_my_inquiries(
        self,
        user_id: int,
    ) -> list[InquiryResponse]:
        inquiries = await self.repository.get_by_user(user_id)
        return [InquiryResponse.model_validate(i) for i in inquiries]

    async def get_received_inquiries(
        self,
        current_user: User,
    ) -> list[InquiryResponse]:
        inquiries = await self.repository.get_received_for_user(current_user)
        return [self.format_inquiry_for_user(i, current_user) for i in inquiries]

    async def get_agent_inquiries(
        self,
        agent_id: int,
        current_user: User | None = None,
    ) -> list[InquiryResponse]:
        inquiries = await self.repository.get_by_agent(agent_id)
        return [self.format_inquiry_for_user(i, current_user) for i in inquiries]

    async def get_builder_inquiries(
        self,
        builder_id: int,
        current_user: User | None = None,
    ) -> list[InquiryResponse]:
        inquiries = await self.repository.get_by_builder(builder_id)
        return [self.format_inquiry_for_user(i, current_user) for i in inquiries]

    async def get_all_inquiries(
        self,
        current_user: User | None = None,
    ) -> list[InquiryResponse]:
        inquiries = await self.repository.get_all()
        return [self.format_inquiry_for_user(i, current_user) for i in inquiries]

    async def list_admin_inquiries(
        self,
        status: str | None = None,
        is_admin_approved: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[InquiryResponse], int]:
        offset = (max(1, page) - 1) * page_size
        items, total = await self.repository.list_admin(
            status=status,
            is_admin_approved=is_admin_approved,
            offset=offset,
            limit=page_size,
        )
        return [InquiryResponse.model_validate(i) for i in items], total

    async def approve_inquiry(
        self,
        inquiry_id: int,
        data: InquiryAdminApproveRequest | None = None,
    ) -> InquiryResponse | None:
        inquiry = await self.repository.get_by_id(inquiry_id)
        if not inquiry:
            return None
        admin_notes = data.admin_notes if data else None
        updated = await self.repository.approve_inquiry(inquiry, admin_notes=admin_notes)
        return InquiryResponse.model_validate(updated)

    async def reject_inquiry(
        self,
        inquiry_id: int,
        data: InquiryAdminRejectRequest | None = None,
    ) -> InquiryResponse | None:
        inquiry = await self.repository.get_by_id(inquiry_id)
        if not inquiry:
            return None
        notes = data.reason if data and data.reason else None
        updated = await self.repository.reject_inquiry(inquiry, admin_notes=notes)
        return InquiryResponse.model_validate(updated)

    async def update_inquiry(
        self,
        inquiry_id: int,
        data: InquiryUpdate,
    ) -> InquiryResponse | None:
        inquiry = await self.repository.get_by_id(inquiry_id)
        if inquiry is None:
            return None
        updated = await self.repository.update(inquiry=inquiry, data=data)
        return InquiryResponse.model_validate(updated)

    async def delete_inquiry(
        self,
        inquiry_id: int,
    ) -> bool:
        inquiry = await self.repository.get_by_id(inquiry_id)
        if inquiry is None:
            return False
        await self.repository.delete(inquiry)
        return True

    async def get_inquiry_status(
        self,
        inquiry_id: int,
    ) -> str | None:
        return await self.repository.get_status(inquiry_id)

    async def get_inquiry_count(self) -> int:
        return await self.repository.get_count()