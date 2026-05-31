from app.checking.calculator import ResultCalculator
from app.checking.interfaces import CheckResultDTO, IChecker
from app.models import Submission


class CheckOrchestrator:
    """CheckOrchestrator — only checker orchestration and score aggregation.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, checkers: list[IChecker], weights: dict[str, float] | None = None):
        self.checkers = checkers
        self.weights = weights or {}

    def run_all(self, submission: Submission, workspace_path: str, on_result=None) -> tuple[list[CheckResultDTO], int]:
        """Run all checkers, optionally invoking callback after each result."""
        results: list[CheckResultDTO] = []
        for checker in self.checkers:
            try:
                item = checker.run(submission, workspace_path)
            except Exception as exc:  # pragma: no cover - runtime guard
                item = CheckResultDTO(
                    checker=getattr(checker, "name", "unknown"),
                    status="error",
                    score=0,
                    message="Checker failed",
                    details={"error": str(exc)},
                )
            results.append(item)
            if on_result is not None:
                on_result(item)
        total = ResultCalculator.total_score(results, self.weights)
        return results, total
