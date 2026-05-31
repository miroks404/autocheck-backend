from datetime import datetime

from fastapi import HTTPException

from app.core.errors import not_found
from app.domain.repositories import SubmissionRepositoryPort
from app.infrastructure.analysis_provider import OpenAIAnalysisProvider
from app.models import SubmissionStatus, User, UserRole, VerdictStatus
from app.schemas import VerdictUpdate
from app.services.ai_reviewer import AICodeReviewer
from app.worker.tasks import run_submission_checks


class SubmissionUseCases:
    """SubmissionUseCases — submission lifecycle and evaluation workflows.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, repo: SubmissionRepositoryPort, candidate_repo=None):
        self.repo = repo
        self.candidate_repo = candidate_repo

    def create(
        self,
        assignment_id: int,
        user: User,
        git_url: str | None = None,
        zip_path: str | None = None,
        candidate_full_name: str | None = None,
        candidate_email: str | None = None,
    ) -> dict:
        source_value = git_url or zip_path
        if not source_value:
            raise HTTPException(status_code=422, detail="Either git_url or zip_path must be provided")
        if git_url and not git_url.lower().startswith("https://"):
            raise HTTPException(status_code=422, detail="Git URL must start with https://")

        candidate_id = user.id
        role = getattr(user.role, "value", user.role)
        if role in {"expert", "admin"} and candidate_email and candidate_full_name:
            if self.candidate_repo is None:
                raise HTTPException(status_code=422, detail="Candidate repository is not configured")
            try:
                candidate = self.candidate_repo.resolve_candidate(candidate_full_name.strip(), candidate_email.strip())
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            candidate_id = candidate.id

        submission = self.repo.create(
            assignment_id=assignment_id,
            candidate_id=candidate_id,
            source_type="git" if git_url else "zip",
            source_value=source_value,
        )
        run_submission_checks.delay(submission.id)
        return self._serialize_submission(submission)

    def list_submissions(self, user: User) -> dict:
        enriched = self.repo.list_enriched_for_user(user)
        items = [
            {
                **self._serialize_submission(entry["submission"]),
                "candidateFullName": entry["candidateFullName"],
                "candidateEmail": entry["candidateEmail"],
                "assignmentTitle": entry["assignmentTitle"],
            }
            for entry in enriched
        ]
        return {"items": items, "total": len(items)}

    def get(self, submission_id: int, user: User) -> dict:
        row = self._get_or_404(submission_id, user)
        payload = self._serialize_submission(row)
        enriched = next(
            (entry for entry in self.repo.list_enriched_for_user(user) if entry["submission"].id == submission_id),
            None,
        )
        if enriched:
            payload["candidateFullName"] = enriched["candidateFullName"]
            payload["candidateEmail"] = enriched["candidateEmail"]
            payload["assignmentTitle"] = enriched["assignmentTitle"]
        return payload

    def status(self, submission_id: int, user: User) -> dict:
        row = self._get_or_404(submission_id, user)
        return {"submissionId": row.id, "status": row.status.value, "updatedAt": row.updated_at.isoformat()}

    def results(self, submission_id: int, user: User) -> dict:
        self._get_or_404(submission_id, user)
        rows = self.repo.list_results(submission_id)
        items = [
            {
                "checker": item.checker,
                "status": item.status,
                "score": item.score,
                "message": item.message,
                "details": item.details,
                "createdAt": item.created_at.isoformat() if item.created_at else None,
            }
            for item in rows
        ]
        return {"items": items, "total": len(items)}

    def timeline(self, submission_id: int, user: User) -> dict:
        row = self._get_or_404(submission_id, user)
        results = sorted(self.repo.list_results(submission_id), key=lambda item: item.created_at or datetime.min)
        events = [
            {"event": "upload", "label": "Загрузка", "timestamp": row.created_at.isoformat() if row.created_at else None},
            {"event": "checks_started", "label": "Запуск проверок", "timestamp": row.updated_at.isoformat() if row.updated_at else None},
        ]
        for result in results:
            events.append(
                {
                    "event": f"checker_{result.checker}",
                    "label": f"Чекер {result.checker}",
                    "timestamp": result.created_at.isoformat() if result.created_at else None,
                    "status": result.status,
                    "score": result.score,
                }
            )
        if row.status == SubmissionStatus.done:
            events.append(
                {
                    "event": "checks_completed",
                    "label": "Проверка завершена",
                    "timestamp": row.updated_at.isoformat() if row.updated_at else None,
                    "finalScore": row.final_score,
                }
            )
        if row.verdict != VerdictStatus.pending:
            events.append(
                {
                    "event": "verdict",
                    "label": "Вердикт",
                    "timestamp": row.updated_at.isoformat() if row.updated_at else None,
                    "verdict": row.verdict.value,
                    "comment": row.verdict_comment,
                }
            )
        return {"items": events, "total": len(events)}

    def rerun(self, submission_id: int) -> dict:
        row = self._get_or_404(submission_id)
        row.status = SubmissionStatus.pending
        row.verdict = VerdictStatus.pending
        row.verdict_comment = None
        saved = self.repo.save(row)
        run_submission_checks.delay(saved.id)
        return self._serialize_submission(saved)

    def verdict(self, submission_id: int, payload: VerdictUpdate) -> dict:
        row = self._get_or_404(submission_id)
        row.verdict = VerdictStatus(payload.verdict)
        row.verdict_comment = payload.comment
        saved = self.repo.save(row)
        return self._serialize_submission(saved)

    def report(self, submission_id: int, user: User) -> dict:
        row = self._get_or_404(submission_id, user)
        results = self.repo.list_results(submission_id)
        enriched = next(
            (entry for entry in self.repo.list_enriched_for_user(user) if entry["submission"].id == submission_id),
            None,
        )
        return {
            "submissionId": row.id,
            "status": row.status.value,
            "finalScore": row.final_score,
            "candidateFullName": enriched["candidateFullName"] if enriched else f"Candidate #{row.candidate_id}",
            "assignmentTitle": enriched["assignmentTitle"] if enriched else f"Assignment #{row.assignment_id}",
            "generatedAt": datetime.utcnow().isoformat(),
            "results": [{"checker": r.checker, "status": r.status, "score": r.score, "message": r.message} for r in results],
            "verdict": row.verdict.value,
            "verdictComment": row.verdict_comment,
        }

    def report_html(self, submission_id: int, user: User) -> str:
        report = self.report(submission_id, user)
        rows = "".join(
            f"<tr><td>{item['checker']}</td><td>{item['status']}</td><td>{item['score']}</td><td>{item['message']}</td></tr>"
            for item in report["results"]
        )
        comment = report.get("verdictComment") or ""
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Отчёт по проверке #{report['submissionId']}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #111; }}
    h1 {{ margin-bottom: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
  </style>
</head>
<body>
  <h1>Отчёт по проверке #{report['submissionId']}</h1>
  <p><strong>Задание:</strong> {report['assignmentTitle']}</p>
  <p><strong>Кандидат:</strong> {report['candidateFullName']}</p>
  <p><strong>Статус:</strong> {report['status']}</p>
  <p><strong>Итоговый балл:</strong> {report['finalScore']}</p>
  <p><strong>Вердикт:</strong> {report['verdict']}</p>
  <p><strong>Комментарий:</strong> {comment}</p>
  <p><strong>Сформирован:</strong> {report['generatedAt']}</p>
  <table>
    <thead><tr><th>Чекер</th><th>Статус</th><th>Балл</th><th>Сообщение</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""

    def ai_review(self, submission_id: int, user: User) -> dict:
        row = self._get_or_404(submission_id, user)
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

    def _get_or_404(self, submission_id: int, user: User | None = None):
        row = self.repo.get(submission_id)
        if not row:
            raise not_found("Submission")
        if user is not None:
            self._ensure_can_access(row, user)
        return row

    @staticmethod
    def _ensure_can_access(submission, user: User) -> None:
        role = getattr(user.role, "value", user.role)
        if role in {"expert", "admin"}:
            return
        if submission.candidate_id != user.id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

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
            "verdictComment": item.verdict_comment,
            "createdAt": item.created_at.isoformat() if item.created_at else None,
            "updatedAt": item.updated_at.isoformat() if item.updated_at else None,
        }
