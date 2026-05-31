from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, Enum):
    """UserRole — user role enumeration for authorization.

    Date: 31-05-2026
    Author: Team 4
    """

    candidate = "candidate"
    expert = "expert"
    admin = "admin"


class SubmissionStatus(str, Enum):
    """SubmissionStatus — lifecycle status for submission processing.

    Date: 31-05-2026
    Author: Team 4
    """

    pending = "pending"
    running = "running"
    done = "done"
    error = "error"


class VerdictStatus(str, Enum):
    """VerdictStatus — final expert verdict states.

    Date: 31-05-2026
    Author: Team 4
    """

    approved = "approved"
    rejected = "rejected"
    pending = "pending"


class AssignmentStatus(str, Enum):
    """AssignmentStatus — publication lifecycle for test assignments.

    Date: 31-05-2026
    Author: Team 4
    """

    draft = "draft"
    published = "published"


class User(Base):
    """User — persistence model for platform users.

    Date: 31-05-2026
    Author: Team 4
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.candidate, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Assignment(Base):
    """Assignment — persistence model for test assignments.

    Date: 31-05-2026
    Author: Team 4
    """

    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    technologies: Mapped[list] = mapped_column(JSON, default=list)
    candidate_instructions: Mapped[str] = mapped_column(Text, default="")
    checker_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[AssignmentStatus] = mapped_column(SqlEnum(AssignmentStatus), default=AssignmentStatus.published)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Submission(Base):
    """Submission — persistence model for candidate submissions.

    Date: 31-05-2026
    Author: Team 4
    """

    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"), nullable=False)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), default="git")
    source_value: Mapped[str] = mapped_column(Text)
    status: Mapped[SubmissionStatus] = mapped_column(SqlEnum(SubmissionStatus), default=SubmissionStatus.pending)
    final_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verdict: Mapped[VerdictStatus] = mapped_column(SqlEnum(VerdictStatus), default=VerdictStatus.pending)
    verdict_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_review: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    results = relationship("CheckResult", back_populates="submission", cascade="all, delete-orphan")


class CheckResult(Base):
    """CheckResult — persistence model for checker execution output.

    Date: 31-05-2026
    Author: Team 4
    """

    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False, index=True)
    checker: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20))
    score: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text, default="")
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="results")
