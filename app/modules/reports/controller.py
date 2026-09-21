from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reports.models import Report
from app.modules.reports.schemas import ReportCreate, ReportUpdate
from app.modules.reports.service import ReportService


class ReportController:
    def __init__(self, db: AsyncSession):
        self.service = ReportService(db)

    async def create_report(self, reporter_id: int, data: ReportCreate) -> Report:
        return await self.service.create_report(reporter_id=reporter_id, data=data)

    async def get_by_id(self, report_id: int) -> Report:
        return await self.service.get_by_id(report_id=report_id)

    async def get_my_reports(self, reporter_id: int) -> list[Report]:
        return await self.service.get_my_reports(reporter_id=reporter_id)

    async def list_reports(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Report], int]:
        return await self.service.list_reports(filters=filters, page=page, page_size=page_size)

    async def resolve_report(
        self,
        report_id: int,
        admin_id: int,
        admin_notes: str | None = None,
    ) -> Report:
        return await self.service.resolve_report(
            report_id=report_id,
            admin_id=admin_id,
            admin_notes=admin_notes,
        )

    async def update_report(self, report_id: int, data: ReportUpdate) -> Report:
        return await self.service.update_report(report_id=report_id, data=data)
