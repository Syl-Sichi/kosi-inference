"""
K.O.S.I. inference API — OpenAI-compatible chat completions.
Proxies to Ollama so CloudConnect's cai-chat (llama provider) works unchanged.
"""

from __future__ import annotations

from typing import Any, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.auth import require_api_key
from app.ollama_client import OllamaClient, iter_sse_bytes
from app.settings import settings

app = FastAPI(
    title="K.O.S.I. Inference",
    description="Knowledge Operating System Intelligence — CloudConnect co-pilot backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama = OllamaClient()


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"] | str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(min_length=1)
    stream: bool = False
    temperature: float | None = 0.7
    max_tokens: int | None = None


@app.get("/health")
async def health() -> dict[str, Any]:
    try:
        models = await ollama.list_models()
        ollama_ok = True
    except Exception as e:  # noqa: BLE001
        models = []
        ollama_ok = False
        return {
            "status": "degraded",
            "service": "kosi-inference",
            "ollama_ok": ollama_ok,
            "error": str(e),
            "default_model": settings.kosi_model,
            "models": models,
        }
    return {
        "status": "ok",
        "service": "kosi-inference",
        "ollama_ok": ollama_ok,
        "default_model": settings.kosi_model,
        "models": models,
    }


@app.get("/v1/models")
async def list_models(_: None = Depends(require_api_key)) -> dict[str, Any]:
    try:
        names = await ollama.list_models()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama unreachable: {e}") from e
    return {
        "object": "list",
        "data": [
            {"id": n, "object": "model", "owned_by": "kosi"}
            for n in names
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    body: ChatCompletionRequest,
    _: None = Depends(require_api_key),
):
    model = body.model or settings.kosi_model
    messages = [m.model_dump() for m in body.messages]

    try:
        response, client = await ollama.chat_completion(
            model=model,
            messages=messages,
            stream=body.stream,
            temperature=body.temperature,
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}") from e

    if body.stream:

        async def stream_and_close():
            try:
                if response.status_code >= 400:
                    err = await response.aread()
                    yield err
                    return
                async for chunk in iter_sse_bytes(response):
                    yield chunk
            finally:
                await response.aclose()
                await client.aclose()

        return StreamingResponse(
            stream_and_close(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-KOSI-Model": model,
            },
        )

    # non-streaming
    try:
        if response.status_code >= 400:
            text = (await response.aread()).decode("utf-8", errors="replace")
            raise HTTPException(status_code=502, detail=text[:500])
        data = response.json()
        return JSONResponse(data)
    finally:
        await response.aclose()
        await client.aclose()


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "K.O.S.I. Inference",
        "docs": "/docs",
        "health": "/health",
        "chat": "/v1/chat/completions",
    }
