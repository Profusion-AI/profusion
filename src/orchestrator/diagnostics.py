"""Diagnostic log helpers for operator recovery surfaces."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key\s*[:=]\s*)[^\s,]+", re.IGNORECASE),
    re.compile(r"(authorization\s*[:=]\s*bearer\s+)[^\s,]+", re.IGNORECASE),
    re.compile(r"(token\s*[:=]\s*)[^\s,]+", re.IGNORECASE),
]
SECRET_KEY_PARTS = ("api_key", "apikey", "authorization", "token")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def redact(value: Any) -> str:
    text = str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    return text


def redact_context(value: Any) -> Any:
    """Recursively redact likely secrets before diagnostics touch disk."""
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = str(key).lower().replace("-", "_")
            if any(part in normalized_key for part in SECRET_KEY_PARTS):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_context(item)
        return redacted
    if isinstance(value, list):
        return [redact_context(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_context(item) for item in value)
    if isinstance(value, str):
        return redact(value)
    return value


def write_diagnostic(
    logs_dir: Path,
    *,
    stage: str,
    item_id: str | None = None,
    job_id: str | None = None,
    attempt: int | None = None,
    error: BaseException | str | None = None,
    error_code: str | None = None,
    context: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Write paired human and JSON diagnostic logs, returning both paths."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = utc_now()
    safe_ts = timestamp.replace(":", "").replace("-", "")
    identifier = job_id or item_id or "run"
    base = f"{stage}-{identifier}-{safe_ts}"
    log_path = logs_dir / f"{base}.log"
    json_path = logs_dir / f"{base}.json"

    exc_class = type(error).__name__ if isinstance(error, BaseException) else None
    exc_message = redact(error) if error is not None else None
    safe_context = redact_context(context or {})
    payload = {
        "timestamp": timestamp,
        "stage": stage,
        "item_id": item_id,
        "job_id": job_id,
        "attempt": attempt,
        "exception_class": exc_class,
        "error_code": error_code,
        "error_message": exc_message,
        "context": safe_context,
    }
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    lines = [
        f"timestamp: {timestamp}",
        f"stage: {stage}",
        f"item_id: {item_id or ''}",
        f"job_id: {job_id or ''}",
        f"attempt: {attempt if attempt is not None else ''}",
        f"exception_class: {exc_class or ''}",
        f"error_code: {error_code or ''}",
        f"error_message: {exc_message or ''}",
        "context:",
        json.dumps(safe_context, indent=2, default=str),
        f"diagnostic_json: {json_path}",
    ]
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(log_path), str(json_path)


def list_logs(
    logs_dir: Path,
    *,
    item_id: str | None = None,
    job_id: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List matching diagnostic/log files from newest to oldest."""
    if not logs_dir.exists():
        return []
    needle = job_id or item_id
    files = [p for p in logs_dir.iterdir() if p.is_file() and p.suffix in {".log", ".json"}]
    if needle:
        files = [p for p in files if needle in p.name or _json_mentions(p, needle)]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [
        {
            "path": str(p),
            "name": p.name,
            "size_bytes": p.stat().st_size,
            "modified_at": datetime.fromtimestamp(
                p.stat().st_mtime, timezone.utc
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
        for p in files[:limit]
    ]


def _json_mentions(path: Path, needle: str) -> bool:
    if path.suffix != ".json":
        return False
    try:
        return needle in path.read_text(encoding="utf-8")
    except OSError:
        return False
