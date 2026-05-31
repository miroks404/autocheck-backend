from app.core.errors import not_found
from app.domain.repositories import CandidateRepositoryPort


class CandidateUseCases:
    """CandidateUseCases — read scenarios for candidates and profile stats.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, repo: CandidateRepositoryPort):
        self.repo = repo

    def list(self) -> dict:
        rows = self.repo.list_candidates()
        items = [{"id": item.id, "fullName": item.full_name, "email": item.email} for item in rows]
        return {"items": items, "total": len(items)}

    def get(self, candidate_id: int) -> dict:
        row = self.repo.get_candidate(candidate_id)
        if not row:
            raise not_found("Candidate")
        submissions = self.repo.count_submissions(candidate_id)
        return {"id": row.id, "fullName": row.full_name, "email": row.email, "submissionsCount": submissions}
