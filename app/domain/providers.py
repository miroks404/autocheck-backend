from typing import Protocol


class IAnalysisProvider(Protocol):
    """IAnalysisProvider — abstraction for AI inference provider.

    Date: 31-05-2026
    Author: Team 4
    """

    def analyze(self, prompt: str) -> str:
        """Execute AI analysis and return raw model response text."""
        ...
