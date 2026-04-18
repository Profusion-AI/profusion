"""profusion script CLI tests — Claude calls are mocked."""

import json
from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    get_all_items,
    get_script_variants,
    insert_content_brief,
    insert_content_item,
    update_item_status,
)


def _use_tmp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


def _seed_planned_item(db_path):
    item_id = insert_content_item(db_path, topic="compliance vs learning")
    update_item_status(db_path, item_id, "planned")
    insert_content_brief(
        db_path,
        content_item_id=item_id,
        thesis="Schools optimize for compliance, not learning.",
        angle="follow the incentive gradient",
        hook_options=["Your school measures compliance."],
        cta="Watch what gets measured.",
        claims_to_verify=[{"claim": "Attendance weighted heavily."}],
        brand_notes="Sober tone.",
        risk_flags=[],
        source_refs=[],
    )
    return item_id


GOOD_SCRIPTS = {
    "variants": [
        {
            "variant_name": "straight_explainer",
            "script_text": "Your school does not measure learning...",
            "duration_target_seconds": 60,
        },
        {
            "variant_name": "provocative_hook",
            "script_text": "The grade book is attendance with math on top...",
            "duration_target_seconds": 60,
        },
        {
            "variant_name": "myth_vs_reality",
            "script_text": "We say schools teach critical thinking. The paperwork says otherwise...",
            "duration_target_seconds": 60,
        },
    ]
}


def _fake_claude_scripts(monkeypatch, payload=GOOD_SCRIPTS):
    from orchestrator.adapters import claude

    def fake_generate(**_kwargs):
        return json.dumps(payload)

    monkeypatch.setattr(claude, "generate", fake_generate)


def test_script_refuses_non_planned_status(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="still just an idea")
    _fake_claude_scripts(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(app, ["script", "--item-id", item_id])
    assert result.exit_code != 0
    assert "Invalid transition" in result.output or "idea" in result.output


def test_script_requires_existing_brief(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="planned but briefless")
    update_item_status(db_path, item_id, "planned")
    _fake_claude_scripts(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(app, ["script", "--item-id", item_id])
    assert result.exit_code != 0
    assert "brief" in result.output.lower()


def test_script_happy_path_writes_variants_and_transitions(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = _seed_planned_item(db_path)
    _fake_claude_scripts(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(app, ["script", "--item-id", item_id])
    assert result.exit_code == 0, result.output

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "scripted"

    variants = get_script_variants(db_path, item_id)
    names = {v["variant_name"] for v in variants}
    assert names == {"straight_explainer", "provocative_hook", "myth_vs_reality"}
    for v in variants:
        assert v["duration_target_seconds"] == 60
        assert v["status"] == "draft"
        assert v["script_text"]


def test_script_rejects_missing_variant(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = _seed_planned_item(db_path)

    partial = {"variants": GOOD_SCRIPTS["variants"][:2]}  # missing myth_vs_reality
    _fake_claude_scripts(monkeypatch, partial)

    runner = CliRunner()
    result = runner.invoke(app, ["script", "--item-id", item_id])
    assert result.exit_code != 0

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "planned"
    variants = get_script_variants(db_path, item_id)
    assert variants == []


def test_script_rejects_extra_variant(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = _seed_planned_item(db_path)

    extra = {
        "variants": GOOD_SCRIPTS["variants"] + [
            {"variant_name": "bonus_riff", "script_text": "extra", "duration_target_seconds": 60}
        ]
    }
    _fake_claude_scripts(monkeypatch, extra)

    runner = CliRunner()
    result = runner.invoke(app, ["script", "--item-id", item_id])
    assert result.exit_code != 0
    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "planned"
    assert get_script_variants(db_path, item_id) == []
