from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.application.use_cases.submission_use_cases import SubmissionUseCases
from app.models import SubmissionStatus, UserRole, VerdictStatus


class FakeSubmissionRepo:
    def __init__(self, submission):
        self.submission = submission

    def create(self, assignment_id: int, candidate_id: int, source_type: str, source_value: str):
        raise NotImplementedError

    def list_for_user(self, user):
        return [self.submission]

    def list_enriched_for_user(self, user):
        return [
            {
                "submission": self.submission,
                "candidateFullName": "Test Candidate",
                "candidateEmail": "candidate@example.com",
                "assignmentTitle": "Test Assignment",
            }
        ]

    def get(self, submission_id: int):
        if submission_id == self.submission.id:
            return self.submission
        return None

    def list_results(self, submission_id: int):
        return []

    def save(self, submission):
        self.submission = submission
        return submission

    def get_assignment_requirements(self, assignment_id: int):
        return {}


def _submission(candidate_id: int = 100):
    now = datetime.utcnow()
    return SimpleNamespace(
        id=1,
        assignment_id=10,
        candidate_id=candidate_id,
        source_type="git",
        source_value="https://example.com/repo.git",
        status=SubmissionStatus.pending,
        final_score=None,
        verdict=VerdictStatus.pending,
        verdict_comment=None,
        ai_review=None,
        created_at=now,
        updated_at=now,
    )


def _user(user_id: int, role: UserRole):
    return SimpleNamespace(id=user_id, role=role)


def test_candidate_cannot_access_foreign_submission():
    repo = FakeSubmissionRepo(_submission(candidate_id=100))
    use_case = SubmissionUseCases(repo)
    user = _user(200, UserRole.candidate)

    with pytest.raises(HTTPException) as exc:
        use_case.get(1, user)

    assert exc.value.status_code == 403


def test_expert_can_access_any_submission():
    repo = FakeSubmissionRepo(_submission(candidate_id=100))
    use_case = SubmissionUseCases(repo)
    expert = _user(300, UserRole.expert)

    data = use_case.get(1, expert)

    assert data["id"] == 1
    assert data["candidateId"] == 100
