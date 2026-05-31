from __future__ import annotations

from typing import Protocol

from app.models import Assignment, CheckResult, Submission, User


class AuthRepositoryPort(Protocol):
    """AuthRepositoryPort — contract for auth data access.

    Date: 31-05-2026
    Author: Team 4
    """

    def get_by_email(self, email: str) -> User | None:
        ...

    def create_user(self, full_name: str, email: str, password_hash: str, role: str) -> User:
        ...


class AssignmentRepositoryPort(Protocol):
    """AssignmentRepositoryPort — contract for assignment persistence.

    Date: 31-05-2026
    Author: Team 4
    """

    def list(self) -> list[Assignment]:
        ...

    def create(
        self,
        title: str,
        description: str,
        checker_weights: dict[str, float],
        created_by: int,
        technologies: list[str] | None = None,
        candidate_instructions: str = "",
        status: str = "published",
    ) -> Assignment:
        ...

    def get(self, assignment_id: int) -> Assignment | None:
        ...

    def update(
        self,
        assignment: Assignment,
        title: str | None,
        description: str | None,
        checker_weights: dict | None,
        technologies: list[str] | None = None,
        candidate_instructions: str | None = None,
        status: str | None = None,
    ) -> Assignment:
        ...

    def delete(self, assignment: Assignment) -> None:
        ...


class SubmissionRepositoryPort(Protocol):
    """SubmissionRepositoryPort — contract for submission/result persistence.

    Date: 31-05-2026
    Author: Team 4
    """

    def create(self, assignment_id: int, candidate_id: int, source_type: str, source_value: str) -> Submission:
        ...

    def list_for_user(self, user: User) -> list[Submission]:
        ...

    def list_enriched_for_user(self, user: User) -> list[dict]:
        ...

    def get(self, submission_id: int) -> Submission | None:
        ...

    def list_results(self, submission_id: int) -> list[CheckResult]:
        ...

    def save(self, submission: Submission) -> Submission:
        ...

    def get_assignment_requirements(self, assignment_id: int) -> dict:
        ...


class CandidateRepositoryPort(Protocol):
    """CandidateRepositoryPort — contract for candidate read operations.

    Date: 31-05-2026
    Author: Team 4
    """

    def list_candidates(self) -> list[User]:
        ...

    def get_candidate(self, candidate_id: int) -> User | None:
        ...

    def count_submissions(self, candidate_id: int) -> int:
        ...

    def resolve_candidate(self, full_name: str, email: str) -> User:
        ...


class ReportRepositoryPort(Protocol):
    """ReportRepositoryPort — contract for aggregated reporting.

    Date: 31-05-2026
    Author: Team 4
    """

    def get_stats(self) -> dict:
        ...
