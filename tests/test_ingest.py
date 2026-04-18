"""profusion ingest CLI tests."""

from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import get_all_items


def _use_tmp_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "content.db"
    import orchestrator.config as config
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


def test_ingest_single_topic(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["ingest", "--topic", "Why schools reward compliance more than learning"],
    )
    assert result.exit_code == 0, result.output

    items = get_all_items(db_path)
    assert len(items) == 1
    assert items[0]["topic"] == "Why schools reward compliance more than learning"
    assert items[0]["status"] == "idea"


def test_ingest_requires_topic_or_file(monkeypatch, tmp_path):
    _use_tmp_db(monkeypatch, tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["ingest"])
    assert result.exit_code != 0
    assert "topic" in result.output.lower() or "file" in result.output.lower()


def test_ingest_csv(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    csv_path = tmp_path / "topics.csv"
    csv_path.write_text(
        "topic,pillar,audience,priority,source\n"
        "AI disruption in legal work,post_labor,career switchers,5,manual\n"
        "The real dropout story,education_reform,policymakers,3,manual\n"
        ",should,be,skipped,0\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["ingest", "--file", str(csv_path)])
    assert result.exit_code == 0, result.output

    items = get_all_items(db_path)
    assert len(items) == 2
    topics = {i["topic"] for i in items}
    assert "AI disruption in legal work" in topics
    assert "The real dropout story" in topics
    pillars = {i["pillar"] for i in items}
    assert "post_labor" in pillars
    assert "education_reform" in pillars
    for item in items:
        assert item["status"] == "idea"


def test_ingest_with_metadata_flags(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "ingest",
            "--topic",
            "Future of apprenticeship",
            "--pillar",
            "future_learning",
            "--audience",
            "educators",
            "--priority",
            "7",
        ],
    )
    assert result.exit_code == 0, result.output
    items = get_all_items(db_path)
    assert len(items) == 1
    assert items[0]["pillar"] == "future_learning"
    assert items[0]["audience"] == "educators"
    assert items[0]["priority"] == 7


def test_ingest_csv_missing_topic_header_fails(monkeypatch, tmp_path):
    _use_tmp_db(monkeypatch, tmp_path)
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("title,pillar\nsome topic,ed\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["ingest", "--file", str(csv_path)])
    assert result.exit_code != 0
    assert "topic" in result.output.lower()


def test_ingest_csv_invalid_priority_fails(monkeypatch, tmp_path):
    _use_tmp_db(monkeypatch, tmp_path)
    csv_path = tmp_path / "bad_prio.csv"
    csv_path.write_text(
        "topic,priority\nsome topic,notint\n", encoding="utf-8"
    )
    runner = CliRunner()
    result = runner.invoke(app, ["ingest", "--file", str(csv_path)])
    assert result.exit_code != 0
    assert "priority" in result.output.lower()


def test_ingest_csv_negative_priority_fails(monkeypatch, tmp_path):
    _use_tmp_db(monkeypatch, tmp_path)
    csv_path = tmp_path / "neg_prio.csv"
    csv_path.write_text(
        "topic,priority\nsome topic,-9\n", encoding="utf-8"
    )
    runner = CliRunner()
    result = runner.invoke(app, ["ingest", "--file", str(csv_path)])
    assert result.exit_code != 0
    assert "priority" in result.output.lower()


def test_ingest_csv_all_blank_topics_exits_nonzero(monkeypatch, tmp_path):
    _use_tmp_db(monkeypatch, tmp_path)
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("topic,pillar\n,ed\n  ,reform\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["ingest", "--file", str(csv_path)])
    assert result.exit_code != 0
