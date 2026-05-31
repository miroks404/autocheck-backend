from dataclasses import dataclass
from typing import Protocol

from app.models import Submission


@dataclass
class CheckResultDTO:
    """CheckResultDTO — normalized checker output payload.

    Date: 31-05-2026
    Author: Team 4
    """

    checker: str
    status: str
    score: float
    message: str
    details: dict


class IChecker(Protocol):
    """IChecker — contract for pluggable checker implementations.

    Date: 31-05-2026
    Author: Team 4
    """

    name: str

    def run(self, submission: Submission, workspace_path: str) -> CheckResultDTO:
        ...
