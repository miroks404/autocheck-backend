from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Assignment, CheckResult, Submission, User, UserRole


class SqlAlchemyAuthRepository:
    """SqlAlchemyAuthRepository — persistence adapter for auth user operations.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - get_by_email(email) -> User | None
    - create_user(full_name, email, password_hash, role) -> User
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, full_name: str, email: str, password_hash: str, role: str) -> User:
        user = User(full_name=full_name, email=email, password_hash=password_hash, role=UserRole(role))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class SqlAlchemyAssignmentRepository:
    """SqlAlchemyAssignmentRepository — persistence adapter for assignments.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - list() -> list[Assignment]
    - create(title, description, checker_weights, created_by) -> Assignment
    - get(assignment_id) -> Assignment | None
    - update(assignment, title, description, checker_weights) -> Assignment
    - delete(assignment) -> None
    """

    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Assignment]:
        return self.db.query(Assignment).order_by(Assignment.id.desc()).all()

    def create(self, title: str, description: str, checker_weights: dict[str, float], created_by: int) -> Assignment:
        assignment = Assignment(
            title=title,
            description=description,
            checker_weights=checker_weights,
            created_by=created_by,
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get(self, assignment_id: int) -> Assignment | None:
        return self.db.get(Assignment, assignment_id)

    def update(self, assignment: Assignment, title: str | None, description: str | None, checker_weights: dict | None) -> Assignment:
        if title is not None:
            assignment.title = title
        if description is not None:
            assignment.description = description
        if checker_weights is not None:
            assignment.checker_weights = checker_weights
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def delete(self, assignment: Assignment) -> None:
        self.db.delete(assignment)
        self.db.commit()


class SqlAlchemySubmissionRepository:
    """SqlAlchemySubmissionRepository — persistence adapter for submissions/results.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - create(...) -> Submission
    - list_for_user(user) -> list[Submission]
    - get(submission_id) -> Submission | None
    - list_results(submission_id) -> list[CheckResult]
    - save(submission) -> Submission
    - get_assignment_requirements(assignment_id) -> dict
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, assignment_id: int, candidate_id: int, source_type: str, source_value: str) -> Submission:
        submission = Submission(
            assignment_id=assignment_id,
            candidate_id=candidate_id,
            source_type=source_type,
            source_value=source_value,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def list_for_user(self, user: User) -> list[Submission]:
        query = self.db.query(Submission).order_by(Submission.id.desc())
        if user.role == UserRole.candidate:
            query = query.filter(Submission.candidate_id == user.id)
        return query.all()

    def get(self, submission_id: int) -> Submission | None:
        return self.db.get(Submission, submission_id)

    def list_results(self, submission_id: int) -> list[CheckResult]:
        return self.db.query(CheckResult).filter(CheckResult.submission_id == submission_id).all()

    def save(self, submission: Submission) -> Submission:
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_assignment_requirements(self, assignment_id: int) -> dict:
        assignment = self.db.get(Assignment, assignment_id)
        if not assignment:
            return {"title": "Unknown assignment", "description": "", "checker_weights": {}}
        return {
            "title": assignment.title,
            "description": assignment.description,
            "checker_weights": assignment.checker_weights or {},
        }


class SqlAlchemyCandidateRepository:
    """SqlAlchemyCandidateRepository — persistence adapter for candidate data.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - list_candidates() -> list[User]
    - get_candidate(candidate_id) -> User | None
    - count_submissions(candidate_id) -> int
    """

    def __init__(self, db: Session):
        self.db = db

    def list_candidates(self) -> list[User]:
        return self.db.query(User).filter(User.role == UserRole.candidate).all()

    def get_candidate(self, candidate_id: int) -> User | None:
        candidate = self.db.get(User, candidate_id)
        if not candidate or candidate.role != UserRole.candidate:
            return None
        return candidate

    def count_submissions(self, candidate_id: int) -> int:
        return self.db.query(Submission).filter(Submission.candidate_id == candidate_id).count()


class SqlAlchemyReportRepository:
    """SqlAlchemyReportRepository — persistence adapter for dashboard statistics.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - get_stats() -> dict
    """

    def __init__(self, db: Session):
        self.db = db

    def get_stats(self) -> dict:
        since = datetime.utcnow() - timedelta(days=30)
        total = self.db.query(Submission).filter(Submission.created_at >= since).count()
        avg_score = self.db.query(func.avg(Submission.final_score)).filter(Submission.created_at >= since).scalar() or 0
        passed = self.db.query(Submission).filter(Submission.created_at >= since, Submission.final_score >= 60).count()
        success_rate = (passed / total * 100) if total else 0

        top_rows = (
            self.db.query(
                Submission.candidate_id.label("candidate_id"),
                func.max(Submission.final_score).label("best_score"),
                func.count(Submission.id).label("attempts"),
            )
            .group_by(Submission.candidate_id)
            .order_by(func.max(Submission.final_score).desc())
            .limit(10)
            .all()
        )
        top_candidates = []
        for row in top_rows:
            candidate = self.db.get(User, row.candidate_id)
            top_candidates.append(
                {
                    "candidate_id": row.candidate_id,
                    "full_name": candidate.full_name if candidate else "Unknown",
                    "best_score": int(row.best_score or 0),
                    "attempts": int(row.attempts or 0),
                }
            )
        return {
            "checks_last_30_days": total,
            "avg_score": round(float(avg_score), 2),
            "pass_rate_pct": round(success_rate, 2),
            "top_candidates": top_candidates,
        }
