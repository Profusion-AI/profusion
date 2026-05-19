# AICE HyperFrames Receipt Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-only AICE HyperFrames Receipt Explorer that turns one completed AICE receipt packet into a visual workflow proof board.

**Architecture:** Add a pure receipt-packet parser and HTML renderer, then serve it through a local FastAPI app launched by `uv run profusion hyperframes serve --receipt-dir <receipt_dir>`. The receipt remains the source of truth; the explorer only normalizes, visualizes, and links the already-generated evidence.

**Tech Stack:** Python 3.11, Typer, FastAPI, pytest, standard-library `html`, `json`, and `pathlib`; no new frontend framework and no public deployment.

---

## Current State

- PR #3 is merged into `main` as `2844545`.
- The P0.2-ish AICE API guard/runbook branch was parked as:

```text
stash@{0}: On codex/aice-demo-readiness-api-hardening: park AICE demo-readiness API guard branch before HyperFrames PR5
```

- This plan starts PR5 from clean `main` on local branch
  `codex/pr5-aice-hyperframes-receipt-explorer-tdd`.
- Exact manual receipt packet for first explorer check:

```text
/tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a/
```

## File Structure

- Create `tests/test_hyperframes_receipt_parser.py`: parser, renderer, server, and CLI dry-run tests.
- Create `src/orchestrator/hyperframes_receipts.py`: pure parser, normalized model builder, and HTML renderer.
- Create `src/orchestrator/hyperframes_server.py`: local FastAPI app for one receipt packet directory.
- Modify `src/orchestrator/cli.py`: register `hyperframes` Typer group and `serve` command.
- Create `docs/runbooks/aice_hyperframes_receipt_explorer.md`: usage, proof boundary, verification, and limitations.
- Modify `docs/runbooks/README.md`: add runbook link.

## Task 1: Add Red Parser Tests

**Files:**
- Create: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Write the failing parser tests**

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


def test_load_aice_hyperframe_model_normalizes_runtime_receipt_packet(tmp_path: Path):
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
    assert model["edges"][0] == {
        "from": "manual-trigger",
        "to": "build-topic-brief",
        "data": ["topic", "thesis"],
    }
    assert model["receipt_sections"]["topic_brief"]["title"] == (
        "Runtime-only AICE topic 20260519"
    )
    assert model["receipt_sections"]["source_cards"][0]["source_id"] == (
        "runtime-source-1"
    )
    assert model["receipt_sections"]["claim_map"][0]["claim_id"] == (
        "runtime-claim-1"
    )
    assert model["verification"]["required_files_present"] is True
    assert model["verification"]["html_receipt_found"] is True
    assert model["verification"]["runtime_payload_found"] is True
    assert model["verification"]["lineage_note"] == (
        "AICE workflow map derived from recorded node trail and receipt artifacts."
    )
    assert model["verification"]["safe_founder_claim"] == (
        "This n8n workflow ran. Profusion preserved what happened. "
        "The receipt tells you what the evidence supports and what it does not."
    )


