from __future__ import annotations

import json
import os
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AgentOrchestrator:
    """Thin Google GenAI SDK adapter with deterministic local fallback."""

    def __init__(self) -> None:
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._client = None
        if self.api_key:
            try:
                from google import genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def mode(self) -> str:
        return "gemini-genai-sdk" if self._client else "local-fallback"

    def structured_generate(self, prompt: str, schema: Type[T], fallback: T) -> T:
        if not self._client:
            return fallback
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                },
            )
            if getattr(response, "parsed", None):
                return response.parsed
            return schema.model_validate(json.loads(response.text))
        except Exception:
            return fallback

