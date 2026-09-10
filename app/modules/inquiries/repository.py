from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inquiries.models import Inquiry
from app.modules.inquiries.schemas import InquiryCreate, InquiryUpdate


class InquiryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        data: InquiryCreate,
    ) -> Inquiry:

        inquiry = Inquiry(
            user_id=user_id,
            property_id=data.property_id,
            project_id=data.project_id,
            agent_id=data.agent_id,
            builder_id=data.builder_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            message=data.message,
            source=data.source,
        )

        self.db.add(inquiry)

        await self.db.commit()
        await self.db.refresh(inquiry)

        return inquiry

    async def get_by_id(
        self,
        inquiry_id: int,
    ) -> Inquiry | None:

        result = await self.db.execute(
            select(Inquiry)
            .where(Inquiry.id == inquiry_id)
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[Inquiry]:

        result = await self.db.execute(
            select(Inquiry)
            .where(Inquiry.user_id == user_id)
            .order_by(Inquiry.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_agent(
        self,
        agent_id: int,
    ) -> list[Inquiry]:

        result = await self.db.execute(
            select(Inquiry)
            .where(Inquiry.agent_id == agent_id)
            .order_by(Inquiry.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_builder(
        self,
        builder_id: int,
    ) -> list[Inquiry]:

        result = await self.db.execute(
            select(Inquiry)
            .where(Inquiry.builder_id == builder_id)
            .order_by(Inquiry.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_all(self) -> list[Inquiry]:

        result = await self.db.execute(
            select(Inquiry)
            .order_by(Inquiry.created_at.desc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        inquiry: Inquiry,
        data: InquiryUpdate,
    ) -> Inquiry:

        if data.status is not None:
            inquiry.status = data.status

        if data.message is not None:
            inquiry.message = data.message

        await self.db.commit()
        await self.db.refresh(inquiry)

        return inquiry

    async def delete(
        self,
        inquiry: Inquiry,
    ) -> None:

        await self.db.delete(inquiry)
        await self.db.commit()

    async def get_count(self) -> int:

        result = await self.db.execute(
            select(func.count(Inquiry.id))
        )

        return result.scalar_one()

    async def get_status(
        self,
        inquiry_id: int,
    ) -> str | None:

        result = await self.db.execute(
            select(Inquiry.status)
            .where(Inquiry.id == inquiry_id)
        )

        return result.scalar_one_or_none()