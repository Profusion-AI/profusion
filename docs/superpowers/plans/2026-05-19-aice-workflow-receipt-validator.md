# AICE Workflow Receipt Validator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-only AICE Workflow Receipt Validator that turns one completed AICE receipt packet into a visual validation replay.

**Architecture:** Add a pure receipt-packet parser, validation layer, and scene-ready HTML renderer, then serve it through a local FastAPI app launched by `uv run profusion hyperframes validate --receipt-dir <receipt_dir>`. The `serve` command remains as a compatibility alias; the receipt remains the source of truth.

**Tech Stack:** Python 3.11, Typer, FastAPI, pytest, standard-library `hashlib`, `html`, `json`, and `pathlib`; plain generated HTML/CSS/JS only; no React, JSX, Vite, frontend framework, public deployment, or MP4 render in PR5.

---

## Current State

- PR #3 is merged into `main` as `2844545`.
- The AICE API guard/runbook follow-up is parked locally as:

```text
stash@{0}: On codex/aice-demo-readiness-api-hardening: park AICE demo-readiness API guard branch before HyperFrames PR5
```

- This plan starts PR5 from clean `main` on local branch
  `codex/pr5-aice-workflow-receipt-validator-tdd`.
- Active product name is now **AICE Workflow Receipt Validator**.
- The interactive view inside it remains **HyperFrames Explorer for one
  completed Profusion receipt packet**.
- Exact manual receipt packet for first validator check:

```text
/tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a/
```

## File Structure

- Create `tests/test_hyperframes_receipt_parser.py`: validator model, rendering, server, safe-artifact, and CLI dry-run tests.
- Create `src/orchestrator/hyperframes_receipts.py`: pure parser, validation model builder, artifact hash checker, forbidden-language detector, and scene-ready HTML renderer.
- Create `src/orchestrator/hyperframes_server.py`: local FastAPI app for one receipt packet directory with safe file routes.
- Modify `src/orchestrator/cli.py`: register `hyperframes` Typer group, add `validate`, and keep `serve` as a compatibility command that calls the same implementation.
- Create `docs/runbooks/aice_workflow_receipt_validator.md`: local usage, proof boundary, validation semantics, and limitations.
- Modify `docs/runbooks/README.md`: add runbook link.

## Shared Constants

Use these exact names and strings in implementation and tests:

```python
VALIDATOR_TITLE = "AICE Workflow Receipt Validator"
VALIDATOR_SUBTITLE = "HyperFrames Explorer for one completed Profusion receipt packet"
VALIDATION_STATUS = "validated_with_limitations"
SAFE_FOUNDER_CLAIM = (
    "This n8n workflow ran. Profusion preserved what happened. "
    "The receipt tells you what the evidence supports and what it does not."
)
PRODUCT_SAFE_EXPLANATION = (
    "Profusion turns one AI-assisted workflow execution into reviewable evidence: "
    "what ran, what artifacts existed, where human review entered, what claims are "
    "supported, what claims are not supported, and what limitations remain."
)
LINEAGE_NOTE = "AICE workflow map derived from recorded node trail and receipt artifacts."
```

Forbidden founder-facing terms:

```python
FORBIDDEN_FOUNDER_TERMS = (
    "certified true",
    "truth verified",
    "legally cleared",
    "fair-use approved",
    "copyright safe",
    "compliance approved",
    "platform compliant",
    "safe to publish",
    "no risk",
    "customer validated",
    "production ready",
)
```

## Task 1: Add Red Validator Model Tests

**Files:**
- Create: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Write failing model tests**

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.m8_gtm.harness import generate_packet_from_runtime_payload
from tests.test_m8_aice_runtime_payload import AICE_SLUG, sample_runtime_payload


EXPECTED_AICE_NODE_LABELS = [
    "Manual Trigger",
    "Build Topic Brief",
    "Build Source Cards",
    "Extract Claim and Quote Candidates",
    "Rights and Ambiguity Classification",
    "Human Editorial Review Stub",
    "Return Runtime Payload for Profusion",
    "Profusion Receipt Packet",
]


def make_runtime_packet(tmp_path: Path) -> Path:
    result = generate_packet_from_runtime_payload(
        AICE_SLUG,
        sample_runtime_payload(),
        output_root=tmp_path,
    )
    return Path(result["packet_dir"])


def test_load_aice_validator_model_normalizes_and_validates_good_packet(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)

    model = load_aice_hyperframe_model(packet_dir)

    assert model["receipt_id"].startswith("receipt-")
    assert model["workflow"]["name"] == "AICE Source-to-Narrative Workflow Receipt"
    assert model["workflow"]["slug"] == AICE_SLUG
    assert model["workflow"]["evidence_mode"] == "workspace_runtime_n8n_payload"
    assert model["workflow"]["n8n_workflow_id"] == "wf_runtime_aice_20260519"
    assert model["workflow"]["n8n_execution_id"] == "exec_runtime_aice_20260519"
    assert model["workflow"]["node_count"] == 7
    assert model["workflow"]["status"] == "success"
    assert [node["label"] for node in model["nodes"]] == EXPECTED_AICE_NODE_LABELS
    assert model["nodes"][-1]["derived"] is True
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
    assert model["validation"]["forbidden_overclaim_language_found"] is False
    assert model["validation"]["artifact_hashes_checked"] in {True, "partial"}
    assert model["validation"]["path_safety_passed"] is True
    assert model["validation"]["validation_findings"]
    assert model["proof_counters"] == {
        "nodes_executed": 7,
        "receipt_artifacts_found": 6,
        "claim_boundaries_present": 2,
        "human_review_gates_recorded": 1,
    }
    assert model["verification"]["safe_founder_claim"] == (
        "This n8n workflow ran. Profusion preserved what happened. "
        "The receipt tells you what the evidence supports and what it does not."
    )


def test_load_aice_validator_model_warns_when_html_receipt_is_missing(tmp_path: Path):
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
        finding["severity"] == "fail" and finding["code"] == "forbidden_overclaim_language"
        for finding in model["validation"]["validation_findings"]
    )
```

- [ ] **Step 2: Run the first model test to verify RED**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_load_aice_validator_model_normalizes_and_validates_good_packet -q
```

Expected: fail with `ModuleNotFoundError: No module named 'orchestrator.hyperframes_receipts'`.

## Task 2: Implement Parser And Validation Model

**Files:**
- Create: `src/orchestrator/hyperframes_receipts.py`
- Test: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Create the parser and validation module**