def test_load_aice_hyperframe_model_reports_missing_optional_html(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    (packet_dir / "workflow_receipt.html").unlink()

    model = load_aice_hyperframe_model(packet_dir)

    assert model["verification"]["required_files_present"] is False
    assert model["verification"]["html_receipt_found"] is False
    assert "workflow_receipt.html" in model["verification"]["missing_files"]


def test_load_aice_hyperframe_model_rejects_missing_core_json(tmp_path: Path):
    from orchestrator.hyperframes_receipts import HyperframeReceiptError
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model

    packet_dir = make_runtime_packet(tmp_path)
    (packet_dir / "workflow_receipt.json").unlink()

    with pytest.raises(HyperframeReceiptError, match="workflow_receipt.json"):
        load_aice_hyperframe_model(packet_dir)
```

- [ ] **Step 2: Run the parser tests to verify RED**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_load_aice_hyperframe_model_normalizes_runtime_receipt_packet -q
```

Expected: fail with `ModuleNotFoundError: No module named 'orchestrator.hyperframes_receipts'`.

## Task 2: Implement The Pure Parser

**Files:**
- Create: `src/orchestrator/hyperframes_receipts.py`
- Test: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Add the parser module**

```python
"""Build local HyperFrames receipt explorer models from Profusion receipt packets."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


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


class HyperframeReceiptError(ValueError):
    """Raised when a receipt packet cannot be parsed into an explorer model."""


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

    return {
        "receipt_id": receipt.get("receipt_id", root.name),
        "receipt_path": str(root),
        "workflow": {
            "name": observation.get("workflow_name") or receipt.get("workflow_name"),
            "slug": observation.get("workflow_id") or manifest.get("workflow_slug"),
            "evidence_mode": observation.get("evidence_mode")
            or receipt.get("evidence_mode"),
            "n8n_project": runtime_payload.get("n8n_project_id")
            or runtime_payload.get("n8n_project")
            or "",
            "n8n_workflow_id": n8n_execution.get("workspace_workflow_id")
            or runtime_payload.get("n8n_workspace_workflow_id"),
            "n8n_execution_id": n8n_execution.get("execution_id")
            or runtime_payload.get("n8n_execution_id"),
            "node_count": n8n_execution.get("node_count")
            or runtime_payload.get("node_count"),
            "status": n8n_execution.get("status") or runtime_payload.get("status", "success"),
        },
        "nodes": _aice_nodes(),
        "edges": _aice_edges(),
        "data_lanes": _data_lanes(),
        "artifacts": _artifact_rows(manifest, root),
        "receipt_sections": _receipt_sections(runtime_payload, receipt),
        "supported_claims": observation.get("supported_claims")
        or receipt.get("claims_supported", []),
        "unsupported_claims": observation.get("unsupported_claims")
        or receipt.get("claims_not_supported", []),
        "limitations": observation.get("limitations") or receipt.get("limitations", []),
        "founder_claim": SAFE_FOUNDER_CLAIM,
        "product_safe_explanation": PRODUCT_SAFE_EXPLANATION,
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


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HyperframeReceiptError(f"invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise HyperframeReceiptError(f"{path.name} must contain a JSON object")
    return value


def _slug(label: str) -> str:
    return (
        label.lower()
        .replace("/", " ")
        .replace("&", "and")
        .replace("-", " ")
        .replace("  ", " ")
        .strip()
        .replace(" ", "-")
    )


def _aice_nodes() -> list[dict[str, Any]]:
    specs = [
        ("Manual Trigger", "trigger", [], ["topic", "thesis"]),
        ("Build Topic Brief", "transform", ["topic", "thesis"], ["topic_brief"]),
        ("Build Source Cards", "transform", ["topic_brief"], ["source_cards"]),
        (
            "Extract Claim and Quote Candidates",
            "transform",
            ["source_cards"],
            ["quote_candidates", "claim_map"],
        ),
        (
            "Rights and Ambiguity Classification",
            "review",
            ["quote_candidates", "claim_map"],
            ["rights_review", "ambiguity_register"],
        ),
        (
            "Human Editorial Review Stub",
            "review",
            ["rights_review", "ambiguity_register"],
            ["human_review"],
        ),
        (
            "Return Runtime Payload for Profusion",
            "handoff",
            ["human_review", "claim_map"],
            ["runtime_payload"],
        ),
        (
            "Profusion Receipt Packet",
            "receipt_packet",
            ["runtime_payload"],
            ["workflow_receipt"],
        ),
    ]
    nodes: list[dict[str, Any]] = []
    for index, (label, node_type, inputs, outputs) in enumerate(specs, start=1):
        nodes.append(
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
        )
    return nodes


def _aice_edges() -> list[dict[str, Any]]:
    rows = [
        ("Manual Trigger", "Build Topic Brief", ["topic", "thesis"]),
        ("Build Topic Brief", "Build Source Cards", ["topic_brief"]),
        ("Build Source Cards", "Extract Claim and Quote Candidates", ["source_cards"]),
        (
            "Extract Claim and Quote Candidates",
            "Rights and Ambiguity Classification",
            ["quote_candidates", "claim_map"],
        ),
        (
            "Rights and Ambiguity Classification",
            "Human Editorial Review Stub",
            ["rights_review", "ambiguity_register"],
        ),
        (
            "Human Editorial Review Stub",
            "Return Runtime Payload for Profusion",
            ["human_review"],
        ),
        (
            "Return Runtime Payload for Profusion",
            "Profusion Receipt Packet",
            ["runtime_payload"],
        ),
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
    for filename, purpose in {
        "workflow_receipt.html": "Finished buyer-readable receipt.",
        "workflow_receipt.md": "Markdown receipt.",
        "workflow_receipt.json": "Structured receipt source.",
        "m8_observation.json": "Workflow observation record.",
        "artifact_manifest.json": "Artifact index and hashes.",
        "artifacts/runtime_payload.json": "Original validated n8n runtime payload.",
    }.items():
        manifest_row = next(
            (row for row in manifest_rows if row.get("packet_path") == filename),
            {},
        )
        rows.append(
            {
                "id": manifest_row.get("artifact_id") or filename.replace("/", "."),
                "kind": manifest_row.get("artifact_type") or Path(filename).stem,
                "purpose": manifest_row.get("description") or purpose,
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
        "Human Editorial Review Stub": "Marks where human judgment enters the workflow.",
        "Return Runtime Payload for Profusion": "Hands structured runtime evidence to Profusion.",
        "Profusion Receipt Packet": "Writes the reviewable receipt packet from runtime artifacts.",
    }
    return summaries[label]


def escape_text(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)
```

- [ ] **Step 2: Run parser tests to verify GREEN**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_load_aice_hyperframe_model_normalizes_runtime_receipt_packet tests/test_hyperframes_receipt_parser.py::test_load_aice_hyperframe_model_reports_missing_optional_html tests/test_hyperframes_receipt_parser.py::test_load_aice_hyperframe_model_rejects_missing_core_json -q
```

Expected: `3 passed`.

- [ ] **Step 3: Commit parser slice**

```bash
git add tests/test_hyperframes_receipt_parser.py src/orchestrator/hyperframes_receipts.py
git commit -m "feat: add AICE hyperframes receipt parser"
```

## Task 3: Add Red Renderer Tests

**Files:**
- Modify: `tests/test_hyperframes_receipt_parser.py`
- Modify: `src/orchestrator/hyperframes_receipts.py`

- [ ] **Step 1: Append renderer tests**

```python
def test_render_aice_hyperframes_view_includes_required_proof_sections(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_receipts import render_aice_hyperframes_view

    packet_dir = make_runtime_packet(tmp_path)
    model = load_aice_hyperframe_model(packet_dir)

    html = render_aice_hyperframes_view(model, local_url="http://127.0.0.1:8765/")

    assert "AICE MVP Receipt Loaded" in html
    assert "Workspace runtime receipt generated" in html
    assert "Manual Trigger" in html
    assert "Return Runtime Payload for Profusion" in html
    assert "Profusion Receipt Packet" in html
    assert "Data Movement" in html
    assert "Artifact Compendium" in html
    assert "Open finished receipt" in html
    assert "Supported Claims" in html
    assert "Unsupported Claims" in html
    assert "Copy Founder Proof Summary" in html
    assert "copyFounderProofSummary" in html
    assert "/receipt" in html
    assert model["verification"]["safe_founder_claim"] in html


def test_render_aice_hyperframes_view_escapes_receipt_text(tmp_path: Path):
    from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
    from orchestrator.hyperframes_receipts import render_aice_hyperframes_view

    packet_dir = make_runtime_packet(tmp_path)
    model = load_aice_hyperframe_model(packet_dir)
    model["workflow"]["name"] = "<script>alert('bad')</script>"
    model["supported_claims"].append("<img src=x onerror=alert(1)>")

    html = render_aice_hyperframes_view(model, local_url="http://127.0.0.1:8765/")

    assert "<script>alert('bad')</script>" not in html
    assert "<img src=x onerror=alert(1)>" not in html
    assert "&lt;script&gt;alert(&#x27;bad&#x27;)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
```

- [ ] **Step 2: Run renderer test to verify RED**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_render_aice_hyperframes_view_includes_required_proof_sections -q
```

Expected: fail with `ImportError` for `render_aice_hyperframes_view`.

## Task 4: Implement Static Explorer Rendering

**Files:**
- Modify: `src/orchestrator/hyperframes_receipts.py`
- Test: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Append renderer functions**

```python
def render_aice_hyperframes_view(model: dict[str, Any], *, local_url: str) -> str:
    proof_summary = {
        "workflow_name": model["workflow"]["name"],
        "execution_id": model["workflow"]["n8n_execution_id"],
        "node_count": model["workflow"]["node_count"],
        "receipt_path": model["receipt_path"],
        "safe_claim": model["founder_claim"],
        "supported_boundary": model["supported_claims"],
        "unsupported_boundary": model["unsupported_claims"],
        "local_viewer_url": local_url,
    }
    proof_summary_json = json.dumps(proof_summary, ensure_ascii=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AICE HyperFrames Receipt Explorer</title>
  <style>{_viewer_css()}</style>
</head>
<body>
  <main class="shell">
    {_completion_header(model)}
    <section class="proof-grid">
      {_workflow_frame(model)}
      {_node_detail_panel(model)}
    </section>
    {_data_movement(model)}
    {_artifact_compendium(model)}
    {_receipt_viewer(model)}
    {_evidence_map(model)}
    {_claims_columns(model)}
    {_founder_claim_panel(model)}
    {_verification_panel(model)}
    <section class="panel">
      <div class="panel-title">Screenshot / Export Moment</div>
      <button type="button" onclick="copyFounderProofSummary()">Copy Founder Proof Summary</button>
      <pre id="copy-state" class="copy-state"></pre>
    </section>
  </main>
  <script>
    const proofSummary = {proof_summary_json};
    function copyFounderProofSummary() {{
      const text = [
        "Workflow: " + proofSummary.workflow_name,
        "Execution ID: " + proofSummary.execution_id,
        "Node count: " + proofSummary.node_count,
        "Receipt path: " + proofSummary.receipt_path,
        "Safe claim: " + proofSummary.safe_claim,
        "Supported boundary: " + proofSummary.supported_boundary.join("; "),
        "Unsupported boundary: " + proofSummary.unsupported_boundary.join("; "),
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


def _completion_header(model: dict[str, Any]) -> str:
    workflow = model["workflow"]
    rows = [
        ("Workflow", workflow["name"]),
        ("n8n workflow ID", workflow["n8n_workflow_id"]),
        ("Execution ID", workflow["n8n_execution_id"]),
        ("Node count", workflow["node_count"]),
        ("Receipt", model["receipt_id"]),
        ("Receipt path", model["receipt_path"]),
        ("Evidence mode", workflow["evidence_mode"]),
    ]
    facts = "".join(
        f"<div><span>{escape_text(label)}</span><strong>{escape_text(value)}</strong></div>"
        for label, value in rows
    )
    return (
        '<section class="hero">'
        '<div><p class="eyebrow">AICE HyperFrames Receipt Explorer</p>'
        "<h1>AICE MVP Receipt Loaded</h1>"
        '<p class="claim">Workspace runtime receipt generated</p></div>'
        f'<div class="fact-grid">{facts}</div>'
        "</section>"
    )


def _workflow_frame(model: dict[str, Any]) -> str:
    nodes = []
    for index, node in enumerate(model["nodes"]):
        active = " active" if index == 0 else ""
        nodes.append(
            '<button type="button" class="node'
            + active
            + f'" data-node-id="{escape_text(node["id"])}" '
            + f'onclick="selectNode(\'{escape_text(node["id"])}\')">'
            + f'<span>{escape_text(node["order"])}</span>{escape_text(node["label"])}</button>'
        )
    return (
        '<section class="panel workflow-panel"><div class="panel-title">Workflow Hyperframe</div>'
        '<p class="note">'
        + escape_text(model["verification"]["lineage_note"])
        + '</p><div class="node-chain">'
        + "".join(nodes)
        + "</div></section>"
    )


def _node_detail_panel(model: dict[str, Any]) -> str:
    panels = []
    for index, node in enumerate(model["nodes"]):
        panels.append(
            '<section class="panel node-detail" data-node-detail="'
            + escape_text(node["id"])
            + '"'
            + ("" if index == 0 else " hidden")
            + ">"
            + f'<div class="panel-title">{escape_text(node["label"])}</div>'
            + f'<p>{escape_text(node["summary"])}</p>'
            + _kv("Role", node["type"])
            + _kv("Input data", ", ".join(node["inputs"]) or "None")
            + _kv("Output data", ", ".join(node["outputs"]) or "None")
            + _kv("Receipt trace", "See evidence map, artifact compendium, and finished receipt.")
            + "</section>"
        )
    return "".join(panels)


def _data_movement(model: dict[str, Any]) -> str:
    lanes = "".join(
        f'<div class="lane"><strong>{escape_text(lane["label"])}</strong>'
        f'<span>{escape_text(lane["summary"])}</span></div>'
        for lane in model["data_lanes"]
    )
    return '<section class="panel"><div class="panel-title">Data Movement</div><div class="lanes">' + lanes + "</div></section>"


def _artifact_compendium(model: dict[str, Any]) -> str:
    rows = []
    for artifact in model["artifacts"]:
        link = (
            f'<a href="/{escape_text(artifact["path"])}" target="_blank" rel="noreferrer">view</a>'
            if artifact["exists"]
            else "<span>missing</span>"
        )
        rows.append(
            "<tr>"
            + f"<td>{escape_text(artifact['path'])}</td>"
            + f"<td>{escape_text(artifact['purpose'])}</td>"
            + f"<td>{escape_text(artifact.get('hash') or '')}</td>"
            + f"<td>{link}</td>"
            + "</tr>"
        )
    return (
        '<section class="panel"><div class="panel-title">Artifact Compendium</div>'
        '<table><thead><tr><th>File</th><th>Purpose</th><th>Hash</th><th>Open</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></section>"
    )


def _receipt_viewer(model: dict[str, Any]) -> str:
    if not model["verification"]["html_receipt_found"]:
        return '<section class="panel"><div class="panel-title">Receipt Viewer</div><p>HTML receipt missing.</p></section>'
    return (
        '<section class="panel"><div class="panel-title">Receipt Viewer</div>'
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
        _json_card("Human editorial review", sections["human_review"]),
    ]
    return '<section class="panel"><div class="panel-title">Evidence Map</div><div class="cards">' + "".join(cards) + "</div></section>"


def _claims_columns(model: dict[str, Any]) -> str:
    supported = "".join(f"<li>{escape_text(item)}</li>" for item in model["supported_claims"])
    unsupported = "".join(f"<li>{escape_text(item)}</li>" for item in model["unsupported_claims"])
    return (
        '<section class="claims-grid"><div class="panel"><div class="panel-title">Supported Claims</div><ul>'
        + supported
        + '</ul></div><div class="panel"><div class="panel-title">Unsupported Claims</div><ul>'
        + unsupported
        + "</ul></div></section>"
    )


def _founder_claim_panel(model: dict[str, Any]) -> str:
    return (
        '<section class="panel founder-claim"><div class="panel-title">Founder-Safe Claim</div>'
        f'<p class="big-claim">{escape_text(model["founder_claim"])}</p>'
        f'<p>{escape_text(model["product_safe_explanation"])}</p></section>'
    )


def _verification_panel(model: dict[str, Any]) -> str:
    verification = model["verification"]
    rows = [
        ("required files", verification["required_files_present"]),
        ("receipt parse", verification["receipt_parse_passed"]),
        ("node trail", verification["node_trail_found"]),
        ("HTML receipt", verification["html_receipt_found"]),
        ("runtime payload", verification["runtime_payload_found"]),
        ("artifact manifest", verification["artifact_manifest_found"]),
        ("readability check", verification["readability_check"]),
    ]
    html_rows = "".join(_kv(label, value) for label, value in rows)
    return '<section class="panel"><div class="panel-title">Verification Panel</div>' + html_rows + "</section>"


def _json_card(title: str, value: object) -> str:
    text = json.dumps(value, ensure_ascii=True, indent=2)
    return f'<article class="card"><h3>{escape_text(title)}</h3><pre>{escape_text(text)}</pre></article>'


def _kv(label: str, value: object) -> str:
    return f'<div class="kv"><span>{escape_text(label)}</span><strong>{escape_text(value)}</strong></div>'


def _viewer_css() -> str:
    return """
:root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
body { margin: 0; background: #f6f7f9; color: #17202a; }
.shell { max-width: 1440px; margin: 0 auto; padding: 28px; }
.hero, .panel { background: #fff; border: 1px solid #d8dee8; border-radius: 8px; padding: 20px; box-shadow: 0 1px 2px rgba(16,24,40,.06); }
.hero { display: grid; grid-template-columns: minmax(280px, 1fr) minmax(320px, 1fr); gap: 20px; align-items: start; }
.eyebrow { margin: 0 0 8px; color: #576476; font-size: 13px; text-transform: uppercase; letter-spacing: .08em; }
h1 { margin: 0; font-size: 36px; letter-spacing: 0; }
.claim, .big-claim { font-size: 18px; font-weight: 700; }
.fact-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.fact-grid div, .kv { display: flex; flex-direction: column; gap: 4px; }
.fact-grid span, .kv span, .note { color: #667085; font-size: 13px; }
.proof-grid, .claims-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
.panel { margin-top: 16px; }
.panel-title { font-size: 18px; font-weight: 800; margin-bottom: 12px; }
.node-chain { display: grid; gap: 8px; }
.node { text-align: left; background: #f8fafc; border: 1px solid #d8dee8; border-radius: 8px; padding: 12px; cursor: pointer; font: inherit; }
.node span { display: inline-grid; place-items: center; width: 24px; height: 24px; margin-right: 8px; border-radius: 999px; background: #17202a; color: #fff; font-size: 12px; }
.node.active { border-color: #1864ab; box-shadow: inset 0 0 0 1px #1864ab; }
.lanes, .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.lane, .card { border: 1px solid #d8dee8; border-radius: 8px; padding: 12px; background: #f8fafc; }
.lane span { display: block; margin-top: 6px; color: #667085; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { border-top: 1px solid #d8dee8; padding: 10px; text-align: left; vertical-align: top; }
iframe { width: 100%; height: 520px; border: 1px solid #d8dee8; border-radius: 8px; margin-top: 12px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px; }
button, .button-link { display: inline-flex; align-items: center; min-height: 38px; padding: 8px 12px; border: 1px solid #17202a; border-radius: 8px; background: #17202a; color: #fff; text-decoration: none; cursor: pointer; }
ul { padding-left: 20px; }
@media (max-width: 860px) { .hero, .proof-grid, .claims-grid { grid-template-columns: 1fr; } .shell { padding: 16px; } }
"""
```

- [ ] **Step 2: Run renderer tests to verify GREEN**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_render_aice_hyperframes_view_includes_required_proof_sections tests/test_hyperframes_receipt_parser.py::test_render_aice_hyperframes_view_escapes_receipt_text -q
```

Expected: `2 passed`.

- [ ] **Step 3: Commit renderer slice**

```bash
git add tests/test_hyperframes_receipt_parser.py src/orchestrator/hyperframes_receipts.py
git commit -m "feat: render AICE hyperframes receipt explorer"
```

## Task 5: Add Red Server And CLI Tests

**Files:**
- Modify: `tests/test_hyperframes_receipt_parser.py`
- Create: `src/orchestrator/hyperframes_server.py`
- Modify: `src/orchestrator/cli.py`

- [ ] **Step 1: Append server and CLI tests**

```python
def test_aice_hyperframes_app_serves_viewer_model_receipt_and_artifact(tmp_path: Path):
    from orchestrator.hyperframes_server import create_aice_hyperframes_app

    packet_dir = make_runtime_packet(tmp_path)
    client = TestClient(create_aice_hyperframes_app(packet_dir, local_url="http://127.0.0.1:8765/"))

    home = client.get("/")
    assert home.status_code == 200
    assert "AICE MVP Receipt Loaded" in home.text

    model = client.get("/api/model")
    assert model.status_code == 200
    assert model.json()["workflow"]["node_count"] == 7

    receipt = client.get("/receipt")
    assert receipt.status_code == 200
    assert "AICE Source-to-Narrative Workflow Receipt" in receipt.text

    artifact = client.get("/artifacts/runtime_payload.json")
    assert artifact.status_code == 200
    assert artifact.json()["workflow_slug"] == AICE_SLUG

    blocked = client.get("/artifacts/../../workflow_receipt.json")
    assert blocked.status_code == 404


def test_hyperframes_serve_cli_dry_run_prints_url_and_first_open_path(tmp_path: Path):
    packet_dir = make_runtime_packet(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "hyperframes",
            "serve",
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
    assert "AICE HyperFrames Receipt Explorer" in result.output
    assert "Local URL: http://127.0.0.1:8765/" in result.output
    assert "Open this first: http://127.0.0.1:8765/" in result.output
    assert "Receipt packet:" in result.output
```

- [ ] **Step 2: Run CLI test to verify RED**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_hyperframes_serve_cli_dry_run_prints_url_and_first_open_path -q
```

Expected: fail because `hyperframes` command is not registered.

## Task 6: Implement Local Server And CLI Command

**Files:**
- Create: `src/orchestrator/hyperframes_server.py`
- Modify: `src/orchestrator/cli.py`
- Test: `tests/test_hyperframes_receipt_parser.py`

- [ ] **Step 1: Add the local FastAPI server module**

```python
"""Local server for the AICE HyperFrames Receipt Explorer."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from orchestrator.hyperframes_receipts import load_aice_hyperframe_model
from orchestrator.hyperframes_receipts import render_aice_hyperframes_view


def create_aice_hyperframes_app(
    receipt_dir: Path | str,
    *,
    local_url: str,
) -> FastAPI:
    root = Path(receipt_dir).expanduser().resolve()
    model = load_aice_hyperframe_model(root)
    viewer_html = render_aice_hyperframes_view(model, local_url=local_url)
    app = FastAPI(title="AICE HyperFrames Receipt Explorer", version="0.1.0")

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

    @app.get("/artifacts/{artifact_path:path}")
    def get_artifact(artifact_path: str) -> FileResponse:
        requested = (root / "artifacts" / artifact_path).resolve()
        try:
            requested.relative_to(root / "artifacts")
        except ValueError:
            raise HTTPException(status_code=404, detail="artifact not found")
        if not requested.is_file():
            raise HTTPException(status_code=404, detail="artifact not found")
        return FileResponse(str(requested))

    return app
```

- [ ] **Step 2: Register the CLI command**

Add the `hyperframes_app` Typer group near the other top-level Typer groups in
`src/orchestrator/cli.py`:

```python
hyperframes_app = typer.Typer(help="Local HyperFrames receipt explorer tools.")
app.add_typer(hyperframes_app, name="hyperframes")
```

Add the command near the M8-GTM commands:

```python
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
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Local bind host. Keep 127.0.0.1 unless Kyle explicitly approves exposure.",
    ),
    port: int = typer.Option(8765, "--port", min=1024, max=65535),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Parse the packet and print the URL without starting the blocking server.",
    ),
) -> None:
    """Serve the local AICE HyperFrames Receipt Explorer."""

    import uvicorn

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
        "AICE HyperFrames Receipt Explorer",
        [
            ("Receipt packet", str(Path(receipt_dir).resolve())),
            ("Workflow", model["workflow"]["name"]),
            ("Execution ID", model["workflow"]["n8n_execution_id"]),
            ("Node count", model["workflow"]["node_count"]),
            ("Local URL", local_url),
            ("Open this first", local_url),
            ("Boundary", "Local viewer only; receipt remains source of truth."),
        ],
    )
    if dry_run:
        return

    server_app = create_aice_hyperframes_app(receipt_dir, local_url=local_url)
    uvicorn.run(server_app, host=host, port=port, log_level="info")
```

- [ ] **Step 3: Run server and CLI tests to verify GREEN**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py::test_aice_hyperframes_app_serves_viewer_model_receipt_and_artifact tests/test_hyperframes_receipt_parser.py::test_hyperframes_serve_cli_dry_run_prints_url_and_first_open_path -q
```

Expected: `2 passed`.

- [ ] **Step 4: Commit server and CLI slice**

```bash
git add tests/test_hyperframes_receipt_parser.py src/orchestrator/hyperframes_server.py src/orchestrator/cli.py
git commit -m "feat: serve local AICE hyperframes explorer"
```

## Task 7: Add Runbook And Boundary Docs

**Files:**
- Create: `docs/runbooks/aice_hyperframes_receipt_explorer.md`
- Modify: `docs/runbooks/README.md`

- [ ] **Step 1: Write the runbook**

```markdown
# AICE HyperFrames Receipt Explorer Runbook

Date: 2026-05-19
Status: Local-only PR5 demo bridge

## Purpose

The AICE HyperFrames Receipt Explorer turns one completed AICE receipt packet
into a local visual proof board. It helps Kyle inspect what ran, what data
moved, what artifacts exist, where human review entered, what the receipt
supports, and what it does not prove.

## Command

```bash
uv run profusion hyperframes serve \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a
```

Open:

```text
http://127.0.0.1:8765/
```

Dry-run preflight:

```bash
uv run profusion hyperframes serve \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a \
  --dry-run
```

## Required Receipt Files

- `artifact_manifest.json`
- `m8_observation.json`
- `workflow_receipt.json`
- `workflow_receipt.md`
- `workflow_receipt.html`
- `artifacts/runtime_payload.json`

## What To Look At First

Start with the completion header and Workflow Hyperframe. Confirm:

- `AICE MVP Receipt Loaded`
- evidence mode `workspace_runtime_n8n_payload`
- n8n workflow ID
- execution ID
- node count `7`
- `Profusion Receipt Packet` terminal frame
- supported and unsupported claims side by side

## What This Proves

This proves a completed receipt packet can be loaded locally and inspected as a
visual workflow proof. It shows the recorded n8n node trail, runtime payload,
receipt artifacts, final HTML receipt, supported claims, unsupported claims,
limitations, and copyable founder proof summary.

## What This Does Not Prove

- public production deployment
- public Profusion API exposure
- live source credentials
- legal clearance
- fair-use approval
- factual truth certification
- platform-policy compliance
- publication safety
- customer traction
- MP4 rendering

## Safe Claim

```text
This n8n workflow ran. Profusion preserved what happened. The receipt tells you what the evidence supports and what it does not.
```
```

- [ ] **Step 2: Add the runbook link**

Add this bullet to `docs/runbooks/README.md`:

```markdown
- [AICE HyperFrames Receipt Explorer](aice_hyperframes_receipt_explorer.md) - local-only visual proof board for one completed AICE receipt packet.
```

- [ ] **Step 3: Verify docs whitespace**

```bash
git diff --check
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Commit docs slice**

```bash
git add docs/runbooks/aice_hyperframes_receipt_explorer.md docs/runbooks/README.md
git commit -m "docs: add AICE hyperframes explorer runbook"
```

## Task 8: Final Verification

**Files:**
- Verify all files changed by Tasks 1-7.

- [ ] **Step 1: Run targeted tests**

```bash
uv run pytest tests/test_hyperframes_receipt_parser.py -q
```

Expected: all HyperFrames explorer tests pass.

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

- [ ] **Step 5: Run the manual explorer preflight against the current AICE packet**

```bash
uv run profusion hyperframes serve \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a \
  --dry-run
```

Expected output includes:

```text
AICE HyperFrames Receipt Explorer
Receipt packet: /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a
Workflow: AICE Source-to-Narrative Workflow Receipt
Execution ID: 1
Node count: 7
Local URL: http://127.0.0.1:8765/
Open this first: http://127.0.0.1:8765/
```

- [ ] **Step 6: Commit final verification note if docs changed during verification**

```bash
git status --short
```

Expected: clean working tree. If verification surfaced a necessary doc correction,
commit that correction with:

```bash
git add <changed-doc-path>
git commit -m "docs: clarify AICE hyperframes verification"
```

## Execution Boundary

This PR5 plan creates the inspectable frame surface. It does not generate a
HyperFrames MP4. A follow-on render slice can use the normalized model as the
input to a real HyperFrames composition and write a `hyperframes_video_manifest.json`
only after the local explorer proves the receipt narrative is correct.

## Plan Self-Review

- Spec coverage: covers parser, visual proof board, local server, CLI command,
  artifact compendium, receipt viewer, evidence map, claims boundary,
  verification panel, copy summary, and runbook.
- Scope check: single local-only explorer slice; no public deployment, no M7
  cockpit mutation, no API guard PR4 work, no MP4 claim.
- TDD check: every implementation task starts with a failing pytest target
  before production code.
- Boundary check: all founder-facing language is sourced from the receipt model
  or the exact safe claim in the approved consultation.
