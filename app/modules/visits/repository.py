from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.properties.models import Property
from app.modules.visits.models import Visit
from app.modules.visits.schemas import VisitCreate


class VisitRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_visit(
        self,
        user_id: int,
        data: VisitCreate,
    ) -> Visit:
        prop_res = await self.db.execute(select(Property).where(Property.id == data.property_id))
        prop = prop_res.scalar_one_or_none()
        agent_id = prop.agent_id if prop else None

        visit = Visit(
            user_id=user_id,
            property_id=data.property_id,
            agent_id=agent_id,
            requested_date=data.requested_date,
            user_notes=data.user_notes,
        )

        self.db.add(visit)

        await self.db.commit()
        await self.db.refresh(visit)

        return visit

    async def get_by_id(
        self,
        visit_id: int,
    ) -> Visit | None:

        result = await self.db.execute(
            select(Visit)
            .where(Visit.id == visit_id)
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[Visit]:

        result = await self.db.execute(
            select(Visit)
            .where(Visit.user_id == user_id)
            .order_by(Visit.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_agent(
        self,
        agent_id: int,
    ) -> list[Visit]:

        result = await self.db.execute(
            select(Visit)
            .where(Visit.agent_id == agent_id)
            .order_by(Visit.created_at.desc())
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        visit: Visit,
        status: str | None = None,
        confirmed_date: datetime | None = None,
        agent_notes: str | None = None,
        cancellation_reason: str | None = None,
    ) -> Visit:

        if status is not None:
            visit.status = status

        if confirmed_date is not None:
            visit.confirmed_date = confirmed_date

        if agent_notes is not None:
            visit.agent_notes = agent_notes

        if cancellation_reason is not None:
            visit.cancellation_reason = cancellation_reason

        await self.db.commit()
        await self.db.refresh(visit)

        return visit

    async def delete(
        self,
        visit: Visit,
    ) -> None:

        await self.db.delete(visit)
        await self.db.commit()