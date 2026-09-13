from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.visits.schemas import VisitCreate , VisitUpdate , VisitStatusUpdate
from app.modules.visits.service import VisitService
import datetime

class VisitController:
    def __init__(self,service:VisitService | None = None , db:AsyncSession | None = None):
        if service is not None:
            self.service = service
        elif db is not None:
            self.service = VisitService(db)
        else:
            raise ValueError("Either service or db must be provided")

    async def create_visit(self , user_id:int , data:VisitCreate):
        return await self.service.create_visit(user_id , data)

    async def get_visit_by_id(self , id:int):
        return await self.service.get_visit_by_id(id)

    async def get_visits_by_user(self , user_id:int):
        return await self.service.get_visits_by_user(user_id)

    async def get_visits_by_agent(self , agent_id:int):
        return await self.service.get_visits_by_agent(agent_id)

    async def update_visit_status(self , id:int , status:str , confirmed_date:datetime , agent_notes:str , cancellation_reason:str):
        return await self.service.update_visit_status(id , status , confirmed_date , agent_notes , cancellation_reason)

    async def delete_visit(self , id:int):
        return await self.service.delete_visit(id)