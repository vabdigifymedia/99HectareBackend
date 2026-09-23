from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.projects.models import Project, ProjectUnit


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug_or_id(self, slug_or_id: str | int) -> Project | None:
        detailed_options = (
            selectinload(Project.media),
            selectinload(Project.amenities),
            selectinload(Project.units),
            selectinload(Project.builder),
            selectinload(Project.city),
            selectinload(Project.locality),
        )

        if isinstance(slug_or_id, int) or (isinstance(slug_or_id, str) and slug_or_id.isdigit()):
            proj_id = int(slug_or_id)
            result = await self.db.execute(
                select(Project).options(*detailed_options).where(Project.id == proj_id)
            )
            item = result.scalar_one_or_none()
            if item:
                return item

        if isinstance(slug_or_id, str):
            parts = slug_or_id.rsplit("-", 1)
            if len(parts) == 2 and parts[1].isdigit():
                proj_id = int(parts[1])
                result = await self.db.execute(
                    select(Project).options(*detailed_options).where(Project.id == proj_id)
                )
                item = result.scalar_one_or_none()
                if item:
                    return item

            # Try matching by name
            first_words = slug_or_id.replace("-", " ").split()[:3]
            if first_words:
                query_term = f"%{'%'.join(first_words)}%"
                result = await self.db.execute(
                    select(Project).options(*detailed_options).where(Project.name.ilike(query_term)).limit(1)
                )
                item = result.scalar_one_or_none()
                if item:
                    return item

        return None

    async def list_projects(
        self,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "newest",
    ) -> tuple[list[Project], int]:
        conditions = []

        if filters.get("builder_id"):
            conditions.append(Project.builder_id == filters["builder_id"])

        if filters.get("city_id"):
            conditions.append(Project.city_id == filters["city_id"])

        if filters.get("locality_id"):
            conditions.append(Project.locality_id == filters["locality_id"])

        if filters.get("status"):
            conditions.append(Project.status == filters["status"])

        if filters.get("project_type"):
            conditions.append(Project.project_type == filters["project_type"])

        if filters.get("min_price") is not None:
            conditions.append(Project.price_from >= filters["min_price"])

        if filters.get("max_price") is not None:
            conditions.append(Project.price_to <= filters["max_price"])

        if filters.get("search"):
            term = f"%{filters['search'].strip()}%"
            conditions.append(
                Project.name.ilike(term)
                | Project.description.ilike(term)
                | Project.address.ilike(term)
            )

        count_query = select(func.count(Project.id)).where(*conditions)
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one() or 0

        if sort_by == "price_asc":
            order_by = Project.price_from.asc().nullslast()
        elif sort_by == "price_desc":
            order_by = Project.price_to.desc().nullslast()
        else:
            order_by = Project.created_at.desc()

        query = (
            select(Project)
            .options(
                selectinload(Project.media),
                selectinload(Project.amenities),
                selectinload(Project.units),
                selectinload(Project.builder),
                selectinload(Project.city),
                selectinload(Project.locality),
            )
            .where(*conditions)
            .order_by(order_by)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def update(self, project: Project) -> Project:
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.flush()
