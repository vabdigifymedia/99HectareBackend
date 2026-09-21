from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import UserRole
from app.common.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.modules.agents.models import Agent
from app.modules.agents.repository import AgentRepository
from app.modules.agents.schemas import (
    AgentBulkPropertyCreate,
    AgentProfileCreate,
    AgentUpdate,
)
from app.modules.properties.models import Property
from app.modules.properties.schemas import PropertyCreate
from app.modules.properties.service import PropertyService
from app.modules.users.models import User


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AgentRepository(db)
        self.property_service = PropertyService(db)

    async def get_by_id(self, agent_id: int) -> Agent:
        agent = await self.repo.get_by_id(agent_id)
        if not agent:
            raise NotFoundException(f"Agent with ID {agent_id} not found")
        return agent

    async def get_by_user_id(self, user_id: int) -> Agent:
        agent = await self.repo.get_by_user_id(user_id)
        if not agent:
            raise NotFoundException(f"Agent profile not found for user {user_id}")
        return agent

    async def list_agents(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Agent], int]:
        offset = (max(1, page) - 1) * page_size
        return await self.repo.list_agents(filters=filters, offset=offset, limit=page_size)

    async def create_profile(self, current_user: User, data: AgentProfileCreate) -> Agent:
        existing = await self.repo.get_by_user_id(current_user.id)
        if existing:
            raise ConflictException("Agent profile already exists for this user")

        payload = data.model_dump(exclude_unset=True)
        if "website" in payload and payload["website"] is not None:
            payload["website"] = str(payload["website"])

        if not payload.get("phone"):
            payload["phone"] = current_user.phone
        if not payload.get("email"):
            payload["email"] = current_user.email

        agent = Agent(user_id=current_user.id, **payload)
        created = await self.repo.create(agent)

        if current_user.role != UserRole.AGENT.value:
            current_user.role = UserRole.AGENT.value

        await self.db.commit()
        await self.db.refresh(created)
        return created

    async def update_profile(self, current_user: User, data: AgentUpdate) -> Agent:
        agent = await self.repo.get_by_user_id(current_user.id)
        if not agent:
            raise NotFoundException("Agent profile not found for this account")

        payload = data.model_dump(exclude_unset=True)
        if "website" in payload and payload["website"] is not None:
            payload["website"] = str(payload["website"])

        for key, value in payload.items():
            setattr(agent, key, value)

        updated = await self.repo.update(agent)
        await self.db.commit()
        return updated

    async def get_agent_properties(
        self,
        agent_id: int,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Property], int]:
        await self.get_by_id(agent_id)
        offset = (max(1, page) - 1) * page_size
        return await self.repo.get_agent_properties(
            agent_id=agent_id, status=status, offset=offset, limit=page_size
        )

    async def get_my_properties(
        self,
        current_user: User,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Property], int]:
        agent = await self.repo.get_by_user_id(current_user.id)
        if not agent:
            raise NotFoundException("Agent profile not found for this account")

        offset = (max(1, page) - 1) * page_size
        return await self.repo.get_agent_properties(
            agent_id=agent.id, status=status, offset=offset, limit=page_size
        )

    async def create_property(
        self,
        current_user: User,
        data: PropertyCreate,
    ) -> Property:
        agent = await self.repo.get_by_user_id(current_user.id)
        if not agent:
            raise NotFoundException("Agent profile not found. Please create an agent profile first.")

        # Ensure role is set or current_user has agent profile loaded
        current_user.agent_profile = agent
        return await self.property_service.create_property(current_user=current_user, data=data)

    async def create_bulk_properties(
        self,
        current_user: User,
        bulk_data: AgentBulkPropertyCreate,
    ) -> list[Property]:
        agent = await self.repo.get_by_user_id(current_user.id)
        if not agent:
            raise NotFoundException("Agent profile not found. Please create an agent profile first.")

        current_user.agent_profile = agent
        created_properties: list[Property] = []

        for prop_data in bulk_data.properties:
            prop = await self.property_service.create_property(current_user=current_user, data=prop_data)
            created_properties.append(prop)

        return created_properties
