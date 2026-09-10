from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inquiries.models import Inquiry
from app.modules.inquiries.schemas import InquiryCreate, InquiryUpdate
from app.modules.inquiries.repository import InquiryRepository


class InquiryService:

    def __init__(self, db: AsyncSession):
        self.repository = InquiryRepository(db)

    async def create_inquiry(
        self,
        user_id: int,
        data: InquiryCreate,
    ) -> Inquiry:

        # Business validation can be added here later.
        # Example:
        # - property exists
        # - project exists
        # - agent belongs to property
        # - builder belongs to project

        inquiry = await self.repository.create(
            user_id=user_id,
            data=data,
        )

        return inquiry

    async def get_inquiry(
        self,
        inquiry_id: int,
    ) -> Inquiry | None:

        return await self.repository.get_by_id(inquiry_id)

    async def get_my_inquiries(
        self,
        user_id: int,
    ) -> list[Inquiry]:

        return await self.repository.get_by_user(user_id)

    async def get_agent_inquiries(
        self,
        agent_id: int,
    ) -> list[Inquiry]:

        return await self.repository.get_by_agent(agent_id)

    async def get_builder_inquiries(
        self,
        builder_id: int,
    ) -> list[Inquiry]:

        return await self.repository.get_by_builder(builder_id)

    async def get_all_inquiries(self) -> list[Inquiry]:

        return await self.repository.get_all()

    async def update_inquiry(
        self,
        inquiry_id: int,
        data: InquiryUpdate,
    ) -> Inquiry | None:

        inquiry = await self.repository.get_by_id(inquiry_id)

        if inquiry is None:
            return None

        return await self.repository.update(
            inquiry=inquiry,
            data=data,
        )

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