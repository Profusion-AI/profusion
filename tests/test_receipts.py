"""M7.5 file-first reviewer receipt generation."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    init_db,
    insert_content_item,
    insert_publish_job,
    record_publish_complete,
    update_item_status,
)
from orchestrator.receipts.generator import (
    ReceiptEligibilityError,
    ReceiptTransitionError,
    generate_content_video_receipt,
    transition_receipt,
)
from tests.test_publish import _seed_approved_item, _use_tmp_db


def _use_receipt_tmp(monkeypatch, tmp_path: Path) -> Path:
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config

    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(config, "RECEIPTS_DIR", tmp_path / "receipts")
    return db_path


def test_content_video_receipt_packet_from_approved_item(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)

    receipt = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=tmp_path / "logs",
        receipts_dir=tmp_path / "receipts",
        item_id=item_id,
    )

    assert receipt.trust_domain == "media_trust"
    assert receipt.receipt_type == "content_video_receipt"
    assert receipt.receipt_status == "draft"
    assert receipt.subject_id == item_id
    assert receipt.packet_dir.exists()
    assert receipt.receipt_md.exists()
    assert receipt.summary_md.exists()
    assert receipt.limitations_md.exists()
    assert receipt.reviewer_notes_md.exists()
    assert receipt.evidence_json.exists()

    receipt_text = receipt.receipt_md.read_text(encoding="utf-8")
    assert "Profusion Content Video Receipt" in receipt_text
    assert "content workflow" in receipt_text
    assert "does not claim universal synthetic-media detection" in receipt_text
    assert "identity verification" in receipt_text
    assert "candidate ranking" not in receipt_text.lower()
    assert "hire/no-hire" not in receipt_text.lower()

    evidence = json.loads(receipt.evidence_json.read_text(encoding="utf-8"))
    assert evidence["receipt"]["receipt_status"] == "draft"
    assert evidence["receipt"]["receipt_type"] == "content_video_receipt"
    assert evidence["workflow"]["lifecycle_state"] == "approved"
    assert evidence["workflow"]["content_approval"]["decision"] == "approved"
    assert evidence["artifacts"]["mp4_exists"] is True
    assert evidence["artifacts"]["qa_report_exists"] is True


def test_content_video_receipt_preserves_publish_metadata(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    job_id = insert_publish_job(
        db_path,
        content_item_id=item_id,
        platform="youtube_shorts",
        title="Evidence demo",
    )
    record_publish_complete(
        db_path,
        content_item_id=item_id,
        job_id=job_id,
        published_url="https://example.com/demo",
        external_post_id="external-123",
    )

    receipt = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=tmp_path / "logs",
        receipts_dir=tmp_path / "receipts",
        item_id=item_id,
    )

    evidence = json.loads(receipt.evidence_json.read_text(encoding="utf-8"))
    latest_publish = evidence["workflow"]["latest_publish_job"]
    assert latest_publish["id"] == job_id
    assert latest_publish["platform"] == "youtube_shorts"
    assert latest_publish["status"] == "completed"
    assert latest_publish["published_url"] == "https://example.com/demo"
    assert latest_publish["external_post_id"] == "external-123"
    assert latest_publish["published_at"]


def test_content_video_receipt_refuses_pre_qa_item(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="too early")
    update_item_status(db_path, item_id, "planned")
    update_item_status(db_path, item_id, "scripted")

    with pytest.raises(ReceiptEligibilityError, match="qa_passed or later"):
        generate_content_video_receipt(
            db_path=db_path,
            logs_dir=tmp_path / "logs",
            receipts_dir=tmp_path / "receipts",
            item_id=item_id,
        )


def test_receipt_draft_cli_outputs_packet_paths(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)

    result = CliRunner().invoke(
        app,
        ["receipt", "draft", "--item-id", item_id, "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["receipt_type"] == "content_video_receipt"
    assert payload["receipt_status"] == "draft"
    assert payload["subject_id"] == item_id
    assert Path(payload["packet_dir"]).exists()
    assert Path(payload["receipt_md"]).exists()
    assert Path(payload["evidence_json"]).exists()


def test_receipt_list_cli_outputs_existing_drafts(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    generated = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=tmp_path / "logs",
        receipts_dir=tmp_path / "receipts",
        item_id=item_id,
    )

    result = CliRunner().invoke(
        app,
        ["receipt", "list", "--item-id", item_id, "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["item_id"] == item_id
    assert payload["receipt_count"] == 1
    assert payload["receipts"][0]["receipt_id"] == generated.receipt_id
    assert payload["receipts"][0]["receipt_status"] == "draft"


def test_receipt_transition_updates_evidence_and_packet_markdown(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    generated = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=tmp_path / "logs",
        receipts_dir=tmp_path / "receipts",
        item_id=item_id,
    )

    transitioned = transition_receipt(
        receipts_dir=tmp_path / "receipts",
        receipt_id=generated.receipt_id,
        to_status="reviewed",
    )

    assert transitioned["receipt_status"] == "reviewed"
    assert transitioned["status_history"][-1]["from_status"] == "draft"
    assert transitioned["status_history"][-1]["to_status"] == "reviewed"

    evidence = json.loads(generated.evidence_json.read_text(encoding="utf-8"))
    assert evidence["receipt"]["receipt_status"] == "reviewed"
    assert evidence["limitations"][-1] == (
        "Receipt status is separate from content approval. "
        "Current receipt status: reviewed."
    )
    assert "- Status: `reviewed`" in generated.summary_md.read_text(encoding="utf-8")
    assert "- Receipt status: `reviewed`" in generated.receipt_md.read_text(encoding="utf-8")
    assert "draft -> reviewed" in generated.reviewer_notes_md.read_text(encoding="utf-8")


def test_receipt_transition_refuses_skipped_lifecycle_step(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    generated = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=tmp_path / "logs",
        receipts_dir=tmp_path / "receipts",
        item_id=item_id,
    )

    with pytest.raises(ReceiptTransitionError, match="draft to approved_for_packet"):
        transition_receipt(
            receipts_dir=tmp_path / "receipts",
            receipt_id=generated.receipt_id,
            to_status="approved_for_packet",
        )


def test_receipt_transition_cli_outputs_updated_status(monkeypatch, tmp_path):
    db_path = _use_receipt_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    generated = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=tmp_path / "logs",
        receipts_dir=tmp_path / "receipts",
        item_id=item_id,
    )

    result = CliRunner().invoke(
        app,
        [
            "receipt",
            "transition",
            "--receipt-id",
            generated.receipt_id,
            "--to",
            "reviewed",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["receipt_id"] == generated.receipt_id
    assert payload["receipt_status"] == "reviewed"
