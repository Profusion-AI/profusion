"""Explicit demo fixtures for static cockpit preview builds.

These helpers seed local, clearly labeled demo data. They do not replace the
normal operator workflow and should not be used as evidence that live vendor
rendering or publishing ran.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from orchestrator import db

DEMO_CONTENT_VIDEO_ITEM_ID = "m75-demo-content-video-receipt"
DEMO_CONTENT_VIDEO_RENDER_TASK_ID = "m75-demo-render-001"
DEMO_CONTENT_VIDEO_VARIANT_ID = "m75-demo-variant-001"
DEMO_CONTENT_VIDEO_BRIEF_ID = "m75-demo-brief-001"
DEMO_CONTENT_VIDEO_APPROVAL_ID = "m75-demo-approval-001"


def seed_content_video_receipt_demo(*, db_path: Path, renders_dir: Path) -> str:
    """Create an approved demo content item suitable for a draft receipt packet."""

    db.init_db(db_path)
    existing = db.get_item(db_path, DEMO_CONTENT_VIDEO_ITEM_ID)
    if existing is not None:
        _write_demo_artifacts(renders_dir=renders_dir)
        return DEMO_CONTENT_VIDEO_ITEM_ID

    db.insert_content_item(
        db_path,
        item_id=DEMO_CONTENT_VIDEO_ITEM_ID,
        topic="Demo: governed AI video workflow receipt",
        pillar="media_trust",
        audience="pilot_reviewer",
        priority=9,
        source="m7.5-demo-receipt",
    )
    db.update_item_status(db_path, DEMO_CONTENT_VIDEO_ITEM_ID, "planned")
    db.insert_content_brief(
        db_path,
        brief_id=DEMO_CONTENT_VIDEO_BRIEF_ID,
        content_item_id=DEMO_CONTENT_VIDEO_ITEM_ID,
        thesis=(
            "A reviewer should be able to inspect the workflow evidence behind "
            "an AI-assisted content artifact without treating it as identity or "
            "liveness verification."
        ),
        angle="Evidence packet, not detector claim.",
        hook_options=[
            "What if the useful artifact is not the video itself, but the receipt behind it?"
        ],
        cta="Review the evidence packet before external delivery.",
        claims_to_verify=[],
        brand_notes="M7.5 demo fixture for static cockpit preview only.",
        risk_flags=[],
        source_refs=[],
    )
    db.update_item_status(db_path, DEMO_CONTENT_VIDEO_ITEM_ID, "scripted")
    db.insert_script_variant(
        db_path,
        variant_id=DEMO_CONTENT_VIDEO_VARIANT_ID,
        content_item_id=DEMO_CONTENT_VIDEO_ITEM_ID,
        variant_name="receipt_demo_explainer",
        script_text=(
            "Profusion records the declared workflow, artifacts, QA checks, "
            "approval state, and limitations for this content workflow."
        ),
        duration_target_seconds=45,
    )
    mp4_path = _write_demo_artifacts(renders_dir=renders_dir)
    db.insert_render_job(
        db_path,
        task_id=DEMO_CONTENT_VIDEO_RENDER_TASK_ID,
        script_variant_id=DEMO_CONTENT_VIDEO_VARIANT_ID,
        render_profile={"fixture": "m7.5-demo-receipt"},
    )
    db.update_render_job(
        db_path,
        DEMO_CONTENT_VIDEO_RENDER_TASK_ID,
        status="completed",
        output_path=str(mp4_path),
    )
    db.update_item_status(db_path, DEMO_CONTENT_VIDEO_ITEM_ID, "rendered")
    db.update_item_status(db_path, DEMO_CONTENT_VIDEO_ITEM_ID, "qa_passed")
    db.record_approval_decision(
        db_path,
        record_id=DEMO_CONTENT_VIDEO_APPROVAL_ID,
        content_item_id=DEMO_CONTENT_VIDEO_ITEM_ID,
        decision="approved",
        approved_by="m7.5-demo-fixture",
        notes="Approved only as a static cockpit reviewer-evidence demo fixture.",
    )
    return DEMO_CONTENT_VIDEO_ITEM_ID


def _write_demo_artifacts(*, renders_dir: Path) -> Path:
    render_dir = renders_dir / DEMO_CONTENT_VIDEO_RENDER_TASK_ID
    render_dir.mkdir(parents=True, exist_ok=True)
    mp4_path = render_dir / "final.mp4"
    if not mp4_path.exists() or mp4_path.stat().st_size == 0:
        mp4_path.write_bytes(b"PROFUSION_M75_DEMO_MP4_PLACEHOLDER\n")

    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "content_item_id": DEMO_CONTENT_VIDEO_ITEM_ID,
        "script_variant_id": DEMO_CONTENT_VIDEO_VARIANT_ID,
        "task_id": DEMO_CONTENT_VIDEO_RENDER_TASK_ID,
        "output_path": str(mp4_path),
        "fixture": "m7.5-demo-receipt",
        "created_at": created_at,
    }
    qa_report = {
        "content_item_id": DEMO_CONTENT_VIDEO_ITEM_ID,
        "task_id": DEMO_CONTENT_VIDEO_RENDER_TASK_ID,
        "overall_go_no_go": "go",
        "risk_flags": [],
        "claims_to_verify": [],
        "fixture": "m7.5-demo-receipt",
        "created_at": created_at,
    }
    (render_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (render_dir / "qa_report.json").write_text(
        json.dumps(qa_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return mp4_path