```python
"""Build local AICE Workflow Receipt Validator models from receipt packets."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

VALIDATOR_TITLE = "AICE Workflow Receipt Validator"
VALIDATOR_SUBTITLE = "HyperFrames Explorer for one completed Profusion receipt packet"
SAFE_FOUNDER_CLAIM = (
    "This n8n workflow ran. Profusion preserved what happened. "
    "The receipt tells you what the evidence supports and what it does not."
)
PRODUCT_SAFE_EXPLANATION = (
    "Profusion turns one AI-assisted workflow execution into reviewable evidence: "
    "what ran, what artifacts existed, where human review entered, what claims are "
    "supported, what claims are not supported, and what limitations remain."
)
LINEAGE_NOTE = "AICE workflow map derived from recorded node trail and receipt artifacts."
CORE_JSON_FILES = (
    "workflow_receipt.json",
    "artifact_manifest.json",
    "m8_observation.json",
    "artifacts/runtime_payload.json",
)
DISPLAY_FILES = CORE_JSON_FILES + ("workflow_receipt.md", "workflow_receipt.html")
REQUIRED_LEDGER_FILES = (
    "workflow_receipt.html",
    "workflow_receipt.md",
    "workflow_receipt.json",
    "m8_observation.json",
    "artifact_manifest.json",
    "artifacts/runtime_payload.json",
)
FORBIDDEN_FOUNDER_TERMS = (
    "certified true",
    "truth verified",
    "legally cleared",
    "fair-use approved",
    "copyright safe",
    "compliance approved",
    "platform compliant",
    "safe to publish",
    "no risk",
    "customer validated",
    "production ready",
)


class HyperframeReceiptError(ValueError):
    """Raised when a receipt packet cannot be parsed into a validator model."""


def load_aice_hyperframe_model(receipt_dir: Path | str) -> dict[str, Any]:
    root = Path(receipt_dir).expanduser().resolve()
    if not root.is_dir():
        raise HyperframeReceiptError(f"receipt directory not found: {root}")

    missing = [rel for rel in DISPLAY_FILES if not (root / rel).is_file()]
    missing_core = [rel for rel in CORE_JSON_FILES if not (root / rel).is_file()]
    if missing_core:
        raise HyperframeReceiptError(
            "receipt packet missing required JSON files: " + ", ".join(missing_core)
        )

    receipt = _read_json(root / "workflow_receipt.json")
    manifest = _read_json(root / "artifact_manifest.json")
    observation = _read_json(root / "m8_observation.json")
    runtime_payload = _read_json(root / "artifacts" / "runtime_payload.json")
    n8n_execution = observation.get("n8n_execution", {})
    supported_claims = list(observation.get("supported_claims") or receipt.get("claims_supported", []))
    unsupported_claims = list(observation.get("unsupported_claims") or receipt.get("claims_not_supported", []))
    limitations = list(observation.get("limitations") or receipt.get("limitations", []))
    artifacts = _artifact_rows(manifest, root)
    validation = _build_validation(
        root=root,
        receipt=receipt,
        manifest=manifest,
        observation=observation,
        runtime_payload=runtime_payload,
        missing_files=missing,
        supported_claims=supported_claims,
        unsupported_claims=unsupported_claims,
        limitations=limitations,
    )

    return {
        "receipt_id": receipt.get("receipt_id", root.name),
        "receipt_path": str(root),
        "validator_title": VALIDATOR_TITLE,
        "validator_subtitle": VALIDATOR_SUBTITLE,
        "workflow": {
            "name": observation.get("workflow_name") or receipt.get("workflow_name"),
            "slug": observation.get("workflow_id") or manifest.get("workflow_slug"),
            "evidence_mode": observation.get("evidence_mode") or receipt.get("evidence_mode"),
            "n8n_project": runtime_payload.get("n8n_project_id") or runtime_payload.get("n8n_project") or "",
            "n8n_workflow_id": n8n_execution.get("workspace_workflow_id") or runtime_payload.get("n8n_workspace_workflow_id"),
            "n8n_execution_id": n8n_execution.get("execution_id") or runtime_payload.get("n8n_execution_id"),
            "node_count": n8n_execution.get("node_count") or runtime_payload.get("node_count"),
            "status": n8n_execution.get("status") or runtime_payload.get("status", "success"),
        },
        "nodes": _aice_nodes(),
        "edges": _aice_edges(),
        "data_lanes": _data_lanes(),
        "artifacts": artifacts,
        "receipt_sections": _receipt_sections(runtime_payload, receipt),
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "limitations": limitations,
        "founder_claim": SAFE_FOUNDER_CLAIM,
        "product_safe_explanation": PRODUCT_SAFE_EXPLANATION,
        "proof_counters": {
            "nodes_executed": int(n8n_execution.get("node_count") or runtime_payload.get("node_count") or 0),
            "receipt_artifacts_found": sum(1 for artifact in artifacts if artifact["exists"]),
            "claim_boundaries_present": int(bool(supported_claims)) + int(bool(unsupported_claims)),
            "human_review_gates_recorded": int(bool(runtime_payload.get("human_editorial_review") or observation.get("human_review_events"))),
        },
        "validation": validation,
        "verification": {
            "required_files_present": not missing,
            "missing_files": missing,
            "receipt_parse_passed": True,
            "node_trail_found": bool(n8n_execution.get("nodes_executed")),
            "html_receipt_found": (root / "workflow_receipt.html").is_file(),
            "runtime_payload_found": (root / "artifacts" / "runtime_payload.json").is_file(),
            "artifact_manifest_found": (root / "artifact_manifest.json").is_file(),
            "readability_check": "passed",
            "safe_founder_claim": SAFE_FOUNDER_CLAIM,
            "lineage_note": LINEAGE_NOTE,
        },
    }
```

- [ ] **Step 2: Append validation helper functions**

