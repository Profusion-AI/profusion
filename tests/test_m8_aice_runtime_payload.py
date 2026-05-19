"""AICE workspace runtime-payload receipt tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.m8_gtm.harness import generate_packet_from_runtime_payload
from orchestrator.m8_gtm.runtime_payloads import validate_aice_runtime_payload
from orchestrator.m8_gtm.schemas import FixtureValidationError


AICE_SLUG = "aice-source-to-narrative-receipt"


def sample_runtime_payload() -> dict:
    return {
        "workflow_slug": AICE_SLUG,
        "n8n_workspace_workflow_id": "wf_runtime_aice_20260519",
        "n8n_execution_id": "exec_runtime_aice_20260519",
        "n8n_execution_url": (
            "https://n8n.example.invalid/workflow/"
            "wf_runtime_aice_20260519/executions/exec_runtime_aice_20260519"
        ),
        "executed_at": "2026-05-19T16:00:00Z",
        "node_count": 7,
        "nodes_executed": [
            "Manual Trigger",
            "Build Topic Brief",
            "Build Source Cards",
            "Extract Claim and Quote Candidates",
            "Rights and Ambiguity Classification",
            "Human Editorial Review Stub",
            "Generate Profusion Receipt via HTTP Request",
        ],
        "topic_brief": {
            "title": "Runtime-only AICE topic 20260519",
            "editorial_question": "Can runtime n8n payloads create Profusion receipts?",
            "working_thesis": (
                "Runtime payload evidence should be visible in the generated receipt."
            ),
        },
        "source_cards": [
            {
                "source_id": "runtime-source-1",
                "title": "Runtime-only source card 20260519",
                "source_type": "public_web_metadata",
                "url": "https://example.com/runtime-source",
                "captured_claims": ["Runtime source card entered the n8n workflow."],
            }
        ],
        "quote_candidates": [
            {
                "quote_id": "runtime-quote-1",
                "source_id": "runtime-source-1",
                "source_label": "Runtime-only source card 20260519",
                "segment_summary": "Metadata-only runtime segment candidate.",
                "storage_mode": "metadata_only",
                "audio_visual_downloaded": False,
                "review_status": "rights_review_required",
            }
        ],
        "claim_map": [
            {
                "claim_id": "runtime-claim-1",
                "claim": "The PR #4 workflow used runtime n8n payload data.",
                "source_ids": ["runtime-source-1"],
                "support_status": "supported_by_runtime_payload",
            }
        ],
        "attention_intelligence_map": [
            {
                "dimension": "accountability",
                "workflow_signal": "Runtime workflow IDs and node trail are preserved.",
            }
        ],
        "rights_review": {
            "status": "review_required",
            "items": [
                {
                    "source_id": "runtime-source-1",
                    "classification": "metadata_reference_only",
                    "decision": "do_not_download_or_publish",
                }
            ],
        },
        "ambiguity_register": [
            {
                "ambiguity_id": "runtime-ambiguity-1",
                "question": "Does this prove publication safety?",
                "current_status": "unresolved",
                "resolution_path": "Human review required before external use.",
            }
        ],
        "human_editorial_review": {
            "reviewer": "Kyle",
            "decision": "internal_demo_only",
            "reviewed_artifacts": [
                "topic_brief",
                "source_cards",
                "claim_map",
                "ambiguity_register",
            ],
            "approval_summary": "Runtime payload is acceptable for internal proof only.",
            "reviewed_at": "2026-05-19T16:05:00Z",
        },
        "narrative_brief": {
            "allowed_use": "internal_demo_only",
            "brief": [
                "Show that runtime data, not committed fixtures, appears in the receipt."
            ],
        },
        "visual_plan": {
            "allowed_use": "planning_only",
            "generated_media_state": "not_generated",
            "notes": ["No third-party audio/video is downloaded."],
        },
        "limitations": [
            "No third-party media downloaded.",
            (
                "Receipt does not certify factual truth, copyright clearance, fair use, "
                "platform compliance, journalistic neutrality, or publication safety."
            ),
        ],
    }


def test_generate_packet_from_runtime_payload_uses_runtime_values(tmp_path: Path):
    result = generate_packet_from_runtime_payload(
        AICE_SLUG,
        sample_runtime_payload(),
        output_root=tmp_path,
    )

    packet_dir = Path(result["packet_dir"])
    receipt = json.loads((packet_dir / "workflow_receipt.json").read_text(encoding="utf-8"))
    observation = json.loads((packet_dir / "m8_observation.json").read_text(encoding="utf-8"))
    manifest = json.loads((packet_dir / "artifact_manifest.json").read_text(encoding="utf-8"))

    assert receipt["evidence_mode"] == "workspace_runtime_n8n_payload"
    assert "Runtime-only AICE topic 20260519" in receipt["topic_episode_thesis"]
    assert receipt["source_cards"][0]["title"] == "Runtime-only source card 20260519"
    assert (
        observation["n8n_execution"]["workspace_workflow_id"]
        == "wf_runtime_aice_20260519"
    )
    assert observation["n8n_execution"]["execution_id"] == "exec_runtime_aice_20260519"
    assert observation["n8n_execution"]["node_count"] == 7
    assert len(observation["n8n_execution"]["nodes_executed"]) >= 3
    assert any(row["artifact_type"] == "runtime_payload" for row in manifest["artifacts"])
    assert any("workspace runtime payload" in claim for claim in receipt["claims_supported"])
    assert any(
        "Workspace proof uses controlled runtime metadata" in item
        for item in receipt["limitations"]
    )


def test_generate_packet_from_runtime_payload_rejects_media_download_claim(
    tmp_path: Path,
):
    payload = sample_runtime_payload()
    payload["quote_candidates"][0]["audio_visual_downloaded"] = True

    try:
        generate_packet_from_runtime_payload(AICE_SLUG, payload, output_root=tmp_path)
    except ValueError as exc:
        assert "must not download audio/video" in str(exc)
    else:
        raise AssertionError("runtime payload with downloaded media should fail")


def test_runtime_payload_requires_core_editorial_fields():
    invalid_payloads = []

    missing_topic_title = sample_runtime_payload()
    del missing_topic_title["topic_brief"]["title"]
    invalid_payloads.append((missing_topic_title, "topic_brief.title"))

    missing_editorial_question = sample_runtime_payload()
    del missing_editorial_question["topic_brief"]["editorial_question"]
    invalid_payloads.append((missing_editorial_question, "topic_brief.editorial_question"))

    missing_reviewer = sample_runtime_payload()
    del missing_reviewer["human_editorial_review"]["reviewer"]
    invalid_payloads.append((missing_reviewer, "human_editorial_review.reviewer"))

    empty_reviewed_artifacts = sample_runtime_payload()
    empty_reviewed_artifacts["human_editorial_review"]["reviewed_artifacts"] = []
    invalid_payloads.append(
        (empty_reviewed_artifacts, "human_editorial_review.reviewed_artifacts")
    )

    missing_allowed_use = sample_runtime_payload()
    del missing_allowed_use["narrative_brief"]["allowed_use"]
    invalid_payloads.append((missing_allowed_use, "narrative_brief.allowed_use"))

    empty_rights_items = sample_runtime_payload()
    empty_rights_items["rights_review"]["items"] = []
    invalid_payloads.append((empty_rights_items, "rights_review.items"))

    for payload, expected_message in invalid_payloads:
        try:
            validate_aice_runtime_payload(payload)
        except FixtureValidationError as exc:
            assert expected_message in str(exc)
        else:
            raise AssertionError(f"{expected_message} should be required")


def test_runtime_receipt_markdown_and_html_render_structured_sections(tmp_path: Path):
    result = generate_packet_from_runtime_payload(
        AICE_SLUG,
        sample_runtime_payload(),
        output_root=tmp_path,
    )

    packet_dir = Path(result["packet_dir"])
    markdown = (packet_dir / "workflow_receipt.md").read_text(encoding="utf-8")
    html = (packet_dir / "workflow_receipt.html").read_text(encoding="utf-8")

    assert "{'source_id'" not in markdown
    assert "{'claim_id'" not in markdown
    assert "{'rights_review'" not in markdown
    assert "&#x27;source_id&#x27;" not in html
    assert "&#x27;claim_id&#x27;" not in html
    assert "&#x27;rights_review&#x27;" not in html
    assert "Source ID: runtime-source-1" in markdown
    assert "<strong>Source ID:</strong> runtime-source-1" in html


def test_m8_generate_from_payload_cli_writes_runtime_receipt(tmp_path: Path):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(sample_runtime_payload()), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "m8",
            "generate-from-payload",
            AICE_SLUG,
            "--input",
            str(payload_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["workflow_slug"] == AICE_SLUG
    assert payload["n8n_execution_id"] == "exec_runtime_aice_20260519"
    assert Path(payload["workflow_receipt_html"]).exists()
