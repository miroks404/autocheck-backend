from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.use_cases.candidate_use_cases import CandidateUseCases
from app.core.database import get_db
from app.core.response import ok
from app.deps import require_expert
from app.infrastructure.repositories import SqlAlchemyCandidateRepository
from app.models import User

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", summary="Список кандидатов")
def list_candidates(db: Session = Depends(get_db), user: User = Depends(require_expert)):
    use_case = CandidateUseCases(SqlAlchemyCandidateRepository(db))
    data = use_case.list()
    return ok(data, meta={"total": data.get("total", 0)})


@router.get("/{candidate_id}", summary="Кандидат по ID")
def get_candidate(candidate_id: int, db: Session = Depends(get_db), user: User = Depends(require_expert)):
    use_case = CandidateUseCases(SqlAlchemyCandidateRepository(db))
    return ok(use_case.get(candidate_id))
