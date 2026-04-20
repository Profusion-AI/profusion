"""Conservative retry operations for failed pipeline work."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from orchestrator import db
from orchestrator.adapters import turbo, v2
from orchestrator.diagnostics import write_diagnostic


class RetryError(RuntimeError):
    """Raised when a requested retry is unsafe or impossible."""


def retry_publish_job(
    db_path: Path,
    logs_dir: Path,
    *,
    job_id: str,
    api_key: str,
) -> dict[str, Any]:
    job = db.get_publish_job(db_path, job_id)
    if job is None:
        raise RetryError(f"Publish job {job_id!r} not found")
    if job["status"] == "completed":
        raise RetryError("Completed publish jobs cannot be retried")
    if job["status"] != "failed":
        raise RetryError(f"Publish job is {job['status']!r}; only failed jobs are retryable")

    item = db.get_item(db_path, job["content_item_id"])
    if item is None:
        raise RetryError("Parent content item not found")

    if job.get("scheduled_for"):
        if item["status"] != "scheduled":
            raise RetryError(
                f"Scheduled publish retry requires parent item status 'scheduled', got {item['status']!r}"
            )
        db.requeue_failed_scheduled_publish_job(db_path, job_id)
        return {
            "action": "requeued_scheduled_job",
            "job_id": job_id,
            "next_safe_command": "uv run profusion publish-due",
        }

    if item["status"] != "approved":
        raise RetryError(
            f"Immediate publish retry requires parent item status 'approved', got {item['status']!r}"
        )
    if not api_key:
        raise RetryError("POST_BRIDGE_API_KEY is not set in .env")

    mp4_path = _validated_publish_video(db_path, item)
    new_job_id = db.insert_publish_job(
        db_path,
        content_item_id=item["id"],
        platform=job["platform"],
        account_id=int(job["account_id"]) if job.get("account_id") is not None else None,
        title=job.get("title") or item.get("topic", ""),
        description=job.get("description") or "",
        platform_metadata=_json_dict(job.get("platform_metadata")),
        retry_of_job_id=job_id,
        attempt_group_id=job.get("attempt_group_id") or job_id,
    )
    profile = v2.PublishProfile(
        platform=job["platform"],
        account_id=int(job["account_id"]),
        api_key=api_key,
        title=job.get("title") or item.get("topic", ""),
        description=job.get("description") or "",
    )
    try:
        result = v2.publish(str(mp4_path), profile)
        db.record_publish_complete(
            db_path,
            content_item_id=item["id"],
            job_id=new_job_id,
            published_url=result.published_url,
            external_post_id=result.external_post_id,
        )
    except Exception as exc:
        log_path, _ = write_diagnostic(
            logs_dir,
            stage="publish",
            item_id=item["id"],
            job_id=new_job_id,
            attempt=(job.get("attempt_count") or 0) + 1,
            error=exc,
            error_code=type(exc).__name__,
            context={"retry_of_job_id": job_id, "platform": job["platform"]},
        )
        db.mark_publish_job_failed(
            db_path,
            new_job_id,
            str(exc),
            error_code=type(exc).__name__,
            log_path=log_path,
        )
        raise RetryError(f"Retry publish attempt failed: {exc}") from exc

    return {
        "action": "created_immediate_retry_attempt",
        "old_job_id": job_id,
        "new_job_id": new_job_id,
        "published_url": result.published_url,
        "external_post_id": result.external_post_id,
    }


def retry_render_job(
    db_path: Path,
    logs_dir: Path,
    *,
    render_job_id: str,
) -> dict[str, Any]:
    job = db.get_render_job_with_item(db_path, render_job_id)
    if job is None:
        raise RetryError(f"Render job {render_job_id!r} not found")
    if job["status"] == "completed":
        raise RetryError("Completed render jobs cannot be retried")
    if job["status"] != "failed":
        raise RetryError(f"Render job is {job['status']!r}; only failed jobs are retryable")
    if job["item_status"] != "scripted":
        raise RetryError(
            f"Render retry requires parent item status 'scripted', got {job['item_status']!r}"
        )

    profile = turbo.RenderProfile()
    try:
        result = turbo.render(
            subject=job["topic"],
            script=job["script_text"],
            profile=profile,
        )
        db.insert_render_job(
            db_path,
            task_id=result.task_id,
            script_variant_id=job["script_variant_id"],
            render_profile=asdict(profile),
            retry_of_job_id=render_job_id,
            attempt_group_id=job.get("attempt_group_id") or render_job_id,
        )
    except Exception as exc:
        log_path, _ = write_diagnostic(
            logs_dir,
            stage="render",
            item_id=job["content_item_id"],
            job_id=render_job_id,
            error=exc,
            error_code=type(exc).__name__,
            context={"variant_name": job["variant_name"]},
        )
        db.update_render_job(
            db_path,
            render_job_id,
            status="failed",
            log_path=log_path,
            error_code=type(exc).__name__,
        )
        raise RetryError(f"Render retry submission failed: {exc}") from exc

    return {
        "action": "created_render_retry_attempt",
        "old_render_job_id": render_job_id,
        "new_render_job_id": result.task_id,
        "next_safe_command": f"uv run profusion render --item-id {job['content_item_id']} --variant {job['variant_name']} --wait",
    }


def retry_qa_stage(db_path: Path, *, item_id: str) -> dict[str, Any]:
    item = db.get_item(db_path, item_id)
    if item is None:
        raise RetryError(f"Content item {item_id!r} not found")
    if item["status"] != "qa_failed":
        raise RetryError(f"QA retry requires item status 'qa_failed', got {item['status']!r}")
    render_job = db.get_completed_render_job_for_item(db_path, item_id)
    if render_job is None:
        raise RetryError("No completed render job is available for QA retry")
    if not render_job.get("output_path"):
        raise RetryError("Completed render job has no output_path")
    mp4_path = Path(render_job["output_path"])
    if not mp4_path.exists() or mp4_path.stat().st_size == 0:
        raise RetryError(f"Render artifact missing or empty: {mp4_path}")
    manifest = mp4_path.parent / "manifest.json"
    if not manifest.exists():
        raise RetryError(f"manifest.json not found at {manifest}")
    db.update_item_status(db_path, item_id, "rendered")
    return {
        "action": "returned_to_rendered_for_qa",
        "item_id": item_id,
        "next_safe_command": f"uv run profusion qa --item-id {item_id}",
    }


def _validated_publish_video(db_path: Path, item: dict) -> Path:
    render_job = db.get_completed_render_job_for_item(db_path, item["id"])
    if render_job is None:
        raise RetryError("No completed render job found")
    if not render_job.get("output_path"):
        raise RetryError("Render job has no output_path")
    mp4 = Path(render_job["output_path"])
    if not mp4.exists() or mp4.stat().st_size == 0:
        raise RetryError(f"Render artifact missing or empty: {mp4}")
    if not (mp4.parent / "manifest.json").exists():
        raise RetryError(f"manifest.json not found at {mp4.parent / 'manifest.json'}")
    if not (mp4.parent / "qa_report.json").exists():
        raise RetryError(f"qa_report.json not found at {mp4.parent / 'qa_report.json'}")
    return mp4


def _json_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        loaded = json.loads(value)
    except ValueError:
        return {}
    return loaded if isinstance(loaded, dict) else {}
