from sqlalchemy.orm import Session

from app.checking.checkers import (
    ArchitectureChecker,
    BuildChecker,
    DocumentationChecker,
    GitPracticesChecker,
    StaticAnalysisChecker,
    TestChecker,
)
from app.checking.orchestrator import CheckOrchestrator
from app.checking.source_manager import prepare_submission_workspace
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models import Assignment, CheckResult, Submission, SubmissionStatus
from app.worker.celery_app import celery_app

logger = get_logger("CheckOrchestrator")


@celery_app.task(name="run_submission_checks")
def run_submission_checks(submission_id: int):
    db: Session = SessionLocal()
    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return
        assignment = db.get(Assignment, submission.assignment_id)
        submission.status = SubmissionStatus.running
        db.commit()
        logger.info("Проверка запущена — submissionId=%s", submission.id)

        try:
            workspace_path = str(prepare_submission_workspace(submission))
        except Exception as exc:
            logger.error("Ошибка — не удалось подготовить workspace submissionId=%s error=%s", submission.id, str(exc))
            db.add(
                CheckResult(
                    submission_id=submission.id,
                    checker="source_preparation",
                    status="error",
                    score=0,
                    message="Failed to prepare source workspace",
                    details={"error": str(exc)},
                )
            )
            submission.status = SubmissionStatus.error
            db.commit()
            return
        checkers = [
            StaticAnalysisChecker(),
            ArchitectureChecker(),
            BuildChecker(),
            TestChecker(),
            DocumentationChecker(),
            GitPracticesChecker(),
        ]
        db.query(CheckResult).filter(CheckResult.submission_id == submission.id).delete()
        db.commit()

        orchestrator = CheckOrchestrator(checkers=checkers, weights=(assignment.checker_weights if assignment else {}))

        def persist_result(item):
            logger.info("Чекер завершен — submissionId=%s checker=%s status=%s", submission.id, item.checker, item.status)
            db.add(
                CheckResult(
                    submission_id=submission.id,
                    checker=item.checker,
                    status=item.status,
                    score=int(item.score),
                    message=item.message,
                    details=item.details,
                )
            )
            db.commit()
            db.refresh(submission)

        _, total_score = orchestrator.run_all(submission=submission, workspace_path=workspace_path, on_result=persist_result)
        submission.final_score = total_score
        submission.status = SubmissionStatus.done
        db.commit()
        logger.info("Проверка завершена — submissionId=%s score=%s", submission.id, total_score)
    except Exception:
        submission = db.get(Submission, submission_id)
        if submission:
            submission.status = SubmissionStatus.error
            db.commit()
        logger.error("Ошибка — выполнение проверки submissionId=%s", submission_id)
        raise
    finally:
        db.close()
