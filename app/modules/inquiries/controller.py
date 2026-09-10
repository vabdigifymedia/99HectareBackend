from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inquiries.schemas import InquiryCreate, InquiryUpdate
from app.modules.inquiries.service import InquiryService


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

    async def getInquiry(self, inquiry_id: int):
        return await self.service.get_inquiry(inquiry_id)

    async def getMyInquiries(self, user_id: int):
        return await self.service.get_my_inquiries(user_id)

    async def getAgentInquiries(self, agent_id: int):
        return await self.service.get_agent_inquiries(agent_id)

    async def getBuilderInquiries(self, builder_id: int):
        return await self.service.get_builder_inquiries(builder_id)

    async def getAllInquiries(self):
        return await self.service.get_all_inquiries()

    async def updateInquiry(self, inquiry_id: int, data: InquiryUpdate):
        return await self.service.update_inquiry(inquiry_id, data)

    async def deleteInquiry(self, inquiry_id: int):
        return await self.service.delete_inquiry(inquiry_id)

    async def inquiryStaus(self, inquiry_id: int, status: str | None = None):
        return await self.service.get_inquiry_status(inquiry_id)