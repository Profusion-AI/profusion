"""profusion render CLI tests — Turbo calls and MP4 download are mocked."""

import json
from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    get_all_items,
    get_render_job,
    get_render_jobs_by_variant,
    get_script_variants,
    init_db,
    insert_content_brief,
    insert_content_item,
    insert_render_job,
    insert_script_variant,
    update_item_status,
)

TASK_ID = "turbo-task-abc-123"


def _use_tmp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


def _seed_scripted_item(db_path: Path) -> str:
    item_id = insert_content_item(db_path, topic="schools vs learning")
    update_item_status(db_path, item_id, "planned")
    insert_content_brief(
        db_path,
        content_item_id=item_id,
        thesis="x",
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
        script_text="Script body.",
        duration_target_seconds=60,
    )
    return item_id


def _fake_render(monkeypatch, task_id: str = TASK_ID) -> None:
    from orchestrator.adapters import turbo
    monkeypatch.setattr(
        turbo, "render",
        lambda **_: turbo.RenderJobResult(task_id=task_id, status="pending"),
    )


def _fake_status(monkeypatch, status: str = "completed", output_url: str | None = None) -> None:
    from orchestrator.adapters import turbo
    monkeypatch.setattr(
        turbo, "get_job_status",
        lambda tid: turbo.RenderJobResult(
            task_id=tid, status=status, output_url=output_url, progress=100
        ),
    )


def _fake_mp4_download(monkeypatch) -> None:
    import httpx

    class _FakeResp:
        content = b"FAKE_MP4_BYTES"
        status_code = 200

        def raise_for_status(self) -> None:
            pass

    monkeypatch.setattr(httpx, "get", lambda *a, **kw: _FakeResp())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_render_refuses_non_scripted_status(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="still an idea")
    _fake_render(monkeypatch)
    result = CliRunner().invoke(app, ["render", "--item-id", item_id])
    assert result.exit_code != 0
    assert "scripted" in result.output.lower() or "Invalid" in result.output


def test_render_requires_existing_variants(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="scripted but no variants")
    update_item_status(db_path, item_id, "scripted")
    _fake_render(monkeypatch)
    result = CliRunner().invoke(app, ["render", "--item-id", item_id])
    assert result.exit_code != 0
    assert "script" in result.output.lower()


def test_render_rejects_unknown_variant(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    _fake_render(monkeypatch)
    result = CliRunner().invoke(
        app, ["render", "--item-id", item_id, "--variant", "no_such_variant"]
    )
    assert result.exit_code != 0
    assert "no_such_variant" in result.output


def test_render_no_wait_stores_pending_job(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    _fake_render(monkeypatch)
    result = CliRunner().invoke(app, ["render", "--item-id", item_id])
    assert result.exit_code == 0, result.output
    job = get_render_job(db_path, TASK_ID)
    assert job is not None
    assert job["status"] == "pending"
    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "scripted"


def test_render_wait_happy_path(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    _fake_render(monkeypatch)
    _fake_status(monkeypatch, status="completed", output_url="http://turbo/final.mp4")
    _fake_mp4_download(monkeypatch)
    monkeypatch.setattr("time.sleep", lambda _: None)
    monkeypatch.setattr(config, "RENDERS_DIR", tmp_path / "renders")
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")

    result = CliRunner().invoke(app, ["render", "--item-id", item_id, "--wait"])
    assert result.exit_code == 0, result.output

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "rendered"

    job = get_render_job(db_path, TASK_ID)
    assert job["status"] == "completed"
    assert job["output_path"] is not None

    manifest_path = tmp_path / "renders" / TASK_ID / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["content_item_id"] == item_id
    assert manifest["task_id"] == TASK_ID
    assert "render_profile" in manifest
    assert "output_path" in manifest


def test_render_wait_failed_job_leaves_item_scripted(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    _fake_render(monkeypatch)
    _fake_status(monkeypatch, status="failed")
    monkeypatch.setattr("time.sleep", lambda _: None)
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")

    result = CliRunner().invoke(app, ["render", "--item-id", item_id, "--wait"])
    assert result.exit_code != 0

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "scripted"

    job = get_render_job(db_path, TASK_ID)
    assert job["status"] == "failed"
    assert job["log_path"] is not None


def test_render_wait_polls_exhausted(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    _fake_render(monkeypatch)
    _fake_status(monkeypatch, status="processing")
    monkeypatch.setattr("time.sleep", lambda _: None)
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")

    result = CliRunner().invoke(
        app, ["render", "--item-id", item_id, "--wait", "--max-polls", "2"]
    )
    assert result.exit_code != 0

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "scripted"

    job = get_render_job(db_path, TASK_ID)
    assert job["status"] == "failed"


def test_render_duplicate_guard(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    sv = get_script_variants(db_path, item_id)[0]
    insert_render_job(
        db_path, task_id="existing-job", script_variant_id=sv["id"], render_profile={}
    )
    _fake_render(monkeypatch)

    result = CliRunner().invoke(app, ["render", "--item-id", item_id])
    assert result.exit_code == 0
    assert "existing-job" in result.output

    jobs = get_render_jobs_by_variant(db_path, sv["id"])
    assert len(jobs) == 1


def test_render_force_bypasses_duplicate_guard(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    sv = get_script_variants(db_path, item_id)[0]
    insert_render_job(
        db_path, task_id="existing-job", script_variant_id=sv["id"], render_profile={}
    )
    _fake_render(monkeypatch)

    result = CliRunner().invoke(app, ["render", "--item-id", item_id, "--force"])
    assert result.exit_code == 0

    jobs = get_render_jobs_by_variant(db_path, sv["id"])
    assert len(jobs) == 2


def test_render_turbo_unavailable_exits_cleanly(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    from orchestrator.adapters import turbo
    monkeypatch.setattr(
        turbo, "render",
        lambda **_: (_ for _ in ()).throw(turbo.TurboUnavailableError("offline")),
    )
    result = CliRunner().invoke(app, ["render", "--item-id", item_id])
    assert result.exit_code != 0
    assert result.exception is None or "Traceback" not in result.output


def test_render_duplicate_guard_with_wait_resumes_polling(monkeypatch, tmp_path):
    """--wait on a dup skips submission and polls the existing job."""
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    sv = get_script_variants(db_path, item_id)[0]
    insert_render_job(
        db_path, task_id=TASK_ID, script_variant_id=sv["id"], render_profile={}
    )
    _fake_status(monkeypatch, status="completed", output_url="http://turbo/final.mp4")
    _fake_mp4_download(monkeypatch)
    monkeypatch.setattr("time.sleep", lambda _: None)
    monkeypatch.setattr(config, "RENDERS_DIR", tmp_path / "renders")
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")

    result = CliRunner().invoke(app, ["render", "--item-id", item_id, "--wait"])
    assert result.exit_code == 0, result.output
    assert "Resuming" in result.output

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "rendered"
    job = get_render_job(db_path, TASK_ID)
    assert job["status"] == "completed"


def test_render_poll_failure_marks_job_failed(monkeypatch, tmp_path):
    """TurboUnavailableError during polling marks the job failed (not stuck pending)."""
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config
    from orchestrator.adapters import turbo
    init_db(db_path)
    item_id = _seed_scripted_item(db_path)
    _fake_render(monkeypatch)
    monkeypatch.setattr(
        turbo, "get_job_status",
        lambda _: (_ for _ in ()).throw(turbo.TurboUnavailableError("timeout")),
    )
    monkeypatch.setattr("time.sleep", lambda _: None)
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")

    result = CliRunner().invoke(app, ["render", "--item-id", item_id, "--wait"])
    assert result.exit_code != 0

    job = get_render_job(db_path, TASK_ID)
    assert job["status"] == "failed"
    assert job["log_path"] is not None

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "scripted"
