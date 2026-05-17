"""Read models for CLI inspection and the future local dashboard."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator import db
from orchestrator.diagnostics import list_logs

TIMESTAMP_FIELDS = {
    "applied_at",
    "created_at",
    "published_at",
    "scheduled_for",
    "started_at",
    "timestamp",
    "updated_at",
}


def _json_load(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except ValueError:
        return default


def _iso_utc(value: str) -> str:
    """Normalize SQLite/ISO timestamp strings to ISO 8601 UTC with Z suffix."""
    raw = value.strip()
    if not raw:
        return value
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _normalize_record(value: Any) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if key in TIMESTAMP_FIELDS and isinstance(item, str):
                normalized[key] = _iso_utc(item)
            else:
                normalized[key] = _normalize_record(item)
        return normalized
    if isinstance(value, list):
        return [_normalize_record(item) for item in value]
    return value


def _normalize_rows(rows: list[dict]) -> list[dict[str, Any]]:
    return [_normalize_record(row) for row in rows]


def _artifact_payload(render_job: dict | None) -> dict[str, Any]:
    if not render_job or not render_job.get("output_path"):
        return {
            "mp4_path": None,
            "mp4_exists": False,
            "manifest_path": None,
            "manifest_exists": False,
            "qa_report_path": None,
            "qa_report_exists": False,
        }
    mp4 = Path(render_job["output_path"])
    manifest = mp4.parent / "manifest.json"
    qa_report = mp4.parent / "qa_report.json"
    return {
        "mp4_path": str(mp4),
        "mp4_exists": mp4.exists() and mp4.stat().st_size > 0,
        "manifest_path": str(manifest),
        "manifest_exists": manifest.exists(),
        "qa_report_path": str(qa_report),
        "qa_report_exists": qa_report.exists(),
    }


def status_payload(db_path: Path, status: str | None = None) -> dict[str, Any]:
    items = db.get_all_items(db_path, status=status)
    return {
        "items": _normalize_rows(items),
        "summary": db.get_queue_summary(db_path),
        "filters": {"status": status},
    }


def jobs_payload(db_path: Path, item_id: str) -> dict[str, Any]:
    render_jobs = db.get_render_jobs_for_item(db_path, item_id)
    publish_jobs = db.get_publish_jobs_for_item(db_path, item_id)
    return {
        "item_id": item_id,
        "render_jobs": [_normalize_render_job(j) for j in render_jobs],
        "publish_jobs": [_normalize_publish_job(j) for j in publish_jobs],
    }


def renders_payload(db_path: Path, item_id: str) -> dict[str, Any]:
    jobs = [_normalize_render_job(j) for j in db.get_render_jobs_for_item(db_path, item_id)]
    latest = jobs[0] if jobs else None
    return {
        "item_id": item_id,
        "latest_render_job": latest,
        "render_jobs": jobs,
        "artifacts": _artifact_payload(latest),
        "retry": _render_retry(latest),
    }


def approvals_payload(db_path: Path, item_id: str) -> dict[str, Any]:
    approvals = _normalize_rows(db.get_approval_records(db_path, item_id))
    latest = approvals[0] if approvals else None
    return {
        "item_id": item_id,
        "latest_approval": latest,
        "approval_records": approvals,
        "effective_decision": latest["decision"] if latest else None,
        "eligible_for_publish": bool(latest and latest["decision"] == "approved"),
    }


def inspect_payload(db_path: Path, logs_dir: Path, item: dict) -> dict[str, Any]:
    item_id = item["id"]
    brief = db.get_latest_brief(db_path, item_id)
    variants = _normalize_rows(db.get_script_variants(db_path, item_id))
    render_jobs = [_normalize_render_job(j) for j in db.get_render_jobs_for_item(db_path, item_id)]
    publish_jobs = [_normalize_publish_job(j) for j in db.get_publish_jobs_for_item(db_path, item_id)]
    approvals = _normalize_rows(db.get_approval_records(db_path, item_id))
    latest_render = _first_or_none(render_jobs)
    latest_publish = _first_or_none(publish_jobs)
    artifacts = _artifact_payload(latest_render)
    blockage = _blockage(item, latest_render, latest_publish, artifacts)
    retry = _item_retry(item, latest_render, latest_publish, artifacts)
    return {
        "item": _normalize_record(item),
        "milestone": "M6",
        "lifecycle_state": item["status"],
        "latest_brief": _normalize_brief(brief) if brief else None,
        "script_variants": variants,
        "latest_script_variant": variants[-1] if variants else None,
        "latest_render_job": latest_render,
        "latest_qa": _load_qa_report(artifacts),
        "latest_approval": _first_or_none(approvals),
        "latest_publish_job": latest_publish,
        "jobs": {
            "render_jobs": render_jobs,
            "publish_jobs": publish_jobs,
        },
        "artifacts": artifacts,
        "recent_logs": list_logs(logs_dir, item_id=item_id, limit=10),
        "blockage": blockage,
        "retry": retry,
        "next_safe_command": _next_safe_command(item, latest_render, latest_publish, artifacts),
    }


def handoff_payload(
    db_path: Path,
    logs_dir: Path,
    *,
    item: dict | None = None,
    status: str | None = None,
    failed_only: bool = False,
) -> dict[str, Any]:
    items = [item] if item else db.get_all_items(db_path, status=status)
    if failed_only:
        failed_ids = {j["content_item_id"] for j in db.get_failed_publish_jobs(db_path)}
        items = [
            i for i in items
            if i["id"] in failed_ids or i["status"] in {"qa_failed"}
        ]
    inspected = [inspect_payload(db_path, logs_dir, i) for i in items]
    return {
        "milestone": "M6",
        "git": _git_state(),
        "queue_summary": db.get_queue_summary(db_path),
        "filters": {"status": status, "failed_only": failed_only},
        "items": inspected,
        "recent_logs": list_logs(logs_dir, limit=10),
    }


def _normalize_brief(brief: dict) -> dict[str, Any]:
    normalized = dict(brief)
    for field in ("hook_options", "claims_to_verify", "risk_flags", "source_refs"):
        normalized[field] = _json_load(normalized.get(field), [])
    return _normalize_record(normalized)


def _normalize_render_job(job: dict) -> dict[str, Any]:
    normalized = dict(job)
    normalized["render_profile"] = _json_load(normalized.get("render_profile"), {})
    normalized["retry"] = _render_retry(normalized)
    return _normalize_record(normalized)


def _normalize_publish_job(job: dict) -> dict[str, Any]:
    normalized = dict(job)
    normalized["platform_metadata"] = _json_load(normalized.get("platform_metadata"), {})
    normalized["retry"] = _publish_retry(normalized)
    return _normalize_record(normalized)


def _render_retry(job: dict | None) -> dict[str, Any]:
    if not job:
        return {"retryable": False, "reason": "No render job exists"}
    if job["status"] == "failed":
        return {
            "retryable": True,
            "reason": "Failed render jobs can be resubmitted",
            "command": f"uv run profusion retry --render-job-id {job['id']}",
        }
    if job["status"] == "completed":
        return {"retryable": False, "reason": "Completed render jobs are immutable"}
    return {"retryable": False, "reason": f"Render job is {job['status']!r}"}


def _publish_retry(job: dict | None) -> dict[str, Any]:
    if not job:
        return {"retryable": False, "reason": "No publish job exists"}
    if job["status"] != "failed":
        return {"retryable": False, "reason": f"Publish job is {job['status']!r}"}
    return {
        "retryable": True,
        "reason": "Failed publish job can be retried",
        "command": f"uv run profusion retry --job-id {job['id']}",
    }


def _item_retry(
    item: dict,
    latest_render: dict | None,
    latest_publish: dict | None,
    artifacts: dict[str, Any],
) -> dict[str, Any]:
    if item["status"] == "qa_failed":
        ok = artifacts["mp4_exists"] and artifacts["manifest_exists"]
        return {
            "retryable": ok,
            "stage": "qa",
            "reason": "QA can be re-run after explicit return to rendered" if ok else "Render package is incomplete",
            "command": f"uv run profusion retry --item-id {item['id']} --stage qa" if ok else None,
        }
    if latest_publish and latest_publish.get("status") == "failed":
        return _publish_retry(latest_publish)
    if latest_render and latest_render.get("status") == "failed":
        return _render_retry(latest_render)
    return {"retryable": False, "reason": "No failed retry surface detected"}


def _blockage(
    item: dict,
    latest_render: dict | None,
    latest_publish: dict | None,
    artifacts: dict[str, Any],
) -> dict[str, Any] | None:
    if latest_publish and latest_publish.get("status") == "failed":
        return {
            "stage": "publish",
            "error_code": latest_publish.get("error_code"),
            "message": latest_publish.get("last_error") or "Publish job failed",
            "job_id": latest_publish["id"],
        }
    if latest_render and latest_render.get("status") == "failed":
        return {
            "stage": "render",
            "error_code": latest_render.get("error_code"),
            "message": "Render job failed",
            "job_id": latest_render["id"],
        }
    if item["status"] == "qa_failed":
        return {"stage": "qa", "message": "QA failed or held this item"}
    if item["status"] in {"rendered", "approved", "scheduled"}:
        missing = [
            name for name, present in (
                ("mp4", artifacts["mp4_exists"]),
                ("manifest", artifacts["manifest_exists"]),
            )
            if not present
        ]
        if missing:
            return {
                "stage": "artifact",
                "message": f"Missing artifact(s): {', '.join(missing)}",
            }
    return None


def _next_safe_command(
    item: dict,
    latest_render: dict | None,
    latest_publish: dict | None,
    artifacts: dict[str, Any],
) -> str | None:
    item_id = item["id"]
    status = item["status"]
    if status == "idea":
        return f"uv run profusion plan --item-id {item_id}"
    if status == "planned":
        return f"uv run profusion script --item-id {item_id}"
    if status == "scripted":
        if latest_render and latest_render.get("status") == "failed":
            return f"uv run profusion retry --render-job-id {latest_render['id']}"
        return f"uv run profusion render --item-id {item_id} --wait"
    if status == "rendered":
        return f"uv run profusion qa --item-id {item_id}"
    if status == "qa_failed":
        if artifacts["mp4_exists"] and artifacts["manifest_exists"]:
            return f"uv run profusion retry --item-id {item_id} --stage qa"
        return None
    if status == "qa_passed":
        return f"uv run profusion approve --item-id {item_id}"
    if status == "approved":
        return f"uv run profusion schedule --item-id {item_id} --at <iso-datetime> --target <platform:account-id>"
    if status == "scheduled":
        if latest_publish and latest_publish.get("status") == "failed":
            return f"uv run profusion retry --job-id {latest_publish['id']}"
        return "uv run profusion publish-due"
    if status == "published":
        return (
            f"uv run profusion measure record --item-id {item_id} "
            "--platform <workflow-type> --observation-type <outcome-type> --recorded-by <operator>"
        )
    return None


def _load_qa_report(artifacts: dict[str, Any]) -> dict[str, Any] | None:
    path = artifacts.get("qa_report_path")
    if not path:
        return None
    qa_path = Path(path)
    if not qa_path.exists():
        return None
    try:
        return json.loads(qa_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _first_or_none(rows: list[dict]) -> dict | None:
    return rows[0] if rows else None


def _git_state() -> dict[str, Any]:
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
        )
        return {"branch": branch, "sha": sha, "dirty": dirty}
    except Exception:
        return {"branch": None, "sha": None, "dirty": None}
