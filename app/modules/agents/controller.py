from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.models import Agent
from app.modules.agents.schemas import (
    AgentBulkPropertyCreate,
    AgentProfileCreate,
    AgentUpdate,
)
from app.modules.agents.service import AgentService
from app.modules.properties.models import Property
from app.modules.properties.schemas import PropertyCreate
from app.modules.users.models import User


class AgentController:
    def __init__(self, db: AsyncSession):
        self.service = AgentService(db)

    async def get_by_id(self, agent_id: int) -> Agent:
        return await self.service.get_by_id(agent_id)

    async def get_by_user_id(self, user_id: int) -> Agent:
        return await self.service.get_by_user_id(user_id)

    async def list_agents(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Agent], int]:
        return await self.service.list_agents(filters=filters, page=page, page_size=page_size)

    async def create_profile(self, current_user: User, data: AgentProfileCreate) -> Agent:
        return await self.service.create_profile(current_user=current_user, data=data)

    async def update_profile(self, current_user: User, data: AgentUpdate) -> Agent:
        return await self.service.update_profile(current_user=current_user, data=data)

    async def get_agent_properties(
        self,
        agent_id: int,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Property], int]:
        return await self.service.get_agent_properties(
            agent_id=agent_id, status=status, page=page, page_size=page_size
        )

    async def get_my_properties(
        self,
        current_user: User,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Property], int]:
        return await self.service.get_my_properties(
            current_user=current_user, status=status, page=page, page_size=page_size
        )

    async def create_property(
        self,
        current_user: User,
        data: PropertyCreate,
    ) -> Property:
        return await self.service.create_property(current_user=current_user, data=data)

    async def create_bulk_properties(
        self,
        current_user: User,
        data: AgentBulkPropertyCreate,
    ) -> list[Property]:
        return await self.service.create_bulk_properties(current_user=current_user, bulk_data=data)