```python
def _build_validation(
    *,
    root: Path,
    receipt: dict[str, Any],
    manifest: dict[str, Any],
    observation: dict[str, Any],
    runtime_payload: dict[str, Any],
    missing_files: list[str],
    supported_claims: list[str],
    unsupported_claims: list[str],
    limitations: list[str],
) -> dict[str, Any]:
    node_trail = observation.get("n8n_execution", {}).get("nodes_executed", [])
    node_count = observation.get("n8n_execution", {}).get("node_count") or runtime_payload.get("node_count")
    hash_result, hash_limitation = _check_manifest_hashes(root, manifest)
    forbidden_hits = _forbidden_overclaims(receipt, supported_claims)
    path_safe = _manifest_paths_are_safe(root, manifest)
    checks = {
        "core_files_present": all((root / rel).is_file() for rel in CORE_JSON_FILES),
        "display_files_present": all((root / rel).is_file() for rel in DISPLAY_FILES),
        "runtime_payload_found": (root / "artifacts" / "runtime_payload.json").is_file(),
        "workflow_slug_matches": observation.get("workflow_id") == runtime_payload.get("workflow_slug"),
        "n8n_execution_id_present": bool(observation.get("n8n_execution", {}).get("execution_id") or runtime_payload.get("n8n_execution_id")),
        "node_count_matches_trail": bool(node_trail) and int(node_count or 0) == len(node_trail),
        "minimum_node_count_met": int(node_count or 0) >= 7,
        "human_review_artifact_present": bool(runtime_payload.get("human_editorial_review") or observation.get("human_review_events")),
        "supported_claims_present": bool(supported_claims),
        "unsupported_claims_present": bool(unsupported_claims),
        "limitations_present": bool(limitations),
        "forbidden_overclaim_language_found": bool(forbidden_hits),
        "path_safety_passed": path_safe,
    }
    findings = _validation_findings(checks, missing_files, forbidden_hits)
    has_fail = any(finding["severity"] == "fail" for finding in findings)
    has_warn = any(finding["severity"] == "warn" for finding in findings)
    if has_fail:
        status = "validation_failed"
    elif has_warn:
        status = "validated_with_warnings"
    else:
        status = "validated_with_limitations"
    return {
        "validation_status": status,
        **checks,
        "artifact_hashes_checked": hash_result,
        "artifact_hash_limitation": hash_limitation,
        "validation_findings": findings,
    }


def _validation_findings(
    checks: dict[str, bool],
    missing_files: list[str],
    forbidden_hits: list[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key, passed in checks.items():
        if key == "display_files_present" and not passed:
            rows.append(
                {
                    "severity": "warn",
                    "code": key,
                    "message": "One or more display files are missing: " + ", ".join(missing_files),
                }
            )
        elif key == "forbidden_overclaim_language_found" and passed:
            rows.append(
                {
                    "severity": "fail",
                    "code": "forbidden_overclaim_language",
                    "message": "Forbidden founder-facing proof language found: " + ", ".join(forbidden_hits),
                }
            )
        elif key == "path_safety_passed" and not passed:
            rows.append({"severity": "fail", "code": key, "message": "Artifact manifest contains an unsafe packet path."})
        elif passed:
            rows.append({"severity": "pass", "code": key, "message": key.replace("_", " ") + " passed."})
        else:
            rows.append({"severity": "fail", "code": key, "message": key.replace("_", " ") + " failed."})
    return rows
```

- [ ] **Step 3: Append JSON, graph, artifact, and safety helpers**

```python
def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HyperframeReceiptError(f"invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise HyperframeReceiptError(f"{path.name} must contain a JSON object")
    return value


def _slug(label: str) -> str:
    normalized = label.lower().replace("/", " ").replace("&", "and").replace("-", " ")
    return "-".join(normalized.split())


def _aice_nodes() -> list[dict[str, Any]]:
    specs = [
        ("Manual Trigger", "trigger", [], ["topic", "thesis"]),
        ("Build Topic Brief", "transform", ["topic", "thesis"], ["topic_brief"]),
        ("Build Source Cards", "transform", ["topic_brief"], ["source_cards"]),
        ("Extract Claim and Quote Candidates", "transform", ["source_cards"], ["quote_candidates", "claim_map"]),
        ("Rights and Ambiguity Classification", "review", ["quote_candidates", "claim_map"], ["rights_review", "ambiguity_register"]),
        ("Human Editorial Review Stub", "human_review_gate", ["rights_review", "ambiguity_register"], ["human_review"]),
        ("Return Runtime Payload for Profusion", "handoff", ["human_review", "claim_map"], ["runtime_payload"]),
        ("Profusion Receipt Packet", "receipt_packet", ["runtime_payload"], ["workflow_receipt"]),
    ]
    return [
        {
            "id": _slug(label),
            "label": label,
            "type": node_type,
            "order": index,
            "summary": _node_summary(label),
            "inputs": inputs,
            "outputs": outputs,
            "derived": label == "Profusion Receipt Packet",
        }
        for index, (label, node_type, inputs, outputs) in enumerate(specs, start=1)
    ]


def _aice_edges() -> list[dict[str, Any]]:
    rows = [
        ("Manual Trigger", "Build Topic Brief", ["topic", "thesis"]),
        ("Build Topic Brief", "Build Source Cards", ["topic_brief"]),
        ("Build Source Cards", "Extract Claim and Quote Candidates", ["source_cards"]),
        ("Extract Claim and Quote Candidates", "Rights and Ambiguity Classification", ["quote_candidates", "claim_map"]),
        ("Rights and Ambiguity Classification", "Human Editorial Review Stub", ["rights_review", "ambiguity_register"]),
        ("Human Editorial Review Stub", "Return Runtime Payload for Profusion", ["human_review"]),
        ("Return Runtime Payload for Profusion", "Profusion Receipt Packet", ["runtime_payload"]),
    ]
    return [{"from": _slug(src), "to": _slug(dst), "data": data} for src, dst, data in rows]


def _data_lanes() -> list[dict[str, str]]:
    labels = [
        ("topic_thesis", "Topic / thesis", "Manual trigger to topic brief."),
        ("source_card", "Source card", "Topic brief to source-card evidence."),
        ("quote_candidate", "Quote candidate", "Source card to quote candidate."),
        ("claim_map", "Claim map", "Source card to mapped claim."),
        ("rights_review", "Rights review", "Claim and quote material to risk review."),
        ("ambiguity_register", "Ambiguity register", "Open uncertainties preserved."),
        ("human_review", "Human review state", "Human judgment enters before receipt."),
        ("runtime_payload", "Runtime payload", "n8n hands structured data to Profusion."),
        ("receipt_packet", "Receipt packet", "Profusion writes the evidence packet."),
    ]
    return [{"id": lane_id, "label": label, "summary": summary} for lane_id, label, summary in labels]


def _artifact_rows(manifest: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    manifest_rows = manifest.get("artifacts", [])
    rows: list[dict[str, Any]] = []
    purposes = {
        "workflow_receipt.html": "Finished buyer-readable receipt.",
        "workflow_receipt.md": "Markdown receipt.",
        "workflow_receipt.json": "Structured receipt source.",
        "m8_observation.json": "Workflow observation record.",
        "artifact_manifest.json": "Artifact index and hashes.",
        "artifacts/runtime_payload.json": "Original validated n8n runtime payload.",
    }
    for filename in REQUIRED_LEDGER_FILES:
        manifest_row = next(
            (row for row in manifest_rows if row.get("packet_path") == filename),
            {},
        )
        rows.append(
            {
                "id": manifest_row.get("artifact_id") or filename.replace("/", "."),
                "kind": manifest_row.get("artifact_type") or Path(filename).stem,
                "purpose": manifest_row.get("description") or purposes[filename],
                "path": filename,
                "hash": manifest_row.get("sha256"),
                "produced_by": "Profusion",
                "used_by": "receipt",
                "exists": (root / filename).is_file(),
            }
        )
    return rows


def _receipt_sections(runtime_payload: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "topic_brief": runtime_payload.get("topic_brief", {}),
        "source_cards": _items(runtime_payload.get("source_cards"), "sources"),
        "quote_candidates": _items(runtime_payload.get("quote_candidates"), "quote_candidates"),
        "claim_map": _items(runtime_payload.get("claim_map"), "claims"),
        "rights_review": _items(runtime_payload.get("rights_review"), "items"),
        "ambiguity_register": _items(runtime_payload.get("ambiguity_register"), "ambiguities"),
        "human_review": runtime_payload.get("human_editorial_review", {}),
        "supported_claims": receipt.get("claims_supported", []),
        "unsupported_claims": receipt.get("claims_not_supported", []),
        "limitations": receipt.get("limitations", []),
    }


def _items(value: object, key: str) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        items = value.get(key, [])
    else:
        items = value
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    return []


def _node_summary(label: str) -> str:
    summaries = {
        "Manual Trigger": "Starts the recorded AICE workspace proof.",
        "Build Topic Brief": "Structures the topic, editorial question, and thesis.",
        "Build Source Cards": "Creates metadata-only source-card evidence candidates.",
        "Extract Claim and Quote Candidates": "Creates claim and quote material from source context.",
        "Rights and Ambiguity Classification": "Preserves rights risk and unresolved uncertainty.",
        "Human Editorial Review Stub": "Makes human editorial judgment visible before receipt generation.",
        "Return Runtime Payload for Profusion": "Hands structured runtime evidence to Profusion.",
        "Profusion Receipt Packet": "Writes the reviewable receipt packet from runtime artifacts.",
    }
    return summaries[label]


def _check_manifest_hashes(root: Path, manifest: dict[str, Any]) -> tuple[bool | str, str]:
    rows = [row for row in manifest.get("artifacts", []) if row.get("packet_path") and row.get("sha256")]
    if not rows:
        return "partial", "Only manifest-listed hashes were available for validation."
    for row in rows:
        path = (root / row["packet_path"]).resolve()
        if not _is_relative_to(path, root) or not path.is_file():
            return False, "Manifest hash validation failed because a listed artifact was missing or unsafe."
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            return False, "Manifest hash validation failed because a listed artifact hash did not match."
    return True, ""


def _manifest_paths_are_safe(root: Path, manifest: dict[str, Any]) -> bool:
    for row in manifest.get("artifacts", []):
        packet_path = row.get("packet_path")
        if not isinstance(packet_path, str):
            continue
        if not _is_relative_to((root / packet_path).resolve(), root):
            return False
    return True


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _forbidden_overclaims(receipt: dict[str, Any], supported_claims: list[str]) -> list[str]:
    founder_facing_values = [receipt.get("workflow_purpose", ""), receipt.get("final_action", "")]
    founder_facing_values.extend(supported_claims)
    text = "\n".join(str(value).lower() for value in founder_facing_values)
    return [term for term in FORBIDDEN_FOUNDER_TERMS if term in text]


def escape_text(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)
```

