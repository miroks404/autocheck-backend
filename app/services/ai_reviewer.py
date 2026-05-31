import json

from app.checking.source_manager import collect_source_snippets, submission_workspace
from app.core.config import get_settings
from app.core.logging import get_logger
from app.domain.providers import IAnalysisProvider

settings = get_settings()
logger = get_logger("AICodeReviewer")


def unavailable_payload(reason: str) -> dict:
    return {
        "available": False,
        "summary": "AI-анализ недоступен",
        "strengths": [],
        "improvements": [reason],
        "raw": None,
    }


def _normalize_ai_response(content: str) -> dict:
    try:
        parsed = json.loads(content)
        summary = str(parsed.get("summary", "AI analysis completed"))
        strengths = [str(x) for x in parsed.get("strengths", [])][:10]
        improvements = [str(x) for x in parsed.get("improvements", [])][:10]
    except Exception:
        lines = [line.strip("- ").strip() for line in content.splitlines() if line.strip()]
        summary = lines[0] if lines else "AI analysis completed"
        strengths = lines[1:4] if len(lines) > 1 else ["Не удалось распарсить структурированный ответ"]
        improvements = lines[4:7] if len(lines) > 4 else ["Проверьте ответ модели вручную"]
    while len(strengths) < 3:
        strengths.append("Требуется дополнительный анализ")
    while len(improvements) < 3:
        improvements.append("Добавьте дополнительную проверку качества кода")
    return {
        "available": True,
        "summary": summary,
        "strengths": strengths[:10],
        "improvements": improvements[:10],
        "raw": content,
    }


class AICodeReviewer:
    """AICodeReviewer — orchestration service for AI code analysis.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, provider: IAnalysisProvider):
        self.provider = provider

    def review(self, submission_context: dict) -> dict:
        base_url = settings.ai_base_url.lower()
        using_ollama = "11434" in base_url or "ollama" in base_url
        if not settings.ai_api_key and not using_ollama:
            return unavailable_payload("AI_API_KEY не задан")

        workspace = submission_workspace(submission_context["submission_id"])
        snippets = collect_source_snippets(workspace) if workspace.exists() else []
        if not snippets:
            return unavailable_payload("Не найдены исходные файлы для AI-анализа")

        prompt = (
            "Ты code reviewer. Верни СТРОГО JSON с полями summary, strengths, improvements.\n"
            "Требования:\n"
            "- summary: короткий итог качества решения\n"
            "- strengths: минимум 3 конкретных сильных стороны\n"
            "- improvements: минимум 3 конкретных замечания/улучшения\n"
            f"- Требования задания: {submission_context.get('assignment_requirements', {})}\n"
            f"- Контекст submission: {submission_context}\n"
            f"- Файлы для анализа (не более 10, до 200 строк): {json.dumps(snippets, ensure_ascii=False)}"
        )
        try:
            content = self.provider.analyze(prompt)
            return _normalize_ai_response(content)
        except Exception as exc:  # pragma: no cover - network dependent
            logger.error("Ошибка — AI анализ недоступен submissionId=%s error=%s", submission_context.get("submission_id"), str(exc))
            return unavailable_payload(str(exc))
