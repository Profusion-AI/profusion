"""profusion approve CLI tests — atomic approval decision."""

from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    get_all_items,
    get_approval_records,
    init_db,
    insert_content_brief,
    insert_content_item,
    insert_script_variant,
    update_item_status,
)


def _use_tmp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


def _seed_qa_passed_item(db_path: Path) -> str:
    item_id = insert_content_item(db_path, topic="qa passed item")
    update_item_status(db_path, item_id, "planned")
    insert_content_brief(
        db_path,
        content_item_id=item_id,
        thesis="thesis",
        angle=None,
        hook_options=[],
        cta=None,
        claims_to_verify=[],
        brand_notes=None,
        risk_flags=[],
        source_refs=[],
    )
    update_item_status(db_path, item_id, "scripted")
    insert_script_variant(
        db_path,
        content_item_id=item_id,
        variant_name="straight_explainer",
        script_text="Script.",
    )
    update_item_status(db_path, item_id, "rendered")
    update_item_status(db_path, item_id, "qa_passed")
    return item_id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_approve_refuses_non_qa_passed_status(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="just scripted")
    update_item_status(db_path, item_id, "planned")
    update_item_status(db_path, item_id, "scripted")
    result = CliRunner().invoke(app, ["approve", "--item-id", item_id])
    assert result.exit_code != 0
    assert result.exception is None or isinstance(result.exception, SystemExit), (
        f"Unexpected exception: {result.exception}"
    )
    assert "[error]" in result.output
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "scripted"


def test_approve_approved_transitions_to_approved(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_qa_passed_item(db_path)
    result = CliRunner().invoke(app, ["approve", "--item-id", item_id, "--decision", "approved"])
    assert result.exit_code == 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"
    records = get_approval_records(db_path, item_id)
    assert len(records) == 1
    assert records[0]["decision"] == "approved"


def test_approve_rejected_archives_item(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_qa_passed_item(db_path)
    result = CliRunner().invoke(app, ["approve", "--item-id", item_id, "--decision", "rejected"])
    assert result.exit_code == 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "archived"
    records = get_approval_records(db_path, item_id)
    assert records[0]["decision"] == "rejected"


def test_approve_revision_requested_returns_to_scripted(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_qa_passed_item(db_path)
    result = CliRunner().invoke(
        app, ["approve", "--item-id", item_id, "--decision", "revision_requested"]
    )
    assert result.exit_code == 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "scripted"
    records = get_approval_records(db_path, item_id)
    assert records[0]["decision"] == "revision_requested"


def test_approve_notes_stored(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_qa_passed_item(db_path)
    CliRunner().invoke(
        app,
        ["approve", "--item-id", item_id, "--decision", "rejected", "--notes", "fix hook"],
    )
    records = get_approval_records(db_path, item_id)
    assert records[0]["notes"] == "fix hook"


def test_approve_invalid_decision_exits(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_qa_passed_item(db_path)
    result = CliRunner().invoke(
        app, ["approve", "--item-id", item_id, "--decision", "gibberish"]
    )
    assert result.exit_code == 2
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_passed"


def test_approve_is_atomic(monkeypatch, tmp_path):
    """Approval record exists AND final status is set — no intermediate state observable."""
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_qa_passed_item(db_path)
    result = CliRunner().invoke(app, ["approve", "--item-id", item_id, "--decision", "approved"])
    assert result.exit_code == 0
    records = get_approval_records(db_path, item_id)
    assert len(records) == 1
    assert records[0]["decision"] == "approved"
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"
    # awaiting_approval must never be the resting state
    assert items[0]["status"] != "awaiting_approval"


def test_approve_advances_updated_at(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_qa_passed_item(db_path)
    # Pin updated_at to a known past value so the comparison is reliable regardless of clock resolution
    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(str(db_path))
    conn.execute(
        "UPDATE content_items SET updated_at = '2000-01-01 00:00:00' WHERE id = ?",
        (item_id,),
    )
    conn.commit()
    conn.close()
    before = "2000-01-01 00:00:00"
    result = CliRunner().invoke(app, ["approve", "--item-id", item_id, "--decision", "approved"])
    assert result.exit_code == 0
    after = [i for i in get_all_items(db_path) if i["id"] == item_id][0]["updated_at"]
    assert after > before
