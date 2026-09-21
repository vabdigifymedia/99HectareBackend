from typing import Any
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.agents.models import Agent
from app.modules.properties.models import Property


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, agent_id: int) -> Agent | None:
        result = await self.db.execute(
            select(Agent)
            .options(selectinload(Agent.user))
            .where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Agent | None:
        result = await self.db.execute(
            select(Agent)
            .options(selectinload(Agent.user))
            .where(Agent.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, agent: Agent) -> Agent:
        self.db.add(agent)
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def update(self, agent: Agent) -> Agent:
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def delete(self, agent: Agent) -> None:
        await self.db.delete(agent)
        await self.db.flush()

    async def list_agents(
        self,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Agent], int]:
        query = select(Agent).options(selectinload(Agent.user))

        if filters.get("is_active") is not None:
            query = query.where(Agent.is_active == filters["is_active"])

        if filters.get("is_featured") is not None:
            query = query.where(Agent.is_featured == filters["is_featured"])

        if filters.get("verification_status"):
            query = query.where(Agent.verification_status == filters["verification_status"])

        if filters.get("search"):
            term = f"%{filters['search']}%"
            query = query.where(
                or_(
                    Agent.agency_name.ilike(term),
                    Agent.description.ilike(term),
                    Agent.license_number.ilike(term),
                    Agent.rera_registration_number.ilike(term),
                    Agent.phone.ilike(term),
                    Agent.email.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(Agent.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_agent_properties(
        self,
        agent_id: int,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Property], int]:
        query = (
            select(Property)
            .options(
                selectinload(Property.media),
                selectinload(Property.amenities),
                selectinload(Property.city),
                selectinload(Property.locality),
            )
            .where(Property.agent_id == agent_id)
        )

        if status:
            query = query.where(Property.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(Property.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

