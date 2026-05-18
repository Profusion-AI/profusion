"""M8-GTM fixture-backed receipt harness tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.m8_gtm.fixtures import load_workflow_fixture
from orchestrator.m8_gtm.harness import (
    build_artifact_manifest,
    build_m8_observation,
    build_workflow_receipt,
    generate_demo_packet,
)
from orchestrator.m8_gtm.renderers import render_receipt_html, render_receipt_markdown


WORKFLOW_SLUG = "support-triage-human-review"
REQUIRED_RECEIPT_FILES = {
    "artifact_manifest.json",
    "m8_observation.json",
    "workflow_receipt.json",
    "workflow_receipt.md",
    "workflow_receipt.html",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _fixture_source() -> Path:
    return _repo_root() / "examples" / "m8" / WORKFLOW_SLUG


def _copied_fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "examples" / "m8"
    shutil.copytree(_fixture_source(), root / WORKFLOW_SLUG)
    return root


def _generated_receipt(tmp_path: Path) -> tuple[dict, dict, dict]:
    fixture = load_workflow_fixture(WORKFLOW_SLUG)
    manifest = build_artifact_manifest(fixture, tmp_path / "packet")
    observation = build_m8_observation(fixture, manifest)
    receipt = build_workflow_receipt(observation, manifest)
    return manifest, observation, receipt


def test_fixture_loader_accepts_support_triage_happy_path():
    fixture = load_workflow_fixture(WORKFLOW_SLUG)

    assert fixture["workflow"]["workflow_name"] == "Customer Trust Triage Receipt"
    assert {run["case_id"] for run in fixture["runs"]} == {
        "routine_invoice",
        "sensitive_billing_complaint",
    }
    runs = {run["case_id"]: run for run in fixture["runs"]}
    assert runs["routine_invoice"]["artifacts"]["ai_classification"]["category"] == "billing"
    assert runs["routine_invoice"]["artifacts"]["final_reply"].strip()
    assert runs["sensitive_billing_complaint"]["artifacts"]["ai_classification"]["sensitivity"] == "sensitive"
    assert runs["sensitive_billing_complaint"]["artifacts"]["human_review_event"]["decision"] == "edited"
    assert runs["sensitive_billing_complaint"]["artifacts"]["final_reply"].strip()


def test_fixture_validator_rejects_missing_sensitive_human_review(tmp_path):
    fixture_root = _copied_fixture_root(tmp_path)
    review_path = (
        fixture_root
        / WORKFLOW_SLUG
        / "runs"
        / "run_002_sensitive_billing_complaint"
        / "human_review_event.json"
    )
    review_path.unlink()

    with pytest.raises(
        ValueError,
        match="sensitive_billing_complaint requires a human_review_event.json artifact",
    ):
        load_workflow_fixture(WORKFLOW_SLUG, fixture_root=fixture_root)


def test_artifact_manifest_copies_and_hashes_files(tmp_path):
    fixture = load_workflow_fixture(WORKFLOW_SLUG)
    packet_dir = tmp_path / "packet"

    manifest = build_artifact_manifest(fixture, packet_dir)

    assert (packet_dir / "artifact_manifest.json").exists()
    assert manifest["workflow_slug"] == WORKFLOW_SLUG
    assert manifest["evidence_mode"] == "fixture_backed_local_demo"
    assert manifest["limitations"]
    artifact_rows = manifest["artifacts"]
    assert any(row["case_id"] == "workflow" for row in artifact_rows)
    assert any(row["case_id"] == "routine_invoice" for row in artifact_rows)
    assert any(row["case_id"] == "sensitive_billing_complaint" for row in artifact_rows)
    for row in artifact_rows:
        assert len(row["sha256"]) == 64
        assert (packet_dir / row["packet_path"]).exists()


def test_observation_builder_requires_honest_claims(tmp_path):
    manifest, observation, _ = _generated_receipt(tmp_path)

    assert observation["source_system"] == "n8n"
    assert observation["evidence_mode"] == "fixture_backed_local_demo"
    assert observation["workflow_id"] == WORKFLOW_SLUG
    assert observation["source_manifest_id"] == manifest["manifest_id"]
    assert set(observation["case_ids"]) == {
        "routine_invoice",
        "sensitive_billing_complaint",
    }
    assert observation["human_review_events"][0]["case_id"] == "sensitive_billing_complaint"
    assert observation["supported_claims"]
    assert observation["unsupported_claims"]
    assert observation["limitations"]
    assert any(
        "does not prove that the customer's billing claim was factually correct" in claim
        for claim in observation["unsupported_claims"]
    )


def test_receipt_json_mirrors_observation(tmp_path):
    _, observation, receipt = _generated_receipt(tmp_path)

    assert receipt["source_observation_id"] == observation["observation_id"]
    assert receipt["evidence_mode"] == "fixture_backed_local_demo"
    assert set(receipt["claims_supported"]).issubset(set(observation["supported_claims"]))
    assert set(receipt["claims_not_supported"]).issubset(set(observation["unsupported_claims"]))
    assert receipt["where_human_review_entered"]
    assert receipt["limitations"] == observation["limitations"]


def test_markdown_and_html_receipts_contain_required_sections_and_escape_text(tmp_path):
    _, _, receipt = _generated_receipt(tmp_path)
    receipt["what_happened"].append("<script>alert('unsafe')</script>")

    markdown = render_receipt_markdown(receipt)
    html = render_receipt_html(receipt)

    required_sections = [
        "Customer Trust Triage Receipt",
        "Workflow Boundary",
        "Where AI Acted",
        "Where Human Review Entered",
        "Supported Claims",
        "Claims Not Supported",
        "Limitations",
        "Next Recommended Review",
    ]
    for section in required_sections:
        assert section in markdown
        assert section in html
    assert "<script>alert('unsafe')</script>" not in html
    assert "&lt;script&gt;alert(&#x27;unsafe&#x27;)&lt;/script&gt;" in html


def test_cli_produces_complete_packet(tmp_path):
    output_dir = tmp_path / "receipts"

    result = CliRunner().invoke(
        app,
        ["m8", "demo", WORKFLOW_SLUG, "--output-dir", str(output_dir)],
    )

    assert result.exit_code == 0, result.output
    assert "workflow_receipt.html" in result.output
    slug_dir = output_dir / WORKFLOW_SLUG
    packet_dirs = [path for path in slug_dir.iterdir() if path.is_dir()]
    assert len(packet_dirs) == 1
    packet_dir = packet_dirs[0]
    assert not packet_dir.name.endswith(".partial")
    assert REQUIRED_RECEIPT_FILES.issubset({path.name for path in packet_dir.iterdir()})
    receipt = json.loads((packet_dir / "workflow_receipt.json").read_text(encoding="utf-8"))
    observation = json.loads((packet_dir / "m8_observation.json").read_text(encoding="utf-8"))
    assert receipt["claims_supported"]
    assert receipt["claims_not_supported"]
    assert receipt["limitations"]
    assert observation["human_review_events"][0]["case_id"] == "sensitive_billing_complaint"


def test_cli_rejects_unknown_workflow_slug(tmp_path):
    result = CliRunner().invoke(
        app,
        ["m8", "demo", "not-a-real-workflow", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 1
    assert "Unknown M8 demo workflow" in result.output
