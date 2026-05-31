import pytest
from fastapi import HTTPException

from app.application.use_cases.assignment_use_cases import AssignmentUseCases
from app.schemas import AssignmentCreate


class FakeAssignmentRepo:
    def list(self):
        return []

    def create(self, title, description, checker_weights, created_by, technologies=None, candidate_instructions="", status="published"):
        raise NotImplementedError

    def get(self, assignment_id):
        return None

    def update(self, assignment, title, description, checker_weights, technologies=None, candidate_instructions=None, status=None):
        raise NotImplementedError

    def delete(self, assignment):
        raise NotImplementedError


def test_assignment_weights_must_sum_to_100():
    use_case = AssignmentUseCases(FakeAssignmentRepo())
    payload = AssignmentCreate(
        title="Test",
        description="Desc",
        checker_weights={"static_analysis": 50, "build": 40},
    )

    with pytest.raises(HTTPException) as exc:
        use_case.create(payload, user_id=1)

    assert exc.value.status_code == 422
    assert "100" in str(exc.value.detail)
