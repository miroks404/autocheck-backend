import httpx

from app.core.config import get_settings
from app.domain.providers import IAnalysisProvider

settings = get_settings()


class OpenAIAnalysisProvider(IAnalysisProvider):
    """OpenAIAnalysisProvider — concrete OpenAI-compatible API adapter.

    Date: 31-05-2026
    Author: Team 4
    """

    def analyze(self, prompt: str) -> str:
        headers = {}
        if settings.ai_api_key and settings.ai_api_key.lower() not in {"ollama", "none"}:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"
        payload = {
            "model": settings.ai_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        base = settings.ai_base_url.rstrip("/")
        endpoint = f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"
        with httpx.Client(timeout=25) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
