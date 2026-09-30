"""Optional Bearer token gate for the inference API."""

from fastapi import Header, HTTPException

from app.settings import settings


async def require_api_key(authorization: str | None = Header(default=None)) -> None:
    expected = settings.kosi_api_key
    if not expected:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
