from datetime import datetime, timezone
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.reports.models import Report
from app.modules.reports.schemas import ReportCreate


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, reporter_id: int, data: ReportCreate) -> Report:
        report = Report(
            reporter_id=reporter_id,
            property_id=data.property_id,
            agent_id=data.agent_id,
            builder_id=data.builder_id,
            reported_user_id=data.reported_user_id,
            reason=data.reason,
            description=data.description,
            status="OPEN",
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_by_id(self, report_id: int) -> Report | None:
        result = await self.db.execute(
            select(Report)
            .options(
                selectinload(Report.reporter),
                selectinload(Report.property),
                selectinload(Report.agent),
                selectinload(Report.builder),
            )
            .where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_by_reporter(self, reporter_id: int) -> list[Report]:
        result = await self.db.execute(
            select(Report)
            .where(Report.reporter_id == reporter_id)
            .order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(
        self,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Report], int]:
        query = select(Report).options(
            selectinload(Report.reporter),
            selectinload(Report.property),
            selectinload(Report.agent),
            selectinload(Report.builder),
        )

        if filters.get("status"):
            query = query.where(Report.status == filters["status"])
        if filters.get("reason"):
            query = query.where(Report.reason == filters["reason"])
        if filters.get("property_id"):
            query = query.where(Report.property_id == filters["property_id"])
        if filters.get("agent_id"):
            query = query.where(Report.agent_id == filters["agent_id"])

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(Report.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def resolve(
        self,
        report: Report,
        admin_id: int,
        admin_notes: str | None = None,
    ) -> Report:
        report.status = "RESOLVED"
        report.resolved_by = admin_id
        report.resolved_at = datetime.now(timezone.utc)
        if admin_notes:
            report.admin_notes = admin_notes

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def update(self, report: Report) -> Report:
        await self.db.commit()
        await self.db.refresh(report)
        return report
