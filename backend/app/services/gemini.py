from __future__ import annotations

import json
from typing import AsyncGenerator, Optional

import structlog

from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()


class GeminiClient:
    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.gemini_api_key)
            except Exception:
                log.warning("gemini_not_configured", hint="Set GEMINI_API_KEY to enable AI features")
                return None
        return self._client

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[list] = None,
        temperature: float = 0.7,
    ) -> str:
        client = await self._get_client()
        if client is None:
            return self._fallback_response(user_message)

        try:
            contents = []
            if conversation_history:
                for msg in conversation_history[-20:]:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})

            contents.append({"role": "user", "parts": [{"text": user_message}]})

            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config={
                    "system_instruction": system_prompt,
                    "temperature": temperature,
                    "max_output_tokens": 2048,
                },
            )
            return response.text

        except Exception:
            log.exception("gemini_generation_failed")
            return self._fallback_response(user_message)

    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[list] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        client = await self._get_client()
        if client is None:
            yield self._fallback_response(user_message)
            return

        try:
            contents = []
            if conversation_history:
                for msg in conversation_history[-20:]:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})

            contents.append({"role": "user", "parts": [{"text": user_message}]})

            response = client.models.generate_content_stream(
                model=settings.gemini_model,
                contents=contents,
                config={
                    "system_instruction": system_prompt,
                    "temperature": temperature,
                    "max_output_tokens": 2048,
                },
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception:
            log.exception("gemini_stream_failed")
            yield self._fallback_response(user_message)

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[list] = None,
    ) -> dict:
        raw = await self.generate(
            system_prompt=system_prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences.",
            user_message=user_message,
            conversation_history=conversation_history,
            temperature=0.3,
        )
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            log.warning("gemini_json_parse_failed", raw=raw[:200])
            return {}

    def _fallback_response(self, user_message: str) -> str:
        return (
            "I'm having a moment — let me think about that again. "
            "In the meantime, feel free to pick from the options above!"
        )


gemini_client = GeminiClient()
