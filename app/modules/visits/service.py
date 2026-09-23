from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from app.modules.visits.models import Visit
from app.modules.visits.schemas import VisitCreate, VisitListResponse, VisitResponse, VisitStatusUpdate , VisitUpdate
from app.modules.visits.repository import VisitRepository


from app.modules.users.models import User


class VisitService:
    def __init__(self , db:AsyncSession):
        self.repository = VisitRepository(db)
        
    async def create_visit(
        self ,
        user_id:int ,
        data:VisitCreate
    ):
        visit = await self.repository.create_visit(
            user_id = user_id,
            data = data
        )
        return visit

    async def get_visit_by_id(self , id:int):
        visit = await self.repository.get_by_id(id)
        return visit

    async def get_visits_by_user(self , user_id:int):
        visits = await self.repository.get_by_user(user_id)
        return visits    

    async def get_visits_by_agent(self , agent_id:int):
        visits = await self.repository.get_by_agent(agent_id)
        return visits    

    async def update_visit_status(
        self,
        id: int,
        data: VisitStatusUpdate,
        current_user: User | None = None,
    ):
        visit = await self.repository.get_by_id(id)
        if visit is None:
            return None
        visit = await self.repository.update_status(
            visit=visit,
            status=data.status,
            confirmed_date=data.confirmed_date,
            agent_notes=data.agent_notes,
            cancellation_reason=data.cancellation_reason,
        )
        return visit

    async def delete_visit(self , id:int):
        visit = await self.repository.get_by_id(id)
        if visit is None:
            return None
        await self.repository.delete(visit)
        return True    
