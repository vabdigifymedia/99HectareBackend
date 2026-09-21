from typing import Any
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.builders.models import Builder


class BuilderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, builder_id: int) -> Builder | None:
        result = await self.db.execute(
            select(Builder)
            .options(selectinload(Builder.user))
            .where(Builder.id == builder_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Builder | None:
        result = await self.db.execute(
            select(Builder)
            .options(selectinload(Builder.user))
            .where(Builder.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, builder: Builder) -> Builder:
        self.db.add(builder)
        await self.db.flush()
        await self.db.refresh(builder)
        return builder

    async def update(self, builder: Builder) -> Builder:
        await self.db.flush()
        await self.db.refresh(builder)
        return builder

    async def list(
        self,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Builder], int]:
        query = select(Builder).options(selectinload(Builder.user))

        if filters.get("is_active") is not None:
            query = query.where(Builder.is_active == filters["is_active"])
        if filters.get("is_featured") is not None:
            query = query.where(Builder.is_featured == filters["is_featured"])
        if filters.get("verification_status"):
            query = query.where(Builder.verification_status == filters["verification_status"])

        if filters.get("search"):
            term = f"%{filters['search']}%"
            query = query.where(
                or_(
                    Builder.company_name.ilike(term),
                    Builder.description.ilike(term),
                    Builder.license_number.ilike(term),
                    Builder.rera_registration_number.ilike(term),
                    Builder.phone.ilike(term),
                    Builder.email.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(Builder.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total
