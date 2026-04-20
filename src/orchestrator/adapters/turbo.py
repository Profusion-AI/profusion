"""MoneyPrinterTurbo HTTP adapter.

Transport-only. All vendor response shapes are validated with Pydantic
before returning to callers. State integer normalization lives here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import httpx
from pydantic import BaseModel, Field, ValidationError

from orchestrator import config

# Vendor state integers — vendor/MoneyPrinterTurbo/app/models/const.py
_STATE_FAILED = -1
_STATE_COMPLETE = 1
_STATE_PROCESSING = 4  # also covers 0/unknown

_STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "for", "with",
    "in", "on", "at", "to", "of", "is", "are", "was", "were",
    "it", "its", "this", "that", "how", "why", "what", "when",
})


class TurboUnavailableError(RuntimeError):
    """Raised when Turbo is unreachable, returns non-2xx, or its payload is malformed."""


# ---------------------------------------------------------------------------
# Private Pydantic response models
# ---------------------------------------------------------------------------

class _TurboRenderData(BaseModel):
    task_id: str = Field(min_length=1)


class _TurboRenderResponse(BaseModel):
    data: _TurboRenderData


class _TurboTaskData(BaseModel):
    state: int
    progress: int = 0
    videos: list[str] = Field(default_factory=list)


class _TurboTaskResponse(BaseModel):
    data: _TurboTaskData


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

@dataclass
class RenderProfile:
    aspect_ratio: str = "9:16"       # Turbo values: "9:16", "16:9", "1:1"
    voice: str = "en-US-GuyNeural"
    tts_engine: str = "edge-tts"
    duration_seconds: int = 60
    subtitle_style: str = "default"


@dataclass
class RenderJobResult:
    task_id: str
    status: str                       # "pending"|"processing"|"completed"|"failed"
    output_url: str | None = None
    progress: int = 0


# ---------------------------------------------------------------------------
# Private parsing helpers (tested in tests/test_turbo_adapter.py)
# ---------------------------------------------------------------------------

def _parse_render_response(body: dict) -> str:
    """Validate POST /api/v1/videos body; return task_id or raise TurboUnavailableError."""
    try:
        return _TurboRenderResponse.model_validate(body).data.task_id
    except ValidationError as e:
        raise TurboUnavailableError(
            f"Unexpected Turbo render response shape: {e}"
        ) from e


def _parse_task_response(body: dict) -> RenderJobResult:
    """Validate GET /api/v1/tasks/{id} body; return RenderJobResult."""
    try:
        resp = _TurboTaskResponse.model_validate(body)
    except ValidationError as e:
        raise TurboUnavailableError(
            f"Unexpected Turbo task response shape: {e}"
        ) from e

    d = resp.data
    if d.state == _STATE_COMPLETE:
        return RenderJobResult(
            task_id="",
            status="completed",
            output_url=d.videos[0] if d.videos else None,
            progress=d.progress,
        )
    if d.state == _STATE_FAILED:
        return RenderJobResult(task_id="", status="failed", progress=d.progress)
    return RenderJobResult(task_id="", status="processing", progress=d.progress)


def _extract_terms(topic: str) -> list[str]:
    """Derive Pexels search terms from topic text to bypass Turbo's LLM."""
    words = re.findall(r"[a-zA-Z]+", topic.lower())
    terms = [w for w in words if w not in _STOP_WORDS and len(w) > 2]
    return terms[:5] or ["education"]


# ---------------------------------------------------------------------------
# Public adapter functions
# ---------------------------------------------------------------------------

def render(
    *,
    subject: str,
    script: str,
    video_terms: list[str] | None = None,
    profile: RenderProfile | None = None,
) -> RenderJobResult:
    """Submit a render job; return immediately with task_id and status='pending'.

    Supplies video_script + video_terms to bypass Turbo's own LLM calls.
    Raises TurboUnavailableError on connection failure, non-2xx, or bad payload.
    """
    profile = profile or RenderProfile()
    payload = {
        "video_subject": subject,
        "video_script": script,
        "video_terms": video_terms or _extract_terms(subject),
        "video_aspect": profile.aspect_ratio,
        "voice_name": profile.voice,
        "subtitle_enabled": True,
    }
    try:
        resp = httpx.post(
            f"{config.TURBO_URL}/api/v1/videos",
            json=payload,
            timeout=30.0,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise TurboUnavailableError(
            f"MoneyPrinterTurbo returned {e.response.status_code}: "
            f"{e.response.text[:200]}"
        ) from e
    except httpx.RequestError as e:
        raise TurboUnavailableError(
            f"MoneyPrinterTurbo not reachable at {config.TURBO_URL}: {e}"
        ) from e

    try:
        task_id = _parse_render_response(resp.json())
    except ValueError as e:
        raise TurboUnavailableError(f"Turbo response is not valid JSON: {e}") from e
    return RenderJobResult(task_id=task_id, status="pending")


def get_job_status(task_id: str) -> RenderJobResult:
    """Poll task status; normalize Turbo state integers to string status.

    Raises TurboUnavailableError on connection failure or bad payload.
    """
    try:
        resp = httpx.get(
            f"{config.TURBO_URL}/api/v1/tasks/{task_id}",
            timeout=10.0,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise TurboUnavailableError(
            f"MoneyPrinterTurbo returned {e.response.status_code}: "
            f"{e.response.text[:200]}"
        ) from e
    except httpx.RequestError as e:
        raise TurboUnavailableError(
            f"MoneyPrinterTurbo not reachable at {config.TURBO_URL}: {e}"
        ) from e

    try:
        result = _parse_task_response(resp.json())
    except ValueError as e:
        raise TurboUnavailableError(f"Turbo response is not valid JSON: {e}") from e
    result.task_id = task_id
    return result