- [ ] **Step 4: Run model tests to verify GREEN**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_load_aice_validator_model_normalizes_and_validates_good_packet tests/test_hyperframes_receipt_parser.py::test_load_aice_validator_model_warns_when_html_receipt_is_missing tests/test_hyperframes_receipt_parser.py::test_load_aice_validator_model_rejects_missing_core_json tests/test_hyperframes_receipt_parser.py::test_load_aice_validator_model_detects_forbidden_supported_claim -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit parser and validation slice**

```bash
git add tests/test_hyperframes_receipt_parser.py src/orchestrator/hyperframes_receipts.py
git commit -m "feat: add AICE receipt validator model"
```

## Task 3: Add Red Renderer Tests

**Files:**
- Modify: `tests/test_hyperframes_receipt_parser.py`
- Modify: `src/orchestrator/hyperframes_receipts.py`

- [ ] **Step 1: Append renderer tests**

```python
def test_render_aice_validator_view_includes_scene_ready_validator_sections(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_receipts import render_aice_validator_view

    packet_dir = make_runtime_packet(tmp_path)
    model = load_aice_hyperframe_model(packet_dir)

    html = render_aice_validator_view(model, local_url="http://127.0.0.1:8765/")

    assert "AICE Workflow Receipt Validator" in html
    assert "HyperFrames Explorer for one completed Profusion receipt packet" in html
    assert "Validated with limitations" in html
    assert "7 nodes executed" in html
    assert "6 receipt artifacts found" in html
    assert "2 claim boundaries present" in html
    assert "1 human review gate recorded" in html
    assert "Human Editorial Review Gate" in html
    assert "Execution" in html
    assert "Evidence" in html
    assert "Receipt" in html
    assert "Artifact Ledger" in html
    assert "Open finished receipt" in html
    assert "Supported Claims" in html
    assert "Unsupported Claims" in html
    assert "Limitations" in html
    assert "Copy Founder Proof Summary" in html
    assert "copyFounderProofSummary" in html
    assert 'data-prof-demo="aice-validator"' in html
    assert 'data-scene="validation-header"' in html
    assert 'data-scene="workflow-replay"' in html
    assert 'data-scene="human-review-gate"' in html
    assert 'data-scene="claim-boundary"' in html
    assert 'data-scene="artifact-ledger"' in html
    assert 'data-scene="founder-summary"' in html
    assert model["verification"]["safe_founder_claim"] in html


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
```

- [ ] **Step 2: Run renderer test to verify RED**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_render_aice_validator_view_includes_scene_ready_validator_sections -q
```

Expected: fail with `ImportError` for `render_aice_validator_view`.

## Task 4: Implement Scene-Ready Validator Rendering

**Files:**
- Modify: `src/orchestrator/hyperframes_receipts.py`
- Test: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Append the renderer entrypoint**

```python
def render_aice_validator_view(model: dict[str, Any], *, local_url: str) -> str:
    proof_summary = {
        "validation_status": model["validation"]["validation_status"],
        "workflow_name": model["workflow"]["name"],
        "execution_id": model["workflow"]["n8n_execution_id"],
        "node_count": model["workflow"]["node_count"],
        "receipt_path": model["receipt_path"],
        "safe_claim": model["founder_claim"],
        "supported_boundary": model["supported_claims"],
        "unsupported_boundary": model["unsupported_claims"],
        "limitations": model["limitations"],
        "local_viewer_url": local_url,
    }
    proof_summary_json = json.dumps(proof_summary, ensure_ascii=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape_text(VALIDATOR_TITLE)}</title>
  <style>{_validator_css()}</style>
