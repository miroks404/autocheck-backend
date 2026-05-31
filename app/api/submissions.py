import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.application.use_cases.submission_use_cases import SubmissionUseCases
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.response import ok
from app.deps import get_current_user, require_expert
from app.infrastructure.repositories import SqlAlchemyCandidateRepository, SqlAlchemySubmissionRepository
from app.models import SubmissionStatus, User
from app.schemas import VerdictUpdate

router = APIRouter(prefix="/submissions", tags=["submissions"])
logger = get_logger("SubmissionController")
MAX_ZIP_SIZE_BYTES = 50 * 1024 * 1024


def _submission_use_cases(db: Session) -> SubmissionUseCases:
    return SubmissionUseCases(
        SqlAlchemySubmissionRepository(db),
        candidate_repo=SqlAlchemyCandidateRepository(db),
    )


@router.post("", summary="Загрузить решение (ZIP или Git URL)")
async def create_submission(
    assignment_id: int = Form(...),
    git_url: str | None = Form(default=None),
    zip_file: UploadFile | None = File(default=None),
    candidate_full_name: str | None = Form(default=None),
    candidate_email: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info("Критическое действие — загрузка задания userId=%s assignmentId=%s", user.id, assignment_id)
    use_case = _submission_use_cases(db)
    zip_path: str | None = None
    if zip_file is not None:
        uploads_dir = Path("/app/storage/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4()}-{zip_file.filename or 'submission.zip'}"
        target = uploads_dir / filename
        content = await zip_file.read()
        if len(content) > MAX_ZIP_SIZE_BYTES:
            logger.error("Ошибка — ZIP превышает лимит userId=%s sizeBytes=%s", user.id, len(content))
            raise HTTPException(status_code=422, detail="ZIP file exceeds 50MB limit")
        if not (zip_file.filename or "").lower().endswith(".zip"):
            raise HTTPException(status_code=422, detail="Only .zip files are allowed")
        target.write_bytes(content)
        zip_path = str(target)
    return ok(
        use_case.create(
            assignment_id=assignment_id,
            user=user,
            git_url=git_url,
            zip_path=zip_path,
            candidate_full_name=candidate_full_name,
            candidate_email=candidate_email,
        ),
        status_code=201,
    )


@router.get("", summary="Список проверок")
def list_submissions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = _submission_use_cases(db)
    data = use_case.list_submissions(user)
    return ok(data, meta={"total": data.get("total", 0)})


@router.get("/{submission_id}", summary="Проверка по ID")
def get_submission(submission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = _submission_use_cases(db)
    return ok(use_case.get(submission_id, user))


@router.get("/{submission_id}/status", summary="Текущий статус проверки")
def get_status(submission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = _submission_use_cases(db)
    return ok(use_case.status(submission_id, user))


@router.get("/{submission_id}/results", summary="Детальные результаты чекеров")
def get_results(submission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = _submission_use_cases(db)
    return ok(use_case.results(submission_id, user))


@router.get("/{submission_id}/timeline", summary="Хронология событий проверки")
def get_timeline(submission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = _submission_use_cases(db)
    return ok(use_case.timeline(submission_id, user))


@router.post("/{submission_id}/rerun", summary="Повторный запуск проверки")
def rerun_submission(submission_id: int, db: Session = Depends(get_db), user: User = Depends(require_expert)):
    logger.info("Критическое действие — повторный запуск проверки submissionId=%s expertId=%s", submission_id, user.id)
    use_case = _submission_use_cases(db)
    return ok(use_case.rerun(submission_id))


@router.put("/{submission_id}/verdict", summary="Вынести вердикт")
def update_verdict(
    submission_id: int,
    payload: VerdictUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_expert),
):
    logger.info(
        "Критическое действие — вынесение вердикта submissionId=%s expertId=%s verdict=%s",
        submission_id,
        user.id,
        payload.verdict,
    )
    use_case = _submission_use_cases(db)
    return ok(use_case.verdict(submission_id, payload))


@router.get("/{submission_id}/report", summary="Скачать отчёт по проверке")
def download_report(
    submission_id: int,
    format: str = "json",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    use_case = _submission_use_cases(db)
    if format.lower() == "html":
        html = use_case.report_html(submission_id, user)
        return HTMLResponse(
            content=html,
            headers={"Content-Disposition": f'attachment; filename="submission-{submission_id}-report.html"'},
        )
    return ok(use_case.report(submission_id, user))


@router.get("/{submission_id}/ai-review", summary="AI-анализ решения")
def ai_review(submission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    use_case = _submission_use_cases(db)
    return ok(use_case.ai_review(submission_id, user))


@router.get("/{submission_id}/events", summary="SSE-поток статусов проверки")
async def submission_events(submission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = SqlAlchemySubmissionRepository(db)
    use_case = SubmissionUseCases(repo, candidate_repo=SqlAlchemyCandidateRepository(db))
    use_case.status(submission_id, user)

    async def event_stream():
        for _ in range(60):
            current = repo.get(submission_id)
            if current is None:
                break
            yield f"data: {current.status.value}\n\n"
            if current.status in {SubmissionStatus.done, SubmissionStatus.error}:
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
