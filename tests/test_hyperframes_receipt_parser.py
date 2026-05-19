from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.m8_gtm.harness import generate_packet_from_runtime_payload
from tests.test_m8_aice_runtime_payload import AICE_SLUG, sample_runtime_payload


def make_runtime_packet(tmp_path: Path) -> Path:
    result = generate_packet_from_runtime_payload(
        AICE_SLUG,
        sample_runtime_payload(),
        output_root=tmp_path,
    )
    return Path(result["packet_dir"])


def test_load_aice_validator_model_normalizes_and_validates_good_packet(
    tmp_path: Path,
):
    from orchestrator.hyperframes_receipts import SAFE_FOUNDER_CLAIM
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    payload = sample_runtime_payload()
    expected_labels = payload["nodes_executed"] + ["Profusion Receipt Packet"]
    manifest = json.loads(
        (packet_dir / "artifact_manifest.json").read_text(encoding="utf-8")
    )

    model = load_aice_hyperframe_model(packet_dir)

    assert model["receipt_id"].startswith("receipt-")
    assert model["receipt_path"] == packet_dir.name
    assert model["receipt"] == {
        "id": model["receipt_id"],
        "packet_path": packet_dir.name,
    }
    assert model["workflow"]["name"] == "AICE Source-to-Narrative Workflow Receipt"
    assert model["workflow"]["slug"] == AICE_SLUG
    assert model["workflow"]["evidence_mode"] == "workspace_runtime_n8n_payload"
    assert model["workflow"]["n8n_workflow_id"] == "wf_runtime_aice_20260519"
    assert model["workflow"]["n8n_execution_id"] == "exec_runtime_aice_20260519"
    assert model["workflow"]["node_count"] == 7
    assert model["workflow"]["status"] == "success"
    assert [node["label"] for node in model["nodes"]] == expected_labels
    assert model["nodes"][-1]["derived"] is True
    assert model["nodes"][0]["derived"] is False
    assert model["validation"]["validation_status"] == "validated_with_limitations"
    assert model["validation"]["core_files_present"] is True
    assert model["validation"]["display_files_present"] is True
    assert model["validation"]["runtime_payload_found"] is True
    assert model["validation"]["workflow_slug_matches"] is True
    assert model["validation"]["n8n_execution_id_present"] is True
    assert model["validation"]["node_count_matches_trail"] is True
    assert model["validation"]["minimum_node_count_met"] is True
    assert model["validation"]["human_review_artifact_present"] is True
    assert model["validation"]["supported_claims_present"] is True
    assert model["validation"]["unsupported_claims_present"] is True
    assert model["validation"]["limitations_present"] is True
    assert model["validation"]["path_safety_passed"] is True
    assert model["validation"]["forbidden_overclaim_language_found"] is False
    assert model["validation"]["artifact_hashes_checked"] is True
    assert model["validation"]["validation_findings"]
    assert model["proof_counters"] == {
        "nodes_executed": 7,
        "receipt_artifacts_found": 6,
        "claim_boundaries_present": 2,
        "human_review_gates_recorded": 1,
    }

    artifact_paths = {artifact["packet_path"] for artifact in model["artifacts"]}
    manifest_paths = {artifact["packet_path"] for artifact in manifest["artifacts"]}
    assert manifest_paths.issubset(artifact_paths)
    assert {
        "workflow_receipt.html",
        "workflow_receipt.md",
        "workflow_receipt.json",
        "m8_observation.json",
        "artifact_manifest.json",
    }.issubset(artifact_paths)
    assert all("path" not in artifact for artifact in model["artifacts"])
    assert all(
        artifact["href"].startswith("/packet/")
        for artifact in model["artifacts"]
        if artifact["exists"]
    )
    assert model["claims"]["supported"] == model["supported_claims"]
    assert model["claims"]["unsupported"] == model["unsupported_claims"]
    assert model["verification"]["safe_founder_claim"] == SAFE_FOUNDER_CLAIM


def test_load_aice_validator_model_warns_when_html_receipt_is_missing(
    tmp_path: Path,
):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    (packet_dir / "workflow_receipt.html").unlink()

    model = load_aice_hyperframe_model(packet_dir)

    assert model["validation"]["validation_status"] == "validated_with_warnings"
    assert model["validation"]["display_files_present"] is False
    assert model["verification"]["html_receipt_found"] is False
    assert "workflow_receipt.html" in model["verification"]["missing_files"]
    assert any(
        finding["severity"] == "warn" and finding["code"] == "display_files_present"
        for finding in model["validation"]["validation_findings"]
    )