</head>
<body>
  <main class="validator-shell" data-prof-demo="aice-validator">
    {_validation_header(model)}
    {_workflow_replay(model)}
    {_human_review_gate(model)}
    {_claim_boundary(model)}
    {_artifact_ledger(model)}
    {_receipt_viewer(model)}
    {_evidence_map(model)}
    {_validation_findings_panel(model)}
    {_founder_summary(model)}
  </main>
  <script>
    const proofSummary = {proof_summary_json};
    function copyFounderProofSummary() {{
      const text = [
        "Validation status: " + proofSummary.validation_status,
        "Workflow: " + proofSummary.workflow_name,
        "Execution ID: " + proofSummary.execution_id,
        "Node count: " + proofSummary.node_count,
        "Receipt path: " + proofSummary.receipt_path,
        "Safe claim: " + proofSummary.safe_claim,
        "Supported boundary: " + proofSummary.supported_boundary.join("; "),
        "Unsupported boundary: " + proofSummary.unsupported_boundary.join("; "),
        "Limitations: " + proofSummary.limitations.join("; "),
        "Local viewer URL: " + proofSummary.local_viewer_url
      ].join("\\n");
      navigator.clipboard.writeText(text).then(() => {{
        document.getElementById("copy-state").textContent = text;
      }}).catch(() => {{
        document.getElementById("copy-state").textContent = text;
      }});
    }}
    function selectNode(nodeId) {{
      for (const panel of document.querySelectorAll("[data-node-detail]")) {{
        panel.hidden = panel.getAttribute("data-node-detail") !== nodeId;
      }}
      for (const node of document.querySelectorAll("[data-node-id]")) {{
        node.classList.toggle("active", node.getAttribute("data-node-id") === nodeId);
      }}
    }}
  </script>
</body>
</html>"""


def render_aice_hyperframes_view(model: dict[str, Any], *, local_url: str) -> str:
    return render_aice_validator_view(model, local_url=local_url)
```

- [ ] **Step 2: Append section rendering helpers**

```python
def _validation_header(model: dict[str, Any]) -> str:
    workflow = model["workflow"]
    counters = model["proof_counters"]
    status_label = _status_label(model["validation"]["validation_status"])
    facts = [
        ("workflow name", workflow["name"]),
        ("evidence mode", workflow["evidence_mode"]),
        ("n8n workflow ID", workflow["n8n_workflow_id"]),
        ("execution ID", workflow["n8n_execution_id"]),
        ("node count", workflow["node_count"]),
        ("receipt ID/path", model["receipt_path"]),
    ]
    fact_html = "".join(_kv(label, value) for label, value in facts)
    counter_html = "".join(
        f'<div class="counter"><strong>{escape_text(value)}</strong><span>{escape_text(label)}</span></div>'
        for label, value in [
            ("nodes executed", counters["nodes_executed"]),
            ("receipt artifacts found", counters["receipt_artifacts_found"]),
            ("claim boundaries present", counters["claim_boundaries_present"]),
            ("human review gate recorded", counters["human_review_gates_recorded"]),
        ]
    )
    return (
        '<section class="validator-hero" data-scene="validation-header">'
        '<div class="hero-copy">'
        f'<p class="eyebrow">{escape_text(model["validator_subtitle"])}</p>'
        f'<h1>{escape_text(model["validator_title"])}</h1>'
        f'<p class="status-pill">{escape_text(status_label)}</p>'
        f'<p class="hero-claim">{escape_text("This n8n workflow ran. Profusion preserved what happened.")}</p>'
        f'<p>{escape_text(model["product_safe_explanation"])}</p>'
        '</div>'
        f'<div class="fact-grid">{fact_html}</div>'
        f'<div class="counter-grid">{counter_html}</div>'
        "</section>"
    )


def _workflow_replay(model: dict[str, Any]) -> str:
    nodes = []
    for index, node in enumerate(model["nodes"]):
        active = " active" if index == 0 else ""
        gate = " human-gate-node" if node["type"] == "human_review_gate" else ""
        nodes.append(
            '<button type="button" class="workflow-node'
            + active
            + gate
            + f'" data-node-id="{escape_text(node["id"])}" onclick="selectNode(\'{escape_text(node["id"])}\')">'
            + f'<span>{escape_text(node["order"])}</span><strong>{escape_text(node["label"])}</strong>'
            + f'<small>{escape_text(node["summary"])}</small></button>'
        )
    details = []
    for index, node in enumerate(model["nodes"]):
        details.append(
            '<article class="node-detail" data-node-detail="'
            + escape_text(node["id"])
            + '"'
            + ("" if index == 0 else " hidden")
            + ">"
            + f'<h3>{escape_text(node["label"])}</h3>'
            + f'<p>{escape_text(node["summary"])}</p>'
            + _kv("role", node["type"])
            + _kv("input data", ", ".join(node["inputs"]) or "none")
            + _kv("output data", ", ".join(node["outputs"]) or "none")
            + _kv("receipt trace", "See evidence map, artifact ledger, and finished receipt.")
            + "</article>"
        )
    lanes = "".join(
        f'<div class="lane"><strong>{escape_text(lane["label"])}</strong><span>{escape_text(lane["summary"])}</span></div>'
        for lane in model["data_lanes"]
    )
    return (
        '<section class="proof-stage" data-scene="workflow-replay">'
        '<div class="stage-labels"><span>Execution</span><span>Evidence</span><span>Receipt</span></div>'
        '<p class="note">' + escape_text(model["verification"]["lineage_note"]) + "</p>"
        '<div class="workflow-grid"><div class="node-chain">' + "".join(nodes) + "</div>"
        '<div class="node-details">' + "".join(details) + "</div></div>"
        '<div class="lanes">' + lanes + "</div>"
        "</section>"
    )


def _human_review_gate(model: dict[str, Any]) -> str:
    human_review = model["receipt_sections"]["human_review"]
    return (
        '<section class="human-review-gate" data-scene="human-review-gate">'
        "<h2>Human Editorial Review Gate</h2>"
        "<p>Human judgment enters before Profusion turns runtime evidence into a receipt packet.</p>"
        + _json_card("Recorded review state", human_review)
        + "</section>"
    )


def _claim_boundary(model: dict[str, Any]) -> str:
    supported = "".join(f"<li>{escape_text(item)}</li>" for item in model["supported_claims"])
    unsupported = "".join(f"<li>{escape_text(item)}</li>" for item in model["unsupported_claims"])
    limitations = "".join(f"<li>{escape_text(item)}</li>" for item in model["limitations"])
    return (
        '<section class="claim-boundary" data-scene="claim-boundary">'
        '<div class="panel"><h2>Supported Claims</h2><ul>' + supported + "</ul></div>"
        '<div class="panel warning"><h2>Unsupported Claims</h2><ul>' + unsupported + "</ul></div>"
        '<div class="panel limitations"><h2>Limitations</h2><ul>' + limitations + "</ul></div>"
        "</section>"
    )


def _artifact_ledger(model: dict[str, Any]) -> str:
    rows = []
    for artifact in model["artifacts"]:
        href = "/packet/" + escape_text(artifact["path"])
        link = f'<a href="{href}" target="_blank" rel="noreferrer">view</a>' if artifact["exists"] else "<span>missing</span>"
        rows.append(
            "<tr>"
            + f"<td>{escape_text(artifact['path'])}</td>"
            + f"<td>{escape_text(artifact['purpose'])}</td>"
            + f"<td>{escape_text(artifact.get('hash') or '')}</td>"
            + f"<td>{escape_text(artifact['exists'])}</td>"
            + f"<td>{link}</td>"
            + "</tr>"
        )
    return (
        '<section class="panel" data-scene="artifact-ledger"><h2>Artifact Ledger</h2>'
        '<table><thead><tr><th>File</th><th>Purpose</th><th>Hash</th><th>Exists</th><th>Open</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></section>"
    )
```

- [ ] **Step 3: Append remaining renderer helpers and CSS**

```python
def _receipt_viewer(model: dict[str, Any]) -> str:
    if not model["verification"]["html_receipt_found"]:
        return '<section class="panel"><h2>Receipt Viewer</h2><p>HTML receipt missing.</p></section>'
    return (
        '<section class="panel"><h2>Receipt Viewer</h2>'
        '<a class="button-link" href="/receipt" target="_blank" rel="noreferrer">Open finished receipt</a>'
        '<iframe src="/receipt" title="Finished workflow receipt"></iframe></section>'
    )


def _evidence_map(model: dict[str, Any]) -> str:
    sections = model["receipt_sections"]
    cards = [
        _json_card("Topic / thesis", sections["topic_brief"]),
        _json_card("Source card", sections["source_cards"]),
        _json_card("Quote candidate", sections["quote_candidates"]),
        _json_card("Claim map", sections["claim_map"]),
        _json_card("Rights review", sections["rights_review"]),
        _json_card("Ambiguity register", sections["ambiguity_register"]),
    ]
    return '<section class="panel"><h2>Evidence Map</h2><div class="cards">' + "".join(cards) + "</div></section>"


def _validation_findings_panel(model: dict[str, Any]) -> str:
    findings = "".join(
        f'<li class="{escape_text(finding["severity"])}"><strong>{escape_text(finding["severity"].upper())}</strong> {escape_text(finding["message"])}</li>'
        for finding in model["validation"]["validation_findings"]
    )
    return '<section class="panel"><h2>Validation Findings</h2><ul class="findings">' + findings + "</ul></section>"


def _founder_summary(model: dict[str, Any]) -> str:
    return (
        '<section class="panel founder-summary" data-scene="founder-summary">'
        "<h2>Founder Proof Summary</h2>"
        f'<p class="big-claim">{escape_text(model["founder_claim"])}</p>'
        '<button type="button" onclick="copyFounderProofSummary()">Copy Founder Proof Summary</button>'
        '<pre id="copy-state" class="copy-state"></pre>'
        "</section>"
    )


def _json_card(title: str, value: object) -> str:
    text = json.dumps(value, ensure_ascii=True, indent=2)
    return f'<article class="card"><h3>{escape_text(title)}</h3><pre>{escape_text(text)}</pre></article>'


def _kv(label: str, value: object) -> str:
    return f'<div class="kv"><span>{escape_text(label)}</span><strong>{escape_text(value)}</strong></div>'


def _status_label(status: str) -> str:
    labels = {
        "validated_with_limitations": "Validated with limitations",
        "validated_with_warnings": "Validated with warnings",
        "validation_failed": "Validation failed",
    }
    return labels.get(status, status)


def _validator_css() -> str:
    return """
