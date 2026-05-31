from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class UserPublic:
    """UserPublic — public user projection for transport layers.

    Date: 31-05-2026
    Author: Team 4
    """

    id: int
    full_name: str
    email: str
    role: str


@dataclass
class AssignmentPublic:
    """AssignmentPublic — public assignment projection for transport layers.

    Date: 31-05-2026
    Author: Team 4
    """

    id: int
    title: str
    description: str
    checker_weights: dict[str, float]
    created_by: int


@dataclass
class SubmissionPublic:
    """SubmissionPublic — public submission projection for transport layers.

    Date: 31-05-2026
    Author: Team 4
    """

    id: int
    assignment_id: int
    candidate_id: int
    status: str
    final_score: int | None
    verdict: str
    created_at: datetime
    updated_at: datetime
    ai_review: dict[str, Any] | None