def test_load_aice_validator_model_rejects_missing_core_json(tmp_path: Path):
    from orchestrator.hyperframes_receipts import HyperframeReceiptError
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    (packet_dir / "workflow_receipt.json").unlink()

    with pytest.raises(HyperframeReceiptError, match="workflow_receipt.json"):
        load_aice_hyperframe_model(packet_dir)


def test_load_aice_validator_model_detects_forbidden_supported_claim(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    receipt_path = packet_dir / "workflow_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["claims_supported"].append("This workflow is production ready.")
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    model = load_aice_hyperframe_model(packet_dir)

    assert model["validation"]["validation_status"] == "validation_failed"
    assert model["validation"]["forbidden_overclaim_language_found"] is True
    assert any(
        finding["severity"] == "fail"
        and finding["code"] == "forbidden_overclaim_language"
        for finding in model["validation"]["validation_findings"]
    )


def test_load_aice_validator_model_fails_when_node_trail_is_truncated(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    observation_path = packet_dir / "m8_observation.json"
    observation = json.loads(observation_path.read_text(encoding="utf-8"))
    observation["n8n_execution"]["nodes_executed"] = observation["n8n_execution"][
        "nodes_executed"
    ][:3]
    observation["n8n_execution"]["node_count"] = 3
    observation_path.write_text(json.dumps(observation, indent=2), encoding="utf-8")

    model = load_aice_hyperframe_model(packet_dir)

    assert model["validation"]["validation_status"] == "validation_failed"
    assert model["validation"]["minimum_node_count_met"] is False
    assert any(
        finding["severity"] == "fail" and finding["code"] == "minimum_node_count_met"
        for finding in model["validation"]["validation_findings"]
    )


def test_load_aice_validator_model_fails_on_observation_workflow_slug_mismatch(
    tmp_path: Path,
):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    observation_path = packet_dir / "m8_observation.json"
    observation = json.loads(observation_path.read_text(encoding="utf-8"))
    observation["workflow_id"] = "other-workflow"
    observation_path.write_text(json.dumps(observation, indent=2), encoding="utf-8")

    model = load_aice_hyperframe_model(packet_dir)

    assert model["validation"]["validation_status"] == "validation_failed"
    assert model["validation"]["workflow_slug_matches"] is False
    assert any(
        finding["severity"] == "fail" and finding["code"] == "workflow_slug_matches"
        for finding in model["validation"]["validation_findings"]
    )


def test_load_aice_validator_model_detects_forbidden_positive_receipt_field(
    tmp_path: Path,
):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    receipt_path = packet_dir / "workflow_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["evidence_boundary"] = (
        f"{receipt['evidence_boundary']} This workflow is production ready."
    )
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    model = load_aice_hyperframe_model(packet_dir)

    assert model["validation"]["validation_status"] == "validation_failed"
    assert model["validation"]["forbidden_overclaim_language_found"] is True
    assert any(
        finding["severity"] == "fail"
        and finding["code"] == "forbidden_overclaim_language"
        for finding in model["validation"]["validation_findings"]
    )


def test_load_aice_validator_model_fails_on_manifest_hash_mismatch(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    (packet_dir / "artifacts" / "source_cards.json").write_text(
        json.dumps({"tampered": True}),
        encoding="utf-8",
    )

    model = load_aice_hyperframe_model(packet_dir)

    assert model["validation"]["validation_status"] == "validation_failed"
    assert model["validation"]["artifact_hashes_checked"] is False
    assert any(
        finding["severity"] == "fail" and finding["code"] == "artifact_hashes_checked"
        for finding in model["validation"]["validation_findings"]
    )


def test_load_aice_validator_model_fails_on_unsafe_manifest_path(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    manifest_path = packet_dir / "artifact_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"].append(
        {
            "artifact_id": "unsafe.outside",
            "artifact_type": "unsafe",
            "description": "Unsafe manifest path.",
            "packet_path": "../outside.json",
            "sha256": "0" * 64,
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    model = load_aice_hyperframe_model(packet_dir)

    assert model["validation"]["validation_status"] == "validation_failed"
    assert model["validation"]["path_safety_passed"] is False
    unsafe_artifact = next(
        artifact
        for artifact in model["artifacts"]
        if artifact["packet_path"] == "../outside.json"
    )
    assert unsafe_artifact["href"] is None
    assert any(
        finding["severity"] == "fail" and finding["code"] == "path_safety_passed"
        for finding in model["validation"]["validation_findings"]
    )


def test_render_aice_validator_view_includes_scene_ready_validator_sections(
    tmp_path: Path,
):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_receipts import render_aice_validator_view

    packet_dir = make_runtime_packet(tmp_path)
    model = load_aice_hyperframe_model(packet_dir)

    html = render_aice_validator_view(model, local_url="http://127.0.0.1:8765/")

    assert html.startswith("<!doctype html>")
    assert '<html lang="en">' in html
    assert "<head>" in html
    assert "<body>" in html
    assert "</body>" in html
    assert "</html>" in html
    assert "AICE Workflow Receipt Validator" in html
    assert "HyperFrames Explorer for one completed Profusion receipt packet" in html
    assert "Validated with limitations" in html
    assert (
        "This n8n workflow ran. Profusion preserved what happened. The receipt tells "
        "you what the evidence supports and what it does not."
    ) in html
    assert "7 nodes executed" in html
    assert "6 receipt artifacts found" in html
    assert "2 claim boundaries present" in html
    assert "1 human review gate recorded" in html
    assert "Human Editorial Review Gate" in html
    assert "Execution" in html
    assert "Evidence" in html
    assert "Receipt" in html
    assert (
        "AICE workflow map derived from recorded node trail and receipt artifacts."
    ) in html
    assert "Artifact Ledger" in html
    assert "Open finished receipt" in html
    assert "Supported Claims" in html
    assert "Unsupported Claims" in html
    assert "Limitations" in html
    assert "Validation Findings" in html
    assert "Founder Proof Summary" in html
    assert "Copy Founder Proof Summary" in html
    assert "copyFounderProofSummary" in html
    assert 'data-prof-demo="aice-validator"' in html
    assert 'data-scene="validation-header"' in html
    assert 'data-scene="workflow-replay"' in html
    assert 'data-scene="human-review-gate"' in html
    assert 'data-scene="claim-boundary"' in html
    assert 'data-scene="artifact-ledger"' in html
    assert 'data-scene="founder-summary"' in html
    assert "/packet/artifacts/runtime_payload.json" in html
    assert "/receipt" in html
    assert "data-start=" not in html
    assert "data-duration=" not in html


def test_render_aice_validator_view_escapes_receipt_text(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_receipts import render_aice_validator_view

    packet_dir = make_runtime_packet(tmp_path)
    model = load_aice_hyperframe_model(packet_dir)
    model["workflow"]["name"] = "<script>alert('bad')</script>"
    model["supported_claims"].append("<img src=x onerror=alert(1)>")

    html = render_aice_validator_view(model, local_url="http://127.0.0.1:8765/")

    assert "<script>alert('bad')</script>" not in html
    assert "<img src=x onerror=alert(1)>" not in html
    assert "&lt;script&gt;alert(&#x27;bad&#x27;)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html


def test_render_aice_validator_view_uses_packet_relative_links_only(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_receipts import render_aice_validator_view

    packet_dir = make_runtime_packet(tmp_path)
    model = load_aice_hyperframe_model(packet_dir)

    html = render_aice_validator_view(model, local_url="http://127.0.0.1:8765/")

    assert str(packet_dir.resolve()) not in html
    assert "/packet/" in html
    for artifact in model["artifacts"]:
        if artifact["href"]:
            assert artifact["href"] in html


def test_render_aice_hyperframes_view_is_validator_alias(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_receipts import render_aice_hyperframes_view
    from orchestrator.hyperframes_receipts import render_aice_validator_view

    packet_dir = make_runtime_packet(tmp_path)
    model = load_aice_hyperframe_model(packet_dir)
    local_url = "http://127.0.0.1:8765/"

    assert render_aice_hyperframes_view(
        model, local_url=local_url
    ) == render_aice_validator_view(model, local_url=local_url)