:root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
body { margin: 0; background: #eef2f6; color: #17202a; }
.validator-shell { max-width: 1480px; margin: 0 auto; padding: 28px; }
.validator-hero, .proof-stage, .human-review-gate, .panel { background: #fff; border: 1px solid #cfd8e3; border-radius: 8px; padding: 22px; box-shadow: 0 1px 2px rgba(16,24,40,.06); margin-top: 16px; }
.validator-hero { margin-top: 0; display: grid; grid-template-columns: minmax(340px, 1.2fr) minmax(320px, .9fr); gap: 18px; align-items: start; }
.eyebrow { margin: 0 0 8px; color: #4b5d73; font-size: 13px; text-transform: uppercase; letter-spacing: .08em; }
h1 { margin: 0; font-size: 42px; line-height: 1.05; letter-spacing: 0; }
h2, h3 { letter-spacing: 0; }
.status-pill { display: inline-flex; margin: 14px 0 0; padding: 8px 12px; border-radius: 999px; background: #12343b; color: #fff; font-weight: 800; }
.hero-claim, .big-claim { font-size: 18px; font-weight: 800; }
.fact-grid, .counter-grid, .cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.counter { border: 1px solid #cfd8e3; border-radius: 8px; padding: 14px; background: #f8fafc; }
.counter strong { display: block; font-size: 28px; }
.counter span, .kv span, .note { color: #5f6f83; font-size: 13px; }
.kv { display: flex; flex-direction: column; gap: 4px; border-top: 1px solid #e4eaf1; padding-top: 10px; }
.stage-labels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-weight: 900; text-transform: uppercase; color: #4b5d73; }
.workflow-grid, .claim-boundary { display: grid; grid-template-columns: 1.1fr .9fr; gap: 16px; margin-top: 16px; }
.node-chain { display: grid; gap: 8px; }
.workflow-node { text-align: left; border: 1px solid #cfd8e3; border-radius: 8px; padding: 12px; background: #f8fafc; cursor: pointer; font: inherit; }
.workflow-node span { display: inline-grid; place-items: center; width: 26px; height: 26px; margin-right: 8px; border-radius: 999px; background: #17202a; color: #fff; font-size: 12px; }
.workflow-node small { display: block; color: #5f6f83; margin-top: 6px; }
.workflow-node.active { border-color: #0f5e5c; box-shadow: inset 0 0 0 1px #0f5e5c; }
.human-gate-node, .human-review-gate { border-color: #9b5c00; background: #fff8ec; }
.lanes { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-top: 16px; }
.lane, .card { border: 1px solid #cfd8e3; border-radius: 8px; padding: 12px; background: #f8fafc; }
.lane span { display: block; margin-top: 6px; color: #5f6f83; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { border-top: 1px solid #dfe7f0; padding: 10px; text-align: left; vertical-align: top; }
iframe { width: 100%; height: 520px; border: 1px solid #cfd8e3; border-radius: 8px; margin-top: 12px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px; }
button, .button-link { display: inline-flex; align-items: center; min-height: 38px; padding: 8px 12px; border: 1px solid #17202a; border-radius: 8px; background: #17202a; color: #fff; text-decoration: none; cursor: pointer; }
.findings { display: grid; gap: 8px; padding-left: 0; list-style: none; }
.findings li { border-radius: 8px; padding: 10px; border: 1px solid #cfd8e3; }
.findings .pass { background: #eef8f1; }
.findings .warn { background: #fff8ec; }
.findings .fail { background: #fff0f0; }
@media (max-width: 900px) { .validator-hero, .workflow-grid, .claim-boundary, .fact-grid, .counter-grid { grid-template-columns: 1fr; } .validator-shell { padding: 16px; } }
"""
```

- [ ] **Step 4: Run renderer tests to verify GREEN**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_render_aice_validator_view_includes_scene_ready_validator_sections tests/test_hyperframes_receipt_parser.py::test_render_aice_validator_view_escapes_receipt_text -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit renderer slice**

```bash
git add tests/test_hyperframes_receipt_parser.py src/orchestrator/hyperframes_receipts.py
git commit -m "feat: render AICE receipt validator"
```

## Task 5: Add Red Server And CLI Tests

**Files:**
- Modify: `tests/test_hyperframes_receipt_parser.py`
- Create: `src/orchestrator/hyperframes_server.py`
- Modify: `src/orchestrator/cli.py`

- [ ] **Step 1: Append server and CLI tests**

```python
def test_aice_hyperframes_app_serves_validator_model_receipt_and_artifact(tmp_path: Path):
    from orchestrator.hyperframes_server import create_aice_hyperframes_app

    packet_dir = make_runtime_packet(tmp_path)
    client = TestClient(create_aice_hyperframes_app(packet_dir, local_url="http://127.0.0.1:8765/"))

    home = client.get("/")
    assert home.status_code == 200
    assert "AICE Workflow Receipt Validator" in home.text
    assert "Validated with limitations" in home.text

    model = client.get("/api/model")
    assert model.status_code == 200
    assert model.json()["validation"]["validation_status"] == "validated_with_limitations"

    receipt = client.get("/receipt")
    assert receipt.status_code == 200
    assert "AICE Source-to-Narrative Workflow Receipt" in receipt.text

    artifact = client.get("/artifacts/runtime_payload.json")
    assert artifact.status_code == 200
    assert artifact.json()["workflow_slug"] == AICE_SLUG

    packet_file = client.get("/packet/workflow_receipt.json")
    assert packet_file.status_code == 200
    assert packet_file.json()["workflow_name"] == "AICE Source-to-Narrative Workflow Receipt"

    blocked = client.get("/artifacts/../../workflow_receipt.json")
    assert blocked.status_code == 404

    blocked_packet = client.get("/packet/../../pyproject.toml")
    assert blocked_packet.status_code == 404


def test_hyperframes_validate_cli_dry_run_prints_validator_language(tmp_path: Path):
    packet_dir = make_runtime_packet(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "hyperframes",
            "validate",
            "--receipt-dir",
            str(packet_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "AICE Workflow Receipt Validator" in result.output
    assert "Validation status: validated_with_limitations" in result.output
    assert "Local URL: http://127.0.0.1:8765/" in result.output
    assert "Open this first: http://127.0.0.1:8765/" in result.output
    assert "Receipt packet:" in result.output


def test_hyperframes_serve_cli_remains_compatibility_alias(tmp_path: Path):
    packet_dir = make_runtime_packet(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "hyperframes",
            "serve",
            "--receipt-dir",
            str(packet_dir),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "AICE Workflow Receipt Validator" in result.output
    assert "Validation status: validated_with_limitations" in result.output
```

- [ ] **Step 2: Run CLI test to verify RED**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_hyperframes_validate_cli_dry_run_prints_validator_language -q
```

Expected: fail because `hyperframes validate` is not registered.

## Task 6: Implement Local Server And CLI Commands

**Files:**
- Create: `src/orchestrator/hyperframes_server.py`
- Modify: `src/orchestrator/cli.py`
- Test: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Add the local FastAPI server module**

```python
"""Local server for the AICE Workflow Receipt Validator."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from orchestrator.hyperframes_receipts import VALIDATOR_TITLE
from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
from orchestrator.hyperframes_receipts import render_aice_validator_view


def create_aice_hyperframes_app(
    receipt_dir: Path | str,
    *,
    local_url: str,
) -> FastAPI:
    root = Path(receipt_dir).expanduser().resolve()
    model = load_aice_hyperframe_model(root)
    viewer_html = render_aice_validator_view(model, local_url=local_url)
    app = FastAPI(title=VALIDATOR_TITLE, version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    def get_viewer() -> str:
        return viewer_html

    @app.get("/api/model")
    def get_model() -> dict:
        return model

    @app.get("/receipt")
    def get_receipt() -> FileResponse:
        receipt_path = root / "workflow_receipt.html"
        if not receipt_path.is_file():
            raise HTTPException(status_code=404, detail="workflow_receipt.html not found")
        return FileResponse(str(receipt_path), media_type="text/html")

    @app.get("/packet/{packet_path:path}")
    def get_packet_file(packet_path: str) -> FileResponse:
        requested = (root / packet_path).resolve()
        try:
            requested.relative_to(root)
        except ValueError:
            raise HTTPException(status_code=404, detail="packet file not found")
        if not requested.is_file():
            raise HTTPException(status_code=404, detail="packet file not found")
        return FileResponse(str(requested))

    @app.get("/artifacts/{artifact_path:path}")
    def get_artifact(artifact_path: str) -> FileResponse:
        requested = (root / "artifacts" / artifact_path).resolve()
        artifacts_root = (root / "artifacts").resolve()
        try:
            requested.relative_to(artifacts_root)
        except ValueError:
            raise HTTPException(status_code=404, detail="artifact not found")
        if not requested.is_file():
            raise HTTPException(status_code=404, detail="artifact not found")
        return FileResponse(str(requested))

    return app
```

- [ ] **Step 2: Register the CLI group and shared runner**

Add the `hyperframes_app` Typer group near the other top-level Typer groups in
`src/orchestrator/cli.py`:

```python
hyperframes_app = typer.Typer(help="Local HyperFrames receipt validator tools.")
app.add_typer(hyperframes_app, name="hyperframes")
```

Add the shared runner near the M8-GTM commands:

```python
def _run_hyperframes_validator(
    *,
    receipt_dir: Path | None,
    host: str,
    port: int,
    dry_run: bool,
) -> None:
    import uvicorn

    from orchestrator.hyperframes_receipts import VALIDATOR_TITLE
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_server import create_aice_hyperframes_app

    if receipt_dir is None:
        console.print("[red]--receipt-dir is required[/red]")
        raise typer.Exit(code=2)

    local_url = f"http://{host}:{port}/"
    try:
        model = load_aice_hyperframe_model(receipt_dir)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    _print_key_values(
        VALIDATOR_TITLE,
        [
            ("Receipt packet", str(Path(receipt_dir).resolve())),
            ("Validation status", model["validation"]["validation_status"]),
            ("Workflow", model["workflow"]["name"]),
            ("Execution ID", model["workflow"]["n8n_execution_id"]),
            ("Node count", model["workflow"]["node_count"]),
            ("Local URL", local_url),
            ("Open this first", local_url),
            ("Boundary", "Local validator only; receipt remains source of truth."),
        ],
    )
    if dry_run:
        return

    server_app = create_aice_hyperframes_app(receipt_dir, local_url=local_url)
    uvicorn.run(server_app, host=host, port=port, log_level="info")
```

- [ ] **Step 3: Register `validate` and compatibility `serve` commands**

```python
@hyperframes_app.command("validate")
def hyperframes_validate(
    receipt_dir: Path | None = typer.Option(
        None,
        "--receipt-dir",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="AICE receipt packet directory.",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Local bind host. Keep 127.0.0.1 unless Kyle explicitly approves exposure.",
    ),
    port: int = typer.Option(8765, "--port", min=1024, max=65535),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Parse and validate the packet without starting the blocking server.",
    ),
) -> None:
    """Run the local AICE Workflow Receipt Validator."""

    _run_hyperframes_validator(
        receipt_dir=receipt_dir,
        host=host,
        port=port,
        dry_run=dry_run,
    )


@hyperframes_app.command("serve")
def hyperframes_serve(
    receipt_dir: Path | None = typer.Option(
        None,
        "--receipt-dir",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="AICE receipt packet directory.",
    ),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8765, "--port", min=1024, max=65535),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Compatibility alias for the local AICE Workflow Receipt Validator."""

    _run_hyperframes_validator(
        receipt_dir=receipt_dir,
        host=host,
        port=port,
        dry_run=dry_run,
    )
```

- [ ] **Step 4: Run server and CLI tests to verify GREEN**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_aice_hyperframes_app_serves_validator_model_receipt_and_artifact tests/test_hyperframes_receipt_parser.py::test_hyperframes_validate_cli_dry_run_prints_validator_language tests/test_hyperframes_receipt_parser.py::test_hyperframes_serve_cli_remains_compatibility_alias -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit server and CLI slice**

```bash
git add tests/test_hyperframes_receipt_parser.py src/orchestrator/hyperframes_server.py src/orchestrator/cli.py
git commit -m "feat: serve local AICE receipt validator"
```

## Task 7: Add Runbook And Boundary Docs

**Files:**
- Create: `docs/runbooks/aice_workflow_receipt_validator.md`
- Modify: `docs/runbooks/README.md`

- [ ] **Step 1: Write the runbook**

````markdown
# AICE Workflow Receipt Validator Runbook

Date: 2026-05-19
Status: Local-only PR5 demo bridge

## Purpose

The AICE Workflow Receipt Validator turns one completed AICE receipt packet into
a local validation replay. It helps Kyle inspect what ran, what data moved, what
artifacts exist, where human review entered, what the receipt supports, and what
it does not prove.

The HyperFrames Explorer is the interactive view inside the validator. The
receipt packet remains the source of truth.

## Command

```bash
uv run profusion hyperframes validate \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a
```

Open:

```text
http://127.0.0.1:8765/
```

Dry-run preflight:

```bash
uv run profusion hyperframes validate \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a \
  --dry-run
```

Compatibility command:

```bash
uv run profusion hyperframes serve \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a
```

## Required Receipt Files

- `artifact_manifest.json`
- `m8_observation.json`
- `workflow_receipt.json`
- `workflow_receipt.md`
- `workflow_receipt.html`
- `artifacts/runtime_payload.json`

## What To Look At First

Start with the validation header and workflow replay. Confirm:

- `AICE Workflow Receipt Validator`
- `Validated with limitations`
- evidence mode `workspace_runtime_n8n_payload`
- n8n workflow ID
- execution ID
- node count `7`
- `Human Editorial Review Gate`
- `Profusion Receipt Packet` terminal frame
- supported and unsupported claims side by side
- limitations visible near the claim boundary

## What This Validates

This validates that a completed receipt packet can be loaded locally and
inspected as a reviewable workflow evidence packet. It shows the recorded n8n
node trail, runtime payload, receipt artifacts, final HTML receipt, supported
claims, unsupported claims, limitations, and copyable founder proof summary.

## What This Does Not Validate

- public production deployment
- public Profusion API exposure
- live source credentials
- legal clearance
- fair-use approval
- factual truth certification
- platform-policy compliance
- publication safety
- customer traction
- production readiness
- MP4 rendering

## Safe Claim

```text
This n8n workflow ran. Profusion preserved what happened. The receipt tells you what the evidence supports and what it does not.
```
````

- [ ] **Step 2: Add the runbook link**

Add this bullet to `docs/runbooks/README.md`:

```markdown
- [AICE Workflow Receipt Validator](aice_workflow_receipt_validator.md) - local-only validator for one completed AICE receipt packet.
```

- [ ] **Step 3: Verify docs whitespace**

```bash
git diff --check
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Commit docs slice**

```bash
git add docs/runbooks/aice_workflow_receipt_validator.md docs/runbooks/README.md
git commit -m "docs: add AICE receipt validator runbook"
```

## Task 8: Final Verification

**Files:**
- Verify all files changed by Tasks 1-7.

- [ ] **Step 1: Run targeted validator tests**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py -q
```

Expected: all AICE Workflow Receipt Validator tests pass.

- [ ] **Step 2: Run receipt regression tests**

```bash
uv run pytest tests/test_m8_aice_runtime_payload.py tests/test_m8_aice_receipt_harness.py -q
```

Expected: AICE runtime and receipt harness tests pass.

- [ ] **Step 3: Run full repo tests**

```bash
uv run pytest -q
```

Expected: full suite passes.

- [ ] **Step 4: Run smoke and whitespace checks**

```bash
uv run profusion smoke --offline
git diff --check
```

Expected: offline smoke passes and whitespace check returns no output.

- [ ] **Step 5: Run the manual validator preflight against the current AICE packet**

```bash
uv run profusion hyperframes validate \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a \
  --dry-run
```

Expected output includes:

```text
AICE Workflow Receipt Validator
Receipt packet: /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a
Validation status: validated_with_limitations
Workflow: AICE Source-to-Narrative Workflow Receipt
Execution ID: 1
Node count: 7
Local URL: http://127.0.0.1:8765/
Open this first: http://127.0.0.1:8765/
```

- [ ] **Step 6: Check that only intended files are modified**

```bash
git status --short
```

Expected: only PR5 implementation files are changed. If another session changed
`docs/runbooks/release-checklist.md`, leave that file unstaged unless Kyle asks
to include it.

## Execution Boundary

This PR5 plan creates the local validator and HyperFrames Explorer view. It does
not create a HyperFrames MP4. A follow-on render slice can use the normalized
model and scene-ready DOM as input to a real HyperFrames composition only after
the validator proves the receipt narrative is correct.

## Plan Self-Review

- Spec coverage: covers Validator naming, Explorer sub-mode, parser, validation
  object, visual replay, human review gate, artifact ledger, receipt viewer,
  evidence map, supported/unsupported claims, limitations, validation findings,
  copy summary, local server, `validate` command, `serve` compatibility alias,
  runbook, and final verification.
- Scope check: single local-only validator slice; no public deployment, no M7
  cockpit mutation, no API guard PR4 work, no React/JSX/frontend framework, no
  public tunnel, no MP4 claim.
- TDD check: every implementation task starts with a failing pytest target
  before production code.
- Boundary check: all founder-facing claims are bounded to receipt-packet
  inspectability and the exact safe claim.
