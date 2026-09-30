"""Thin client for Ollama's OpenAI-compatible endpoints."""

from __future__ import annotations

from typing import Any, AsyncIterator

import httpx

from app.settings import settings


class OllamaClient:
    def __init__(self) -> None:
        self.base = settings.ollama_base_url.rstrip("/")
        self.timeout = settings.request_timeout_s

    def _url(self, path: str) -> str:
        return f"{self.base}{path}"

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(self._url("/api/tags"))
            r.raise_for_status()
            data = r.json()
            return [m.get("name", "") for m in data.get("models", [])]

    async def chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        stream: bool,
        temperature: float | None,
    ) -> httpx.Response:
        payload: dict[str, Any] = {
            "model": model or settings.kosi_model,
            "messages": messages,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        client = httpx.AsyncClient(timeout=self.timeout)
        # Caller must aclose client when done for stream paths; for non-stream we close after read.
        req = client.build_request(
            "POST",
            self._url("/v1/chat/completions"),
            json=payload,
        )
        return await client.send(req, stream=stream), client


async def iter_sse_bytes(response: httpx.Response) -> AsyncIterator[bytes]:
    async for chunk in response.aiter_bytes():
        yield chunk
