from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.visits.schemas import VisitCreate , VisitUpdate , VisitStatusUpdate
from app.modules.visits.service import VisitService
import datetime

class VisitController:
    def __init__(self, db: AsyncSession | None = None, service: VisitService | None = None):
        if isinstance(db, VisitService):
            self.service = db
        elif service is not None:
            self.service = service
        elif db is not None:
            self.service = VisitService(db)
        else:
            raise ValueError("Either db or service must be provided")

    async def create_visit(self , user_id:int , data:VisitCreate):
        return await self.service.create_visit(user_id , data)

    async def get_visit_by_id(self , id:int):
        return await self.service.get_visit_by_id(id)

    async def get_visits_by_user(self , user_id:int):
        return await self.service.get_visits_by_user(user_id)

    async def get_visits_by_agent(self , agent_id:int):
        return await self.service.get_visits_by_agent(agent_id)

    async def update_visit_status(self, id: int, data: VisitStatusUpdate, current_user: Any = None):
        return await self.service.update_visit_status(id, data, current_user)

    async def delete_visit(self , id:int):
        return await self.service.delete_visit(id)