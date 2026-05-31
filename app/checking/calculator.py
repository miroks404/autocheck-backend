from app.checking.interfaces import CheckResultDTO


class ResultCalculator:
    """ResultCalculator — computes final weighted score from checker results.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - total_score(results, weights) -> int
    """

    @staticmethod
    def total_score(results: list[CheckResultDTO], weights: dict[str, float]) -> int:
        if not results:
            return 0
        numerator = 0.0
        denominator = 0.0
        for result in results:
            weight = float(weights.get(result.checker, 1))
            numerator += result.score * weight
            denominator += weight
        return int(round((numerator / denominator) if denominator else 0))
