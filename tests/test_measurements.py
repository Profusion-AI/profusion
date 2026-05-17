"""M8 file-first workflow outcome observation tests."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

import orchestrator.config as config
from orchestrator.api import create_app
from orchestrator.cli import app
from orchestrator.db import get_all_items, init_db, insert_content_item, update_item_status
from orchestrator.measurements import (
    MeasurementEligibilityError,
    measurement_summary_payload,
    measurements_payload,
    record_measurement_observation,
)
from tests.test_publish import _seed_approved_item, _use_tmp_db


def _use_measurement_tmp(monkeypatch, tmp_path: Path) -> Path:
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(config, "MEASUREMENTS_DIR", tmp_path / "measurements")
    return db_path


def _seed_published_item(db_path: Path, tmp_path: Path) -> str:
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    update_item_status(db_path, item_id, "scheduled")
    update_item_status(db_path, item_id, "published")
    return item_id


def test_record_measurement_writes_file_and_transitions_published_item(monkeypatch, tmp_path):
    db_path = _use_measurement_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_published_item(db_path, tmp_path)

    observation = record_measurement_observation(
        db_path=db_path,
        measurements_dir=tmp_path / "measurements",
        item_id=item_id,
        platform="internal_demo",
        observation_type="reviewer_feedback",
        recorded_by="Kyle",
        qualitative_signal="Reviewer understood the receipt boundary.",
        views=None,
        completion_rate=None,
        comments=None,
        recorded_at="2026-05-03T00:00:00Z",
    )

    assert observation["content_item_id"] == item_id
    assert observation["platform"] == "internal_demo"
    assert observation["observation_type"] == "reviewer_feedback"
    assert observation["metrics"] == {
        "views": None,
        "completion_rate": None,
        "comments": None,
    }
    observation_path = Path(observation["observation_path"])
    assert observation_path.exists()
    assert json.loads(observation_path.read_text(encoding="utf-8"))["status_after"] == "measured"
    item = [row for row in get_all_items(db_path) if row["id"] == item_id][0]
    assert item["status"] == "measured"


def test_record_measurement_refuses_pre_published_item(monkeypatch, tmp_path):
    db_path = _use_measurement_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)

    with pytest.raises(MeasurementEligibilityError, match="published or measured"):
        record_measurement_observation(
            db_path=db_path,
            measurements_dir=tmp_path / "measurements",
            item_id=item_id,
            platform="internal_demo",
            observation_type="reviewer_feedback",
            recorded_by="Kyle",
        )


def test_measure_record_cli_outputs_observation_payload(monkeypatch, tmp_path):
    db_path = _use_measurement_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_published_item(db_path, tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "measure",
            "record",
            "--item-id",
            item_id,
            "--platform",
            "pilot_review",
            "--observation-type",
            "workflow_outcome",
            "--views",
            "120",
            "--completion-rate",
            "0.42",
            "--comments",
            "3",
            "--recorded-by",
            "Kyle",
            "--recorded-at",
            "2026-05-08T12:00:00-05:00",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["content_item_id"] == item_id
    assert payload["status_before"] == "published"
    assert payload["status_after"] == "measured"
    assert payload["recorded_at"] == "2026-05-08T17:00:00Z"
    assert payload["platform"] == "pilot_review"
    assert payload["observation_type"] == "workflow_outcome"
    assert payload["metrics"]["views"] == 120
    assert payload["metrics"]["completion_rate"] == 0.42
    assert payload["metrics"]["comments"] == 3


def test_measurement_read_models_return_item_and_aggregate_payloads(monkeypatch, tmp_path):
    db_path = _use_measurement_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_published_item(db_path, tmp_path)
    record_measurement_observation(
        db_path=db_path,
        measurements_dir=tmp_path / "measurements",
        item_id=item_id,
        platform="internal_demo",
        observation_type="reviewer_feedback",
        recorded_by="Kyle",
        qualitative_signal="Strong enough for internal review.",
    )

    item_payload = measurements_payload(
        measurements_dir=tmp_path / "measurements",
        item_id=item_id,
    )
    summary = measurement_summary_payload(
        db_path=db_path,
        measurements_dir=tmp_path / "measurements",
    )

    assert item_payload["item_id"] == item_id
    assert item_payload["measurement_count"] == 1
    assert item_payload["latest_observation"]["platform"] == "internal_demo"
    assert summary["observation_count"] == 1
    assert summary["measured_item_count"] == 1
    assert summary["platforms"] == [{"platform": "internal_demo", "count": 1}]
    assert summary["observation_types"] == [{"observation_type": "reviewer_feedback", "count": 1}]
    assert summary["display_labels"] == {
        "measurement_group": "Outcome Observations",
        "platform": "Workflow Type",
        "hook_variant": "Scenario Variant",
        "content_format": "Workflow Type",
        "editorial_pillar": "Trust Domain",
    }


def test_measurement_summary_compares_manual_workflow_dimensions(monkeypatch, tmp_path):
    db_path = _use_measurement_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_a = insert_content_item(
        db_path,
        topic="Evidence boundary pilot A",
        pillar="workflow_trust",
        status="published",
    )
    item_b = insert_content_item(
        db_path,
        topic="Evidence boundary pilot B",
        pillar="workflow_trust",
        status="published",
    )

    record_measurement_observation(
        db_path=db_path,
        measurements_dir=tmp_path / "measurements",
        item_id=item_a,
        platform="founder_review",
        observation_type="workflow_outcome",
        recorded_by="Kyle",
        hook_variant="receipt_boundary_open",
        content_format="demo_packet",
        editorial_pillar="workflow_trust",
        views=100,
        completion_rate=0.5,
        comments=2,
        recorded_at="2026-05-08T12:00:00Z",
    )
    record_measurement_observation(
        db_path=db_path,
        measurements_dir=tmp_path / "measurements",
        item_id=item_b,
        platform="founder_review",
        observation_type="workflow_outcome",
        recorded_by="Kyle",
        hook_variant="receipt_boundary_open",
        content_format="demo_packet",
        editorial_pillar="workflow_trust",
        views=50,
        completion_rate=0.75,
        comments=1,
        recorded_at="2026-05-08T13:00:00Z",
    )

    summary = measurement_summary_payload(
        db_path=db_path,
        measurements_dir=tmp_path / "measurements",
    )

    assert summary["comparisons"]["hook_variants"] == [
        {
            "hook_variant": "receipt_boundary_open",
            "display_label": "Scenario Variant",
            "display_value": "receipt_boundary_open",
            "observation_count": 2,
            "item_count": 2,
            "aggregate_metrics": {
                "views": 150,
                "comments": 3,
                "average_completion_rate": 0.625,
            },
            "latest_observation": summary["latest_observation"],
        }
    ]
    assert summary["comparisons"]["content_formats"][0]["content_format"] == "demo_packet"
    assert summary["comparisons"]["content_formats"][0]["display_label"] == "Workflow Type"
    assert summary["comparisons"]["editorial_pillars"][0]["editorial_pillar"] == "workflow_trust"
    assert summary["comparisons"]["editorial_pillars"][0]["display_label"] == "Trust Domain"


def test_measure_record_cli_accepts_generic_workflow_dimension_aliases(monkeypatch, tmp_path):
    db_path = _use_measurement_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_published_item(db_path, tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "measure",
            "record",
            "--item-id",
            item_id,
            "--platform",
            "internal_demo",
            "--observation-type",
            "reviewer_feedback",
            "--scenario-variant",
            "receipt_boundary_open",
            "--workflow-type",
            "demo_packet",
            "--trust-domain",
            "media_trust",
            "--recorded-by",
            "Kyle",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["dimensions"] == {
        "hook_variant": "receipt_boundary_open",
        "content_format": "demo_packet",
        "editorial_pillar": "media_trust",
    }
    assert payload["display_dimensions"] == {
        "scenario_variant": "receipt_boundary_open",
        "workflow_type": "demo_packet",
        "trust_domain": "media_trust",
    }


def test_profusion_help_does_not_register_substack_command():
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "substack" not in result.output.lower()
    assert "educational media engine" not in result.output
    assert "workflow trust" in result.output.lower()
    assert "evidence receipt" in result.output.lower()


def test_measure_record_help_prefers_generic_workflow_dimension_labels():
    result = CliRunner().invoke(app, ["measure", "record", "--help"])

    assert result.exit_code == 0
    assert "--scenario-variant" in result.output
    assert "--workflow-type" in result.output
    assert "--trust-domain" in result.output
    assert "Scenario variant" in result.output
    assert "Workflow type" in result.output
    assert "Trust domain" in result.output
    assert "content format" not in result.output.lower()
    assert "editorial pillar" not in result.output.lower()


def test_measure_record_cli_keeps_legacy_dimension_flags_hidden_but_accepted(monkeypatch, tmp_path):
    db_path = _use_measurement_tmp(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = _seed_published_item(db_path, tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "measure",
            "record",
            "--item-id",
            item_id,
            "--platform",
            "internal_demo",
            "--observation-type",
            "reviewer_feedback",
            "--hook-variant",
            "receipt_boundary_open",
            "--content-format",
            "demo_packet",
            "--editorial-pillar",
            "media_trust",
            "--recorded-by",
            "Kyle",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["display_dimensions"] == {
        "scenario_variant": "receipt_boundary_open",
        "workflow_type": "demo_packet",
        "trust_domain": "media_trust",
    }


def test_measurement_api_routes(client_measurements):
    tc, db_path, tmp_path = client_measurements
    item_id = _seed_published_item(db_path, tmp_path)
    record_measurement_observation(
        db_path=db_path,
        measurements_dir=tmp_path / "measurements",
        item_id=item_id,
        platform="internal_demo",
        observation_type="reviewer_feedback",
        recorded_by="Kyle",
    )

    item_resp = tc.get(f"/api/items/{item_id}/measurements")
    summary_resp = tc.get("/api/measurements/summary")

    assert item_resp.status_code == 200
    assert item_resp.json()["measurement_count"] == 1
    assert summary_resp.status_code == 200
    assert summary_resp.json()["observation_count"] == 1


@pytest.fixture()
def client_measurements(monkeypatch, tmp_path):
    db_path = tmp_path / "content.db"
    init_db(db_path)
    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(config, "RECEIPTS_DIR", tmp_path / "receipts")
    monkeypatch.setattr(config, "MEASUREMENTS_DIR", tmp_path / "measurements")
    monkeypatch.setattr(config, "POST_BRIDGE_API_KEY", "test-key")
    (tmp_path / "logs").mkdir()
    return TestClient(create_app(dev=True)), db_path, tmp_path
