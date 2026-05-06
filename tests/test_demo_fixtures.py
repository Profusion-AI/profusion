"""Demo fixture helpers for static cockpit previews."""

from pathlib import Path

from orchestrator.db import get_all_items, get_approval_records, get_render_jobs_for_item
from orchestrator.demo_fixtures import (
    DEMO_CONTENT_VIDEO_ITEM_ID,
    seed_content_video_receipt_demo,
)
from orchestrator.receipts.generator import generate_content_video_receipt, receipts_payload


def test_seed_content_video_receipt_demo_creates_approved_item(tmp_path: Path):
    db_path = tmp_path / "content.db"
    renders_dir = tmp_path / "renders"

    item_id = seed_content_video_receipt_demo(db_path=db_path, renders_dir=renders_dir)

    assert item_id == DEMO_CONTENT_VIDEO_ITEM_ID
    item = [row for row in get_all_items(db_path) if row["id"] == item_id][0]
    assert item["status"] == "approved"
    assert item["source"] == "m7.5-demo-receipt"
    assert get_approval_records(db_path, item_id)[0]["decision"] == "approved"
    render_job = get_render_jobs_for_item(db_path, item_id)[0]
    assert render_job["status"] == "completed"
    assert Path(render_job["output_path"]).exists()
    assert (Path(render_job["output_path"]).parent / "manifest.json").exists()
    assert (Path(render_job["output_path"]).parent / "qa_report.json").exists()


def test_seed_content_video_receipt_demo_is_idempotent(tmp_path: Path):
    db_path = tmp_path / "content.db"
    renders_dir = tmp_path / "renders"

    seed_content_video_receipt_demo(db_path=db_path, renders_dir=renders_dir)
    seed_content_video_receipt_demo(db_path=db_path, renders_dir=renders_dir)

    demo_items = [
        row for row in get_all_items(db_path)
        if row["source"] == "m7.5-demo-receipt"
    ]
    assert len(demo_items) == 1


def test_seeded_demo_item_can_generate_receipt_packet(tmp_path: Path):
    db_path = tmp_path / "content.db"
    renders_dir = tmp_path / "renders"
    logs_dir = tmp_path / "logs"
    receipts_dir = tmp_path / "receipts"
    logs_dir.mkdir()

    item_id = seed_content_video_receipt_demo(db_path=db_path, renders_dir=renders_dir)
    generated = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=logs_dir,
        receipts_dir=receipts_dir,
        item_id=item_id,
    )

    payload = receipts_payload(receipts_dir=receipts_dir, item_id=item_id)
    assert payload["receipt_count"] == 1
    assert payload["receipts"][0]["receipt_id"] == generated.receipt_id
    assert "content-video-m75-demo" in generated.receipt_id
