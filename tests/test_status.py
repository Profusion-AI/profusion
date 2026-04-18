"""profusion status CLI tests."""

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import insert_content_item


def _use_tmp_db(monkeypatch, tmp_path):
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


def test_status_empty_queue(monkeypatch, tmp_path):
    _use_tmp_db(monkeypatch, tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "empty" in result.output.lower()


def test_status_shows_ingested_item(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    insert_content_item(db_path, topic="test topic for status")
    runner = CliRunner()
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "test topic for status" in result.output
    assert "idea" in result.output


def test_status_filter_valid(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    insert_content_item(db_path, topic="idea item", status="idea")
    insert_content_item(db_path, topic="planned item", status="planned")
    runner = CliRunner()
    result = runner.invoke(app, ["status", "--status", "idea"])
    assert result.exit_code == 0
    assert "idea item" in result.output
    assert "planned item" not in result.output


def test_status_filter_invalid_exits_nonzero(monkeypatch, tmp_path):
    _use_tmp_db(monkeypatch, tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["status", "--status", "bogus"])
    assert result.exit_code != 0
    assert "bogus" in result.output


def test_plan_missing_api_key_exits_cleanly(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    import orchestrator.config as config
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="key test")
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", None)

    runner = CliRunner()
    result = runner.invoke(app, ["plan", "--item-id", item_id])
    assert result.exit_code != 0
    assert result.exception is None or "Traceback" not in result.output


def test_script_missing_api_key_exits_cleanly(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db, insert_content_brief, update_item_status
    import orchestrator.config as config
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="key test script")
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
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", None)

    runner = CliRunner()
    result = runner.invoke(app, ["script", "--item-id", item_id])
    assert result.exit_code != 0
    assert result.exception is None or "Traceback" not in result.output
