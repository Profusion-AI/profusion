"""profusion qa CLI tests — Claude adapter and filesystem are mocked."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    get_all_items,
    init_db,
    insert_content_brief,
    insert_content_item,
    insert_render_job,
    insert_script_variant,
    update_item_status,
    update_render_job,
)

TASK_ID = "turbo-task-qa-001"


def _use_tmp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


def _seed_rendered_item(db_path: Path, tmp_path: Path, task_id: str = TASK_ID) -> tuple[str, str, str]:
    """Return (item_id, variant_id, mp4_path)."""
    item_id = insert_content_item(db_path, topic="test topic")
    update_item_status(db_path, item_id, "planned")
    insert_content_brief(
        db_path,
        content_item_id=item_id,
        thesis="thesis",
        angle=None,
        hook_options=["hook1"],
        cta=None,
        claims_to_verify=[{"claim": "x", "why_it_matters": "y", "suggested_source_type": "z"}],
        brand_notes=None,
        risk_flags=[],
        source_refs=[],
    )
    update_item_status(db_path, item_id, "scripted")
    variant_id = insert_script_variant(
        db_path,
        content_item_id=item_id,
        variant_name="straight_explainer",
        script_text="Script body.",
    )
    renders_dir = tmp_path / "renders" / task_id
    renders_dir.mkdir(parents=True)
    mp4_path = renders_dir / "final.mp4"
    mp4_path.write_bytes(b"FAKE_MP4_BYTES")
    manifest = {
        "content_item_id": item_id,
        "script_variant_id": variant_id,
        "task_id": task_id,
        "output_path": str(mp4_path),
        "created_at": "2024-01-01T00:00:00Z",
    }
    (renders_dir / "manifest.json").write_text(json.dumps(manifest))
    job_id = insert_render_job(
        db_path,
        task_id=task_id,
        script_variant_id=variant_id,
        render_profile={},
    )
    update_render_job(db_path, task_id, status="completed", output_path=str(mp4_path))
    update_item_status(db_path, item_id, "rendered")
    return item_id, variant_id, str(mp4_path)


def _go_response() -> str:
    return json.dumps({
        "risk_flags": [],
        "claims_to_verify": [],
        "overall_go_no_go": "go",
    })


def _hold_response() -> str:
    return json.dumps({
        "risk_flags": [
            {"category": "factual", "description": "claim unverifiable", "mitigation": "verify first"}
        ],
        "claims_to_verify": [],
        "overall_go_no_go": "hold",
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_qa_refuses_non_rendered_status(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="still an idea")
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    items = [i for i in __import__("orchestrator.db", fromlist=["get_all_items"]).get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "idea"


def test_qa_fails_if_no_completed_render_job(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="test")
    update_item_status(db_path, item_id, "planned")
    update_item_status(db_path, item_id, "scripted")
    update_item_status(db_path, item_id, "rendered")
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "rendered"


def test_qa_fails_if_mp4_missing(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    Path(mp4_path).unlink()
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_fails_if_mp4_empty(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    Path(mp4_path).write_bytes(b"")
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_fails_if_manifest_missing(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    (Path(mp4_path).parent / "manifest.json").unlink()
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_fails_on_manifest_content_item_id_mismatch(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    manifest_path = Path(mp4_path).parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["content_item_id"] = "wrong-id"
    manifest_path.write_text(json.dumps(manifest))
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    assert "content_item_id" in result.output
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_fails_on_manifest_task_id_mismatch(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    manifest_path = Path(mp4_path).parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["task_id"] = "wrong-task-id"
    manifest_path.write_text(json.dumps(manifest))
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    assert "task_id" in result.output
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_fails_on_manifest_variant_id_mismatch(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    manifest_path = Path(mp4_path).parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["script_variant_id"] = "wrong-variant-id"
    manifest_path.write_text(json.dumps(manifest))
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    assert "script_variant_id" in result.output
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_fails_on_manifest_output_path_mismatch(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    manifest_path = Path(mp4_path).parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["output_path"] = "/totally/wrong/path.mp4"
    manifest_path.write_text(json.dumps(manifest))
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    assert "output_path" in result.output
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_passes_on_go(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    from orchestrator.adapters import claude
    monkeypatch.setattr(claude, "generate", lambda **_: _go_response())
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code == 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_passed"


def test_qa_fails_on_hold(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    from orchestrator.adapters import claude
    monkeypatch.setattr(claude, "generate", lambda **_: _hold_response())
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_report_written_before_state_advance(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    from orchestrator.adapters import claude
    monkeypatch.setattr(claude, "generate", lambda **_: _go_response())
    CliRunner().invoke(app, ["qa", "--item-id", item_id])
    report_path = Path(mp4_path).parent / "qa_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text())
    assert report["content_item_id"] == item_id
    assert report["overall_go_no_go"] == "go"
    assert "task_id" in report
    assert "created_at" in report

    # Also written on hold verdict
    db_path2 = _use_tmp_db(monkeypatch, tmp_path / "hold")
    init_db(db_path2)
    item_id2, variant_id2, mp4_path2 = _seed_rendered_item(db_path2, tmp_path / "hold")
    monkeypatch.setattr(claude, "generate", lambda **_: _hold_response())
    CliRunner().invoke(app, ["qa", "--item-id", item_id2])
    assert (Path(mp4_path2).parent / "qa_report.json").exists()


def test_qa_report_write_failure_stays_rendered(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    from orchestrator.adapters import claude
    monkeypatch.setattr(claude, "generate", lambda **_: _go_response())

    original_write_text = Path.write_text

    def fail_on_qa_report(self, *args, **kwargs):
        if self.name == "qa_report.json":
            raise OSError("disk full")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_on_qa_report)
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    assert "qa_report" in result.output or "Failed" in result.output
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "rendered"


def test_qa_adapter_exception_stays_rendered(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    from orchestrator.adapters import claude
    monkeypatch.setattr(claude, "generate", lambda **_: (_ for _ in ()).throw(Exception("network error")))
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "rendered"


def test_qa_fails_on_null_output_path(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    # Null out output_path directly — update_render_job uses COALESCE so None is a no-op
    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(str(db_path))
    conn.execute("UPDATE render_jobs SET output_path = NULL WHERE id = ?", (TASK_ID,))
    conn.commit()
    conn.close()
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"


def test_qa_fails_on_corrupted_brief_json(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, variant_id, mp4_path = _seed_rendered_item(db_path, tmp_path)
    # Corrupt claims_to_verify in the DB directly
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "UPDATE content_briefs SET claims_to_verify = ? WHERE content_item_id = ?",
        ("{not valid json{{", item_id),
    )
    conn.commit()
    conn.close()
    result = CliRunner().invoke(app, ["qa", "--item-id", item_id])
    assert result.exit_code != 0
    from orchestrator.db import get_all_items
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "qa_failed"
