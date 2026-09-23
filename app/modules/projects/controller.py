from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.schemas import ProjectCreate, ProjectUpdate
from app.modules.projects.service import ProjectService


class ProjectController:
    def __init__(self, db: AsyncSession):
        self.service = ProjectService(db)

    async def list_projects(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "newest",
    ):
        return await self.service.list_projects(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
        )

    async def get_project(self, project_id_or_slug: int | str):
        return await self.service.get_project(project_id_or_slug)

    async def create_project(self, data: ProjectCreate):
        return await self.service.create_project(data)

    async def update_project(self, project_id: int, data: ProjectUpdate):
        return await self.service.update_project(project_id, data)

    async def delete_project(self, project_id: int) -> None:
        await self.service.delete_project(project_id)
