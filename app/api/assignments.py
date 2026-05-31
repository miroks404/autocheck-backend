from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.use_cases.assignment_use_cases import AssignmentUseCases
from app.core.database import get_db
from app.core.response import ok
from app.deps import get_current_user, require_expert
from app.infrastructure.repositories import SqlAlchemyAssignmentRepository
from app.models import User
from app.schemas import AssignmentCreate, AssignmentUpdate

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("", summary="Список тестовых заданий")
def list_assignments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = AssignmentUseCases(SqlAlchemyAssignmentRepository(db))
    data = use_case.list()
    return ok(data, meta={"total": data.get("total", 0)})


@router.post("", summary="Создание тестового задания")
def create_assignment(payload: AssignmentCreate, db: Session = Depends(get_db), user: User = Depends(require_expert)):
    use_case = AssignmentUseCases(SqlAlchemyAssignmentRepository(db))
    return ok(use_case.create(payload, user.id), status_code=201)


@router.get("/{assignment_id}", summary="Получить задание по ID")
def get_assignment(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = AssignmentUseCases(SqlAlchemyAssignmentRepository(db))
    return ok(use_case.get(assignment_id))


@router.put("/{assignment_id}", summary="Редактировать задание")
def update_assignment(
    assignment_id: int,
    payload: AssignmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_expert),
):
    use_case = AssignmentUseCases(SqlAlchemyAssignmentRepository(db))
    return ok(use_case.update(assignment_id, payload))


@router.delete("/{assignment_id}", summary="Удалить задание")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(require_expert)):
    use_case = AssignmentUseCases(SqlAlchemyAssignmentRepository(db))
    deleted_id = use_case.delete(assignment_id)
    return ok({"deleted": deleted_id})
