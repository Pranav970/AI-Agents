from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from app.config import settings


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.llm_provider

    def available(self) -> bool:
        if self.provider == "openai":
            return bool(settings.openai_api_key)
        if self.provider == "ollama":
            return True
        return False

    def generate(self, system: str, user: str, extra_context: Optional[str] = None) -> str:
        if self.provider == "openai" and settings.openai_api_key:
            return self._openai_generate(system, user, extra_context)
        if self.provider == "ollama":
            return self._ollama_generate(system, user, extra_context)
        return self._offline_generate(user, extra_context)

    def _offline_generate(self, user: str, extra_context: Optional[str] = None) -> str:
        context = f"\n\nContext: {extra_context}" if extra_context else ""
        return (
            "I can help with that using a practical fitness plan. "
            "Share your age, height, weight, goal, activity level, and equipment for a more personalized answer."
            f"{context}"
        )

    def _ollama_generate(self, system: str, user: str, extra_context: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user if not extra_context else f"{user}\n\n{extra_context}"},
            ],
            "stream": False,
        }
        resp = requests.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"].strip()

    def _openai_generate(self, system: str, user: str, extra_context: Optional[str] = None) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = user if not extra_context else f"{user}\n\n{extra_context}"
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
