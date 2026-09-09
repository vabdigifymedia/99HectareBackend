from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.agents.models import Agent


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
