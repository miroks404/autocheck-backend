from app.core.errors import not_found
from app.domain.repositories import AssignmentRepositoryPort
from app.schemas import AssignmentCreate, AssignmentUpdate


class AssignmentUseCases:
    """AssignmentUseCases — operations with test assignments.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, repo: AssignmentRepositoryPort):
        self.repo = repo

    def list(self) -> dict:
        rows = self.repo.list()
        items = [self._serialize(item) for item in rows]
        return {"items": items, "total": len(items)}

    def create(self, payload: AssignmentCreate, user_id: int) -> dict:
        row = self.repo.create(payload.title, payload.description, payload.checker_weights, user_id)
        return self._serialize(row)

    def get(self, assignment_id: int) -> dict:
        row = self.repo.get(assignment_id)
        if not row:
            raise not_found("Assignment")
        return self._serialize(row)

    def update(self, assignment_id: int, payload: AssignmentUpdate) -> dict:
        row = self.repo.get(assignment_id)
        if not row:
            raise not_found("Assignment")
        updated = self.repo.update(row, payload.title, payload.description, payload.checker_weights)
        return self._serialize(updated)

    def delete(self, assignment_id: int) -> int:
        row = self.repo.get(assignment_id)
        if not row:
            raise not_found("Assignment")
        self.repo.delete(row)
        return assignment_id

    @staticmethod
    def _serialize(item) -> dict:
        return {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "checkerWeights": item.checker_weights,
            "createdBy": item.created_by,
            "createdAt": item.created_at.isoformat() if item.created_at else None,
        }
