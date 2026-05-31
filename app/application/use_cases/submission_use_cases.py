from datetime import datetime

from fastapi import HTTPException

from app.core.errors import not_found
from app.domain.repositories import SubmissionRepositoryPort
from app.infrastructure.analysis_provider import OpenAIAnalysisProvider
from app.models import SubmissionStatus, User, VerdictStatus
from app.schemas import VerdictUpdate
from app.services.ai_reviewer import AICodeReviewer
from app.worker.tasks import run_submission_checks


class SubmissionUseCases:
    """SubmissionUseCases — submission lifecycle and evaluation workflows.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, repo: SubmissionRepositoryPort):
        self.repo = repo

    def create(
        self,
        assignment_id: int,
        user: User,
        git_url: str | None = None,
        zip_path: str | None = None,
    ) -> dict:
        source_value = git_url or zip_path
        if not source_value:
            raise HTTPException(status_code=422, detail="Either git_url or zip_path must be provided")
        submission = self.repo.create(
            assignment_id=assignment_id,
            candidate_id=user.id,
            source_type="git" if git_url else "zip",
            source_value=source_value,
        )
        run_submission_checks.delay(submission.id)
        return self._serialize_submission(submission)

    def list_submissions(self, user: User) -> dict:
        rows = self.repo.list_for_user(user)
        items = [self._serialize_submission(item) for item in rows]
        return {"items": items, "total": len(items)}

    def get(self, submission_id: int) -> dict:
        row = self._get_or_404(submission_id)
        return self._serialize_submission(row)

    def status(self, submission_id: int) -> dict:
        row = self._get_or_404(submission_id)
        return {"submissionId": row.id, "status": row.status.value, "updatedAt": row.updated_at.isoformat()}

    def results(self, submission_id: int) -> dict:
        self._get_or_404(submission_id)
        rows = self.repo.list_results(submission_id)
        items = [
            {
                "checker": item.checker,
                "status": item.status,
                "score": item.score,
                "message": item.message,
                "details": item.details,
            }
            for item in rows
        ]
        return {"items": items, "total": len(items)}

    def rerun(self, submission_id: int) -> dict:
        row = self._get_or_404(submission_id)
        row.status = SubmissionStatus.pending
        saved = self.repo.save(row)
        run_submission_checks.delay(saved.id)
        return self._serialize_submission(saved)

    def verdict(self, submission_id: int, payload: VerdictUpdate) -> dict:
        row = self._get_or_404(submission_id)
        row.verdict = VerdictStatus(payload.verdict)
        saved = self.repo.save(row)
        return self._serialize_submission(saved)

    def report(self, submission_id: int) -> dict:
        row = self._get_or_404(submission_id)
        results = self.repo.list_results(submission_id)
        return {
            "submissionId": row.id,
            "status": row.status.value,
            "finalScore": row.final_score,
            "generatedAt": datetime.utcnow().isoformat(),
            "results": [{"checker": r.checker, "status": r.status, "score": r.score, "message": r.message} for r in results],
        }

    def ai_review(self, submission_id: int) -> dict:
        row = self._get_or_404(submission_id)
        if row.ai_review:
            return row.ai_review
        assignment_requirements = self.repo.get_assignment_requirements(row.assignment_id)
        reviewer = AICodeReviewer(provider=OpenAIAnalysisProvider())
        payload = reviewer.review(
            {
                "submission_id": row.id,
                "assignment_id": row.assignment_id,
                "source_type": row.source_type,
                "source_value": row.source_value,
                "status": row.status.value,
                "assignment_requirements": assignment_requirements,
            }
        )
        row.ai_review = payload
        self.repo.save(row)
        return payload

    def _get_or_404(self, submission_id: int):
        row = self.repo.get(submission_id)
        if not row:
            raise not_found("Submission")
        return row

    @staticmethod
    def _serialize_submission(item) -> dict:
        return {
            "id": item.id,
            "assignmentId": item.assignment_id,
            "candidateId": item.candidate_id,
            "sourceType": item.source_type,
            "status": item.status.value,
            "finalScore": item.final_score,
            "verdict": item.verdict.value,
            "createdAt": item.created_at.isoformat() if item.created_at else None,
            "updatedAt": item.updated_at.isoformat() if item.updated_at else None,
        }
