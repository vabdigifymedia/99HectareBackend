from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inquiries.schemas import (
    InquiryAdminApproveRequest,
    InquiryAdminRejectRequest,
    InquiryCreate,
    InquiryUpdate,
)
from app.modules.inquiries.service import InquiryService
from app.modules.users.models import User


class InquiryController:
    def __init__(
        self,
        service: InquiryService | None = None,
        db: AsyncSession | None = None,
    ):
        if service is not None:
            self.service = service
        elif db is not None:
            self.service = InquiryService(db)
        else:
            raise ValueError("Either service or db must be provided")

    async def createInquiry(self, user_id: int, data: InquiryCreate):
        return await self.service.create_inquiry(user_id, data)

    async def getInquiry(self, inquiry_id: int, current_user: User | None = None):
        return await self.service.get_inquiry(inquiry_id, current_user=current_user)

    async def getMyInquiries(self, user_id: int):
        return await self.service.get_my_inquiries(user_id)

    async def getReceivedInquiries(self, current_user: User):
        return await self.service.get_received_inquiries(current_user)

    async def getAgentInquiries(self, agent_id: int, current_user: User | None = None):
        return await self.service.get_agent_inquiries(agent_id, current_user=current_user)

    async def getBuilderInquiries(self, builder_id: int, current_user: User | None = None):
        return await self.service.get_builder_inquiries(builder_id, current_user=current_user)

    async def getAllInquiries(self, current_user: User | None = None):
        return await self.service.get_all_inquiries(current_user=current_user)

    async def listAdminInquiries(
        self,
        status: str | None = None,
        is_admin_approved: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        return await self.service.list_admin_inquiries(
            status=status,
            is_admin_approved=is_admin_approved,
            page=page,
            page_size=page_size,
        )

    async def approveInquiry(self, inquiry_id: int, data: InquiryAdminApproveRequest | None = None):
        return await self.service.approve_inquiry(inquiry_id, data=data)

    async def rejectInquiry(self, inquiry_id: int, data: InquiryAdminRejectRequest | None = None):
        return await self.service.reject_inquiry(inquiry_id, data=data)

    async def updateInquiry(self, inquiry_id: int, data: InquiryUpdate):
        return await self.service.update_inquiry(inquiry_id, data)

    async def deleteInquiry(self, inquiry_id: int):
        return await self.service.delete_inquiry(inquiry_id)

    async def inquiryStaus(self, inquiry_id: int, status: str | None = None):
        return await self.service.get_inquiry_status(inquiry_id)