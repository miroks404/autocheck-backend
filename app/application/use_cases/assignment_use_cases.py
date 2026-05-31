from fastapi import HTTPException

from app.core.errors import not_found
from app.domain.repositories import AssignmentRepositoryPort
from app.schemas import AssignmentCreate, AssignmentUpdate


def _validate_weights(weights: dict[str, float]) -> None:
    if not weights:
        return
    total = round(sum(float(value) for value in weights.values()), 2)
    if total != 100:
        raise HTTPException(status_code=422, detail=f"Checker weights must sum to 100%, got {total}%")


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
        _validate_weights(payload.checker_weights)
        row = self.repo.create(
            payload.title,
            payload.description,
            payload.checker_weights,
            user_id,
            technologies=payload.technologies,
            candidate_instructions=payload.candidate_instructions,
            status=payload.status,
        )
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
        if payload.checker_weights is not None:
            _validate_weights(payload.checker_weights)
        updated = self.repo.update(
            row,
            payload.title,
            payload.description,
            payload.checker_weights,
            technologies=payload.technologies,
            candidate_instructions=payload.candidate_instructions,
            status=payload.status,
        )
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
            "technologies": item.technologies or [],
            "candidateInstructions": item.candidate_instructions or "",
            "checkerWeights": item.checker_weights,
            "status": item.status.value if hasattr(item.status, "value") else item.status,
            "createdBy": item.created_by,
            "createdAt": item.created_at.isoformat() if item.created_at else None,
        }
