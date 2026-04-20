"""profusion publish CLI tests — V2 adapter mocked."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    get_all_items,
    get_publish_jobs_for_item,
    init_db,
    insert_content_brief,
    insert_content_item,
    insert_render_job,
    insert_script_variant,
    record_approval_decision,
    update_item_status,
    update_render_job,
)

TASK_ID = "turbo-task-pub-001"
PLATFORM = "youtube_shorts"
ACCOUNT_ID = "99"


def _use_tmp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "POST_BRIDGE_API_KEY", "test-api-key")
    return db_path


def _seed_approved_item(db_path: Path, tmp_path: Path, task_id: str = TASK_ID) -> tuple[str, str, str]:
    """Seed a fully approved item. Returns (item_id, variant_id, mp4_path)."""
    item_id = insert_content_item(db_path, topic="publish test topic")
    update_item_status(db_path, item_id, "planned")
    insert_content_brief(
        db_path,
        content_item_id=item_id,
        thesis="thesis",
        angle=None,
        hook_options=["hook"],
        cta=None,
        claims_to_verify=[],
        brand_notes=None,
        risk_flags=[],
        source_refs=[],
    )
    update_item_status(db_path, item_id, "scripted")
    variant_id = insert_script_variant(
        db_path,
        content_item_id=item_id,
        variant_name="straight_explainer",
        script_text="Script.",
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

    qa_report = {
        "content_item_id": item_id,
        "task_id": task_id,
        "overall_go_no_go": "go",
        "risk_flags": [],
        "claims_to_verify": [],
        "created_at": "2024-01-01T00:00:00Z",
    }
    (renders_dir / "qa_report.json").write_text(json.dumps(qa_report))

    insert_render_job(db_path, task_id=task_id, script_variant_id=variant_id, render_profile={})
    update_render_job(db_path, task_id, status="completed", output_path=str(mp4_path))
    update_item_status(db_path, item_id, "rendered")
    update_item_status(db_path, item_id, "qa_passed")
    record_approval_decision(
        db_path,
        content_item_id=item_id,
        decision="approved",
        approved_by="operator",
    )
    return item_id, variant_id, str(mp4_path)


def _publish_args(item_id: str) -> list[str]:
    return ["publish", "--item-id", item_id, "--platform", PLATFORM, "--account-id", ACCOUNT_ID]


def _mock_v2_success(monkeypatch) -> None:
    from orchestrator.adapters.v2 import PublishResult
    mock_result = PublishResult(
        platform=PLATFORM,
        external_post_id="post-999",
        published_url="https://youtube.com/shorts/xyz",
    )
    monkeypatch.setattr("orchestrator.adapters.v2.publish", lambda *a, **kw: mock_result)


# ---------------------------------------------------------------------------
# Package validation tests
# ---------------------------------------------------------------------------

def test_publish_refuses_non_approved_status(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="not approved")
    update_item_status(db_path, item_id, "planned")
    update_item_status(db_path, item_id, "scripted")
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "[error]" in result.output
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "scripted"


def test_publish_fails_if_no_completed_render_job(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="approved no render")
    for s in ("planned", "scripted", "rendered", "qa_passed"):
        update_item_status(db_path, item_id, s)
    record_approval_decision(db_path, content_item_id=item_id, decision="approved", approved_by="op")
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    assert "[error]" in result.output
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"


def test_publish_fails_if_mp4_missing(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    Path(mp4_path).unlink()
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    assert "[error]" in result.output
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"


def test_publish_fails_if_mp4_empty(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    Path(mp4_path).write_bytes(b"")
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"


def test_publish_fails_if_manifest_missing(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    (Path(mp4_path).parent / "manifest.json").unlink()
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"


def test_publish_fails_if_qa_report_missing(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    (Path(mp4_path).parent / "qa_report.json").unlink()
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"


def test_publish_fails_if_no_approved_record(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    # Override the approval record decision to rejected
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    conn.execute("UPDATE approval_records SET decision = 'rejected' WHERE content_item_id = ?", (item_id,))
    conn.commit()
    conn.close()
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    assert "[error]" in result.output


def test_publish_fails_if_no_api_key(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config
    monkeypatch.setattr(config, "POST_BRIDGE_API_KEY", "")
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    assert "POST_BRIDGE_API_KEY" in result.output


# ---------------------------------------------------------------------------
# Publish job lifecycle
# ---------------------------------------------------------------------------

def test_publish_creates_pending_job_before_adapter(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)

    captured = {}

    def capturing_publish(video_path, profile, **kw):
        jobs = get_publish_jobs_for_item(db_path, item_id)
        captured["jobs_before"] = jobs
        from orchestrator.adapters.v2 import PublishResult
        return PublishResult(platform=PLATFORM, external_post_id="p1", published_url=None)

    monkeypatch.setattr("orchestrator.adapters.v2.publish", capturing_publish)
    CliRunner().invoke(app, _publish_args(item_id))

    assert len(captured["jobs_before"]) == 1
    assert captured["jobs_before"][0]["status"] == "pending"


def test_publish_success_transitions_to_published(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    _mock_v2_success(monkeypatch)

    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code == 0
    assert "[published]" in result.output

    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "published"

    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert jobs[0]["status"] == "completed"
    assert jobs[0]["external_post_id"] == "post-999"
    assert jobs[0]["published_url"] == "https://youtube.com/shorts/xyz"


def test_publish_adapter_exception_stays_approved(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)

    from orchestrator.adapters.v2 import V2PublishError
    monkeypatch.setattr(
        "orchestrator.adapters.v2.publish",
        lambda *a, **kw: (_ for _ in ()).throw(V2PublishError("network error")),
    )
    result = CliRunner().invoke(app, _publish_args(item_id))
    assert result.exit_code != 0
    assert "[error]" in result.output

    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"

    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert jobs[0]["status"] == "failed"


def test_publish_scheduled_never_resting_state(monkeypatch, tmp_path):
    """approved → scheduled → published happens atomically; 'scheduled' is never the final status."""
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    _mock_v2_success(monkeypatch)

    CliRunner().invoke(app, _publish_args(item_id))

    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "published"
    assert items[0]["status"] != "scheduled"
