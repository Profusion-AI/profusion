"""AICE P0.1.1 live-minimum receipt harness tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import orchestrator.m8_gtm.harness as harness
from orchestrator.m8_gtm.fixtures import load_workflow_fixture
from orchestrator.m8_gtm.harness import generate_demo_packet
from orchestrator.m8_gtm.renderers import render_receipt_html


AICE_WORKFLOW_SLUG = "aice-source-to-narrative-receipt"
N8N_WORKFLOW_PATH = Path(
    "examples/n8n/aice-source-to-narrative-receipt.workflow.json"
)
REQUIRED_RECEIPT_FILES = {
    "artifact_manifest.json",
    "m8_observation.json",
    "workflow_receipt.json",
    "workflow_receipt.md",
    "workflow_receipt.html",
}
REQUIRED_AICE_ARTIFACT_TYPES = {
    "workflow_json",
    "topic_brief",
    "source_cards",
    "quote_candidates",
    "claim_map",
    "attention_intelligence_map",
    "rights_review",
    "ambiguity_register",
    "human_editorial_review",
    "narrative_brief",
    "visual_plan",
    "execution_log",
    "n8n_run_summary",
}
FORBIDDEN_AFFIRMATIVE_CLAIMS = (
    "legally cleared",
    "legal clearance",
    "fair-use approved",
    "fair use approved",
    "fair-use safe",
    "copyright safe",
    "copyright cleared",
    "cleared for use",
    "journalistically verified",
    "journalistically neutral",
    "PBS-approved",
    "Frontline-style certified",
    "Frontline-grade",
    "PBS-like",
    "safe to publish",
    "publication safe",
    "publication-ready",
    "platform compliant",
    "YouTube compliant",
    "truth-certified",
    "factually verified",
    "fully verified",
    "no-risk clip",
    "permission secured",
    "rights secured",
    "public-interest exception applies",
)


def test_aice_fixture_loader_accepts_live_minimum_contract():
    fixture = load_workflow_fixture(AICE_WORKFLOW_SLUG)

    assert fixture["workflow"]["workflow_name"] == "AICE Source-to-Narrative Workflow Receipt"
    assert fixture["workflow"]["trust_domain"] == "ai_assisted_investigative_content"
    assert fixture["workflow"]["evidence_mode"] == "fixture_backed_live_n8n_demo"
    assert fixture["workflow"]["default_publication_state"] == "not_publishable_without_human_review"
    assert len(fixture["runs"]) == 1

    run = fixture["runs"][0]
    assert run["case_id"] == "live_minimum_aice"
    assert REQUIRED_AICE_ARTIFACT_TYPES.issubset(
        {row["artifact_type"] for row in run["artifact_files"]} | {"workflow_json"}
    )
    assert run["artifacts"]["n8n_run_summary"]["node_count"] >= 3
    assert (
        run["artifacts"]["n8n_run_summary"]["execution_mode"]
        == "live_n8n_or_controlled_live_fallback"
    )
    assert run["artifacts"]["human_editorial_review"]["reviewer"] == "Kyle"

    quote_candidates = run["artifacts"]["quote_candidates"]["quote_candidates"]
    assert quote_candidates
    for candidate in quote_candidates:
        assert candidate["storage_mode"] == "metadata_only"
        assert candidate["audio_visual_downloaded"] is False
        assert candidate["review_status"] in {
            "rights_review_required",
            "hold_for_permission_or_replacement",
        }


def test_aice_cli_generates_complete_receipt_packet(tmp_path):
    result = generate_demo_packet(AICE_WORKFLOW_SLUG, output_root=tmp_path)

    packet_dir = Path(result["packet_dir"])
    assert REQUIRED_RECEIPT_FILES.issubset({path.name for path in packet_dir.iterdir()})
    assert not packet_dir.name.endswith(".partial")

    manifest = json.loads((packet_dir / "artifact_manifest.json").read_text(encoding="utf-8"))
    observation = json.loads((packet_dir / "m8_observation.json").read_text(encoding="utf-8"))
    receipt = json.loads((packet_dir / "workflow_receipt.json").read_text(encoding="utf-8"))
    markdown = (packet_dir / "workflow_receipt.md").read_text(encoding="utf-8")
    n8n_run_summary = json.loads(
        (packet_dir / "artifacts" / "n8n_run_summary.json").read_text(encoding="utf-8")
    )

    assert manifest["workflow_slug"] == AICE_WORKFLOW_SLUG
    assert manifest["evidence_mode"] == "fixture_backed_live_n8n_demo"
    assert "Gmail" not in "\n".join(manifest["limitations"])
    assert "No live customer message was sent by P0." not in manifest["limitations"]
    assert any("metadata/reference-only" in item for item in manifest["limitations"])
    assert REQUIRED_AICE_ARTIFACT_TYPES.issubset(
        {row["artifact_type"] for row in manifest["artifacts"]}
    )
    for row in manifest["artifacts"]:
        assert len(row["sha256"]) == 64
        assert (packet_dir / row["packet_path"]).exists()

    assert observation["workflow_id"] == AICE_WORKFLOW_SLUG
    assert observation["workflow_name"] == "AICE Source-to-Narrative Workflow Receipt"
    assert observation["trust_domain"] == "ai_assisted_investigative_content"
    assert observation["source_system"] == "n8n"
    assert observation["evidence_mode"] == "fixture_backed_live_n8n_demo"
    assert observation["n8n_execution"]["execution_id"]
    assert observation["n8n_execution"]["node_count"] >= 3
    assert len(observation["n8n_execution"]["nodes_executed"]) >= 3
    assert observation["n8n_execution"]["receipt_packet_path"] == str(packet_dir)
    assert observation["n8n_execution"]["output_receipt_path"] == str(
        packet_dir / "workflow_receipt.html"
    )
    assert n8n_run_summary["receipt_packet_path"] == str(packet_dir)
    assert n8n_run_summary["output_receipt_path"] == str(
        packet_dir / "workflow_receipt.html"
    )
    assert observation["n8n_execution"]["status"] in {
        "success",
        "completed_with_review_required",
    }
    assert observation["supported_claims"]
    assert observation["unsupported_claims"]
    assert observation["limitations"]
    assert receipt["claims_supported"] == observation["supported_claims"]
    assert receipt["claims_not_supported"] == observation["unsupported_claims"]
    assert receipt["ambiguities_preserved"]
    checked_in_claim_map = json.loads(
        (packet_dir / "artifacts" / "claim_map.json").read_text(encoding="utf-8")
    )
    checked_in_narrative = json.loads(
        (packet_dir / "artifacts" / "narrative_brief.json").read_text(encoding="utf-8")
    )
    embedded_fixture_text = json.dumps(
        {"claim_map": checked_in_claim_map, "narrative_brief": checked_in_narrative}
    ).lower()
    assert "does not prove live n8n execution" not in embedded_fixture_text
    assert "no live execution proof" not in embedded_fixture_text
    for candidate in receipt["quote_candidates"]:
        assert candidate["storage_mode"] == "metadata_only"
        assert candidate["audio_visual_downloaded"] is False
        assert "local_media_path" not in candidate
        assert "transcript_full_text" not in candidate

    required_sections = [
        "Workflow Boundary",
        "Topic / Episode Thesis",
        "What Happened",
        "Where AI Acted",
        "Where n8n Acted",
        "Where Human Editorial Review Entered",
        "Source Cards Captured",
        "Claims and Quote Candidates",
        "Rights / Use / Ambiguity Classification",
        "Attention Intelligence Mapping",
        "Narrative Decisions",
        "Generated / Synthetic Media Plan",
        "Supported Claims",
        "Claims Not Supported",
        "Limitations",
        "Next Recommended Review",
    ]
    for section in required_sections:
        assert f"## {section}" in markdown


def test_aice_n8n_workflow_export_matches_receipt_contract():
    workflow = json.loads(N8N_WORKFLOW_PATH.read_text(encoding="utf-8"))
    node_names = [node["name"] for node in workflow["nodes"]]

    assert workflow["id"] == "aiceSourceNarrativeP011"
    assert workflow["name"] == "AICE Source-to-Narrative Receipt - Profusion Local Demo"
    assert len(node_names) >= 3
    assert "Manual Trigger" in node_names
    assert "Generate Receipt Packet via Code Command" in node_names
    assert "Return Receipt Summary" in node_names

    receipt_node = next(
        node
        for node in workflow["nodes"]
        if node["name"] == "Generate Receipt Packet via Code Command"
    )
    receipt_code = receipt_node["parameters"]["jsCode"]
    assert "uv run profusion m8 demo aice-source-to-narrative-receipt" in receipt_code
    assert "--output-dir /tmp/profusion-aice-p0-1" in receipt_code


def test_aice_receipt_preserves_ambiguity_and_no_claims(tmp_path):
    result = generate_demo_packet(AICE_WORKFLOW_SLUG, output_root=tmp_path)
    receipt = result["receipt"]

    required_no_claims = (
        "does not certify factual truth",
        "does not certify copyright clearance",
        "does not certify fair use",
        "does not prove that third-party video/audio may be downloaded",
        "does not prove platform-policy compliance",
        "does not certify journalistic neutrality",
        "does not imply PBS/Frontline affiliation",
        "does not mean the final content is safe to publish",
        "does not replace human editorial or legal review",
        "only shows what was captured, classified, reviewed, limited, and generated",
    )
    combined_no_claims = "\n".join(receipt["claims_not_supported"])
    for phrase in required_no_claims:
        assert phrase in combined_no_claims

    combined_supported = "\n".join(receipt["claims_supported"]).lower()
    affirmative_text = "\n".join(
        receipt["claims_supported"]
        + receipt["what_happened"]
        + receipt.get("narrative_decisions", [])
    ).lower()
    for phrase in FORBIDDEN_AFFIRMATIVE_CLAIMS:
        assert phrase.lower() not in combined_supported
        assert phrase.lower() not in affirmative_text

    assert any(
        item["current_status"] in {"unresolved", "review_required"}
        for item in receipt["ambiguities_preserved"]
    )


def test_aice_html_escapes_fixture_text(tmp_path):
    result = generate_demo_packet(AICE_WORKFLOW_SLUG, output_root=tmp_path)
    receipt = result["receipt"]
    receipt["what_happened"].append("<script>alert('unsafe')</script>")
    receipt["source_cards"][0]["title"] = "<img src=x onerror=alert(1)>"
    receipt["quote_candidates"][0]["source_label"] = "<script>alert('quote')</script>"

    html = render_receipt_html(receipt)

    assert "<script>alert('unsafe')</script>" not in html
    assert "<img src=x onerror=alert(1)>" not in html
    assert "<script>alert('quote')</script>" not in html
    assert "&lt;script&gt;alert(&#x27;unsafe&#x27;)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "&lt;script&gt;alert(&#x27;quote&#x27;)&lt;/script&gt;" in html


def test_aice_failed_run_does_not_leave_completed_packet(tmp_path, monkeypatch):
    def fail_markdown(_receipt: dict) -> str:
        raise RuntimeError("forced render failure")

    monkeypatch.setattr(harness, "render_receipt_markdown", fail_markdown)

    with pytest.raises(RuntimeError, match="forced render failure"):
        generate_demo_packet(AICE_WORKFLOW_SLUG, output_root=tmp_path)

    slug_root = tmp_path / AICE_WORKFLOW_SLUG
    if slug_root.exists():
        for packet in slug_root.iterdir():
            if not packet.is_dir():
                continue
            assert packet.name.endswith(".partial")
            assert not REQUIRED_RECEIPT_FILES.issubset({path.name for path in packet.iterdir()})
