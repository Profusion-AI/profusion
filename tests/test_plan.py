"""profusion plan CLI tests — Claude calls are mocked."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import get_all_items, get_latest_brief, insert_content_item


def _use_tmp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


GOOD_BRIEF = {
    "thesis": "U.S. K-12 policy optimizes for compliance over learning outcomes.",
    "angle": "follow the incentive gradient, not the mission statement",
    "hook_options": [
        "Your school does not measure learning. It measures compliance.",
        "The grade book is an attendance sheet with math on top.",
    ],
    "cta": "Watch what gets measured, not what gets said.",
    "claims_to_verify": [
        {
            "claim": "State accountability systems weight attendance heavily.",
            "why_it_matters": "If false, the thesis collapses.",
            "suggested_source_type": "state ESSA plan text",
        }
    ],
    "risk_flags": [
        {
            "category": "partisan_framing",
            "description": "Could be read as anti-teacher if framed carelessly.",
            "mitigation": "Name the incentive system, not the people inside it.",
        }
    ],
    "brand_notes": "Keep tone sober; no policy-advocacy language.",
    "source_refs": [],
}


def _fake_claude_brief(monkeypatch, payload=GOOD_BRIEF):
    from orchestrator.adapters import claude

    def fake_generate(**_kwargs):
        return json.dumps(payload)

    monkeypatch.setattr(claude, "generate", fake_generate)


def test_plan_refuses_non_idea_status(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="pre-planned topic", status="planned")
    _fake_claude_brief(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(app, ["plan", "--item-id", item_id])
    assert result.exit_code != 0
    assert "Invalid transition" in result.output or "planned" in result.output


def test_plan_happy_path_stores_brief_and_transitions(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="compliance vs learning")
    _fake_claude_brief(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(app, ["plan", "--item-id", item_id])
    assert result.exit_code == 0, result.output

    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "planned"

    brief = get_latest_brief(db_path, item_id)
    assert brief is not None
    assert brief["thesis"].startswith("U.S. K-12")
    assert json.loads(brief["risk_flags"])[0]["category"] == "partisan_framing"
    assert json.loads(brief["claims_to_verify"])[0]["claim"].startswith("State accountability")


def test_plan_rejects_invalid_json(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="broken json case")

    from orchestrator.adapters import claude

    def fake_generate(**_kwargs):
        return "this is not json at all"

    monkeypatch.setattr(claude, "generate", fake_generate)

    runner = CliRunner()
    result = runner.invoke(app, ["plan", "--item-id", item_id])
    assert result.exit_code != 0
    items = {i["id"]: i for i in get_all_items(db_path)}
    # State must not advance on validation failure.
    assert items[item_id]["status"] == "idea"


def test_plan_rejects_schema_mismatch(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="bad category case")

    bad_payload = {
        "thesis": "valid thesis",
        "risk_flags": [
            {"category": "totally_made_up", "description": "x"}
        ],
    }
    _fake_claude_brief(monkeypatch, bad_payload)

    runner = CliRunner()
    result = runner.invoke(app, ["plan", "--item-id", item_id])
    assert result.exit_code != 0
    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "idea"


def test_plan_accepts_fenced_json(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    from orchestrator.db import init_db
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="fenced json case")

    from orchestrator.adapters import claude

    def fake_generate(**_kwargs):
        return "```json\n" + json.dumps(GOOD_BRIEF) + "\n```"

    monkeypatch.setattr(claude, "generate", fake_generate)

    runner = CliRunner()
    result = runner.invoke(app, ["plan", "--item-id", item_id])
    assert result.exit_code == 0, result.output
    items = {i["id"]: i for i in get_all_items(db_path)}
    assert items[item_id]["status"] == "planned"
