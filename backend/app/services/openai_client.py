from __future__ import annotations

import json
from typing import AsyncGenerator, Optional

import structlog

from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()


class OpenAIClient:
    def __init__(self) -> None:
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=settings.openai_api_key)
            except Exception:
                log.warning("openai_not_configured", hint="Set OPENAI_API_KEY to enable AI features")
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
            messages = [{"role": "system", "content": system_prompt}]

            if conversation_history:
                for msg in conversation_history[-20:]:
                    role = "user" if msg["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": msg["content"]})

            messages.append({"role": "user", "content": user_message})

            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
            )
            return response.choices[0].message.content or ""

        except Exception:
            log.exception("openai_generation_failed")
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
            messages = [{"role": "system", "content": system_prompt}]

            if conversation_history:
                for msg in conversation_history[-20:]:
                    role = "user" if msg["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": msg["content"]})

            messages.append({"role": "user", "content": user_message})

            stream = await client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        except Exception:
            log.exception("openai_stream_failed")
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
            log.warning("openai_json_parse_failed", raw=raw[:200])
            return {}

    def _fallback_response(self, user_message: str) -> str:
        return (
            "I'm having a moment — let me think about that again. "
            "In the meantime, feel free to pick from the options above!"
        )


openai_client = OpenAIClient()
