from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.reports.models import Report
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import ReportCreate, ReportUpdate


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReportRepository(db)

    async def create_report(self, reporter_id: int, data: ReportCreate) -> Report:
        return await self.repo.create(reporter_id=reporter_id, data=data)

    async def get_by_id(self, report_id: int) -> Report:
        report = await self.repo.get_by_id(report_id)
        if not report:
            raise NotFoundException(f"Report with ID {report_id} not found")
        return report

    async def get_my_reports(self, reporter_id: int) -> list[Report]:
        return await self.repo.get_by_reporter(reporter_id)

    async def list_reports(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Report], int]:
        offset = (max(1, page) - 1) * page_size
        return await self.repo.list(filters=filters, offset=offset, limit=page_size)

    async def resolve_report(
        self,
        report_id: int,
        admin_id: int,
        admin_notes: str | None = None,
    ) -> Report:
        report = await self.get_by_id(report_id)
        return await self.repo.resolve(report=report, admin_id=admin_id, admin_notes=admin_notes)

    async def update_report(self, report_id: int, data: ReportUpdate) -> Report:
        report = await self.get_by_id(report_id)
        if data.status:
            report.status = data.status
        if data.admin_notes:
            report.admin_notes = data.admin_notes
        return await self.repo.update(report)
