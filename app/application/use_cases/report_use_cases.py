from app.domain.repositories import ReportRepositoryPort


class ReportUseCases:
    """ReportUseCases — aggregated dashboard reporting scenarios.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, repo: ReportRepositoryPort):
        self.repo = repo

    def stats(self) -> dict:
        raw = self.repo.get_stats()
        top_candidates = [
            {
                "candidateId": item.get("candidate_id"),
                "fullName": item.get("full_name"),
                "bestScore": item.get("best_score"),
                "attempts": item.get("attempts"),
            }
            for item in raw.get("top_candidates", [])
        ]
        return {
            "checksLast30Days": raw.get("checks_last_30_days", 0),
            "avgScore": raw.get("avg_score", 0),
            "passRatePct": raw.get("pass_rate_pct", 0),
            "topCandidates": top_candidates,
        }
