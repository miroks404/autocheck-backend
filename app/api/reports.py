from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.use_cases.report_use_cases import ReportUseCases
from app.core.database import get_db
from app.core.response import ok
from app.deps import require_expert
from app.infrastructure.repositories import SqlAlchemyReportRepository
from app.models import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/stats", summary="Статистика проверок")
def stats(db: Session = Depends(get_db), user: User = Depends(require_expert)):
    use_case = ReportUseCases(SqlAlchemyReportRepository(db))
    return ok(use_case.stats())
