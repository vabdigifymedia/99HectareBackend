from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.projects.models import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProjectRepository(db)

    async def list_projects(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "newest",
    ) -> tuple[list[Project], int]:
        offset = (max(1, page) - 1) * page_size
        return await self.repo.list_projects(
            filters=filters,
            offset=offset,
            limit=page_size,
            sort_by=sort_by,
        )

    async def get_project(self, project_id_or_slug: int | str) -> Project:
        project = await self.repo.get_by_slug_or_id(project_id_or_slug)
        if not project:
            raise NotFoundException(f"Project '{project_id_or_slug}' not found")
        return project

    async def create_project(self, data: ProjectCreate) -> Project:
        project_dict = data.model_dump()
        project = Project(**project_dict)
        created = await self.repo.create(project)
        await self.db.commit()
        return await self.repo.get_by_slug_or_id(created.id) or created

    async def update_project(self, project_id: int, data: ProjectUpdate) -> Project:
        project = await self.get_project(project_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        updated = await self.repo.update(project)
        await self.db.commit()
        return updated

    async def delete_project(self, project_id: int) -> None:
        project = await self.get_project(project_id)
        await self.repo.delete(project)
        await self.db.commit()
