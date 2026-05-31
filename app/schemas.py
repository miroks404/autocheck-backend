from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    """RegisterIn — payload schema for user registration.

    Date: 31-05-2026
    Author: Team 4
    """

    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["candidate", "expert", "admin"] = "candidate"


class LoginIn(BaseModel):
    """LoginIn — payload schema for user login.

    Date: 31-05-2026
    Author: Team 4
    """

    email: EmailStr
    password: str


class AssignmentCreate(BaseModel):
    """AssignmentCreate — payload schema for assignment creation.

    Date: 31-05-2026
    Author: Team 4
    """

    title: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    candidate_instructions: str = ""
    checker_weights: dict[str, float] = Field(default_factory=dict)
    status: Literal["draft", "published"] = "published"


class AssignmentUpdate(BaseModel):
    """AssignmentUpdate — payload schema for assignment update.

    Date: 31-05-2026
    Author: Team 4
    """

    title: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    candidate_instructions: str | None = None
    checker_weights: dict[str, float] | None = None
    status: Literal["draft", "published"] | None = None


class SubmissionCreate(BaseModel):
    """SubmissionCreate — payload schema for submission creation.

    Date: 31-05-2026
    Author: Team 4
    """

    assignment_id: int
    git_url: str | None = None
    zip_path: str | None = None


class VerdictUpdate(BaseModel):
    """VerdictUpdate — payload schema for verdict update.

    Date: 31-05-2026
    Author: Team 4
    """

    verdict: Literal["approved", "rejected", "pending"]
    comment: str | None = None


class AIReviewOut(BaseModel):
    """AIReviewOut — response schema for AI review section.

    Date: 31-05-2026
    Author: Team 4
    """

    available: bool
    summary: str
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    raw: Any | None = None


class SubmissionOut(BaseModel):
    """SubmissionOut — projection schema for submission list/details.

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
