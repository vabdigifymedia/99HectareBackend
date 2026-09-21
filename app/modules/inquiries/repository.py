from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inquiries.models import Inquiry
from app.modules.inquiries.schemas import InquiryCreate, InquiryUpdate
from app.modules.properties.models import Property
from app.modules.users.models import User


class InquiryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        data: InquiryCreate,
    ) -> Inquiry:
        agent_id = data.agent_id
        builder_id = data.builder_id
        project_id = data.project_id

        # Auto-resolve agent/builder/project from property if not explicitly set
        if data.property_id:
            prop_res = await self.db.execute(
                select(Property).where(Property.id == data.property_id)
            )
            prop = prop_res.scalar_one_or_none()
            if prop:
                if not agent_id and prop.agent_id:
                    agent_id = prop.agent_id
                if not builder_id and prop.builder_id:
                    builder_id = prop.builder_id
                if not project_id and prop.project_id:
                    project_id = prop.project_id

        inquiry = Inquiry(
            user_id=user_id,
            property_id=data.property_id,
            project_id=project_id,
            agent_id=agent_id,
            builder_id=builder_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            message=data.message,
            source=data.source,
            is_admin_approved=False,
            status="NEW",
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
            .options(
                selectinload(Inquiry.property),
                selectinload(Inquiry.agent),
                selectinload(Inquiry.user),
            )
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

    async def get_received_for_user(
        self,
        user: User,
    ) -> list[Inquiry]:
        """Fetch inquiries received by the user as an agent or property owner."""
        conditions = []

        # 1. If user is an agent, include inquiries directed to their agent profile
        if user.agent_profile:
            conditions.append(Inquiry.agent_id == user.agent_profile.id)

        # 2. If user is a builder, include inquiries directed to their builder profile
        if user.builder_profile:
            conditions.append(Inquiry.builder_id == user.builder_profile.id)

        # 3. Include inquiries on properties owned by this user
        query = (
            select(Inquiry)
            .outerjoin(Property, Inquiry.property_id == Property.id)
            .options(selectinload(Inquiry.property))
        )

        owner_condition = Property.owner_id == user.id
        if conditions:
            query = query.where(or_(owner_condition, *conditions))
        else:
            query = query.where(owner_condition)

        query = query.order_by(Inquiry.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self) -> list[Inquiry]:
        result = await self.db.execute(
            select(Inquiry)
            .options(selectinload(Inquiry.property))
            .order_by(Inquiry.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_admin(
        self,
        status: str | None = None,
        is_admin_approved: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Inquiry], int]:
        query = select(Inquiry).options(
            selectinload(Inquiry.property),
            selectinload(Inquiry.agent),
            selectinload(Inquiry.user),
        )

        if status:
            query = query.where(Inquiry.status == status)
        if is_admin_approved is not None:
            query = query.where(Inquiry.is_admin_approved == is_admin_approved)

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(Inquiry.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        return items, total

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

    async def approve_inquiry(
        self,
        inquiry: Inquiry,
        admin_notes: str | None = None,
    ) -> Inquiry:
        inquiry.is_admin_approved = True
        inquiry.status = "APPROVED"
        if admin_notes is not None:
            inquiry.admin_notes = admin_notes
        await self.db.commit()
        await self.db.refresh(inquiry)
        return inquiry

    async def reject_inquiry(
        self,
        inquiry: Inquiry,
        admin_notes: str | None = None,
    ) -> Inquiry:
        inquiry.is_admin_approved = False
        inquiry.status = "REJECTED"
        if admin_notes is not None:
            inquiry.admin_notes = admin_notes
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
        result = await self.db.execute(select(func.count(Inquiry.id)))
        return result.scalar_one()

    async def get_status(
        self,
        inquiry_id: int,
    ) -> str | None:
        result = await self.db.execute(
            select(Inquiry.status).where(Inquiry.id == inquiry_id)
        )
        return result.scalar_one_or_none()