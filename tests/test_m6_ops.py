"""M6 operator hardening surfaces."""

import json
from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    get_all_items,
    get_publish_jobs_for_item,
    get_render_jobs_for_item,
    init_db,
    insert_content_item,
    mark_publish_job_failed,
)
from tests.test_publish import _seed_approved_item, _use_tmp_db
from tests.test_schedule import _schedule_args


def _use_m6_tmp(monkeypatch, tmp_path: Path) -> Path:
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    import orchestrator.config as config
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(config, "RENDERS_DIR", tmp_path / "renders")
    return db_path


def test_status_json_contract(monkeypatch, tmp_path):
    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="json status topic")

    result = CliRunner().invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["items"][0]["id"] == item_id
    assert payload["summary"][0]["status"] == "idea"
    assert "T" in payload["items"][0]["created_at"]
    assert payload["items"][0]["created_at"].endswith("Z")


def test_inspect_json_includes_next_command(monkeypatch, tmp_path):
    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="inspect me")

    result = CliRunner().invoke(app, ["inspect", "--item-id", item_id, "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["item"]["id"] == item_id
    assert payload["lifecycle_state"] == "idea"
    assert payload["next_safe_command"].endswith(f"plan --item-id {item_id}")


def test_jobs_renders_approvals_json_for_approved_item(monkeypatch, tmp_path):
    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)

    jobs = CliRunner().invoke(app, ["jobs", "--item-id", item_id, "--json"])
    renders = CliRunner().invoke(app, ["renders", "--item-id", item_id, "--json"])
    approvals = CliRunner().invoke(app, ["approvals", "--item-id", item_id, "--json"])

    assert jobs.exit_code == renders.exit_code == approvals.exit_code == 0
    assert json.loads(jobs.output)["render_jobs"][0]["status"] == "completed"
    assert json.loads(renders.output)["artifacts"]["mp4_exists"] is True
    assert json.loads(approvals.output)["effective_decision"] == "approved"


def test_handoff_markdown_contains_next_safe_command(monkeypatch, tmp_path):
    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="handoff topic")

    result = CliRunner().invoke(app, ["handoff", "--item-id", item_id])

    assert result.exit_code == 0
    assert "# Profusion Handoff" in result.output
    assert "uv run profusion plan" in result.output


def test_retry_requeues_failed_scheduled_publish_job(monkeypatch, tmp_path):
    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    CliRunner().invoke(app, _schedule_args(item_id, "youtube_shorts:99"))
    job = get_publish_jobs_for_item(db_path, item_id)[0]
    mark_publish_job_failed(db_path, job["id"], "network error")

    result = CliRunner().invoke(app, ["retry", "--job-id", job["id"], "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["action"] == "requeued_scheduled_job"
    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert jobs[0]["status"] == "scheduled"
    assert jobs[0]["last_error"] is None


def test_retry_qa_returns_item_to_rendered(monkeypatch, tmp_path):
    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    # Move back to rendered -> qa_failed by direct status for a retry-surface fixture.
    from orchestrator.db import update_item_status
    update_item_status(db_path, item_id, "archived")
    # update_item_status intentionally does not validate transitions; use it to create a
    # historical qa_failed fixture without exercising the full QA adapter.
    update_item_status(db_path, item_id, "qa_failed")

    result = CliRunner().invoke(
        app, ["retry", "--item-id", item_id, "--stage", "qa", "--json"]
    )

    assert result.exit_code == 0
    assert json.loads(result.output)["action"] == "returned_to_rendered_for_qa"
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "rendered"


def test_retry_render_job_submits_linked_new_job(monkeypatch, tmp_path):
    from orchestrator.adapters.turbo import RenderJobResult
    from orchestrator.db import update_item_status, update_render_job

    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    update_item_status(db_path, item_id, "scripted")
    old_job = get_render_jobs_for_item(db_path, item_id)[0]
    update_render_job(db_path, old_job["id"], status="failed")
    monkeypatch.setattr(
        "orchestrator.adapters.turbo.render",
        lambda **kw: RenderJobResult(task_id="retry-render-1", status="pending"),
    )

    result = CliRunner().invoke(app, ["retry", "--render-job-id", old_job["id"], "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["new_render_job_id"] == "retry-render-1"
    jobs = get_render_jobs_for_item(db_path, item_id)
    retry_job = [j for j in jobs if j["id"] == "retry-render-1"][0]
    assert retry_job["retry_of_job_id"] == old_job["id"]


def test_schedule_duplicate_target_requires_force(monkeypatch, tmp_path):
    db_path = _use_m6_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)

    result = CliRunner().invoke(
        app,
        _schedule_args(item_id, "youtube_shorts:99", "youtube_shorts:99"),
    )

    assert result.exit_code != 0
    assert "Duplicate" in result.output
    assert get_publish_jobs_for_item(db_path, item_id) == []


def test_smoke_offline(monkeypatch, tmp_path):
    _use_m6_tmp(monkeypatch, tmp_path)

    result = CliRunner().invoke(app, ["smoke", "--offline"])

    assert result.exit_code == 0
    assert "offline smoke passed" in result.output


def test_diagnostic_context_redacts_secrets(tmp_path):
    from orchestrator.diagnostics import write_diagnostic

    log_path, json_path = write_diagnostic(
        tmp_path / "logs",
        stage="publish",
        item_id="item-1",
        error="authorization: bearer secret-token",
        context={
            "api_key": "sk-secret",
            "nested": {"token": "nested-secret"},
            "message": "api_key=inline-secret",
        },
    )

    log_text = Path(log_path).read_text(encoding="utf-8")
    payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
    assert "secret-token" not in log_text
    assert "sk-secret" not in log_text
    assert "nested-secret" not in log_text
    assert "inline-secret" not in log_text
    assert payload["context"]["api_key"] == "[REDACTED]"
    assert payload["context"]["nested"]["token"] == "[REDACTED]"
