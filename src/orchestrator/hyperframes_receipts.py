"""Build local AICE Workflow Receipt Validator models from receipt packets."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

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
AICE_MINIMUM_NODE_COUNT = 7
CORE_JSON_FILES = (
    "workflow_receipt.json",
    "artifact_manifest.json",
    "m8_observation.json",
    "artifacts/runtime_payload.json",
)
DISPLAY_FILES = CORE_JSON_FILES + ("workflow_receipt.md", "workflow_receipt.html")
REQUIRED_RECEIPT_FILES = DISPLAY_FILES
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

    missing_files = [rel for rel in REQUIRED_RECEIPT_FILES if not (root / rel).is_file()]
    missing_core = [rel for rel in CORE_JSON_FILES if not (root / rel).is_file()]
    if missing_core:
        raise HyperframeReceiptError(
            "receipt packet missing required JSON files: " + ", ".join(missing_core)
        )

    receipt = _read_json(root / "workflow_receipt.json")
    manifest = _read_json(root / "artifact_manifest.json")
    observation = _read_json(root / "m8_observation.json")
    runtime_payload = _read_json(root / "artifacts" / "runtime_payload.json")

    n8n_execution = _dict_value(observation.get("n8n_execution"))
    nodes = _build_nodes(n8n_execution)
    artifacts = _build_artifacts(root, manifest)
    supported_claims = _list_value(receipt.get("claims_supported"))
    unsupported_claims = _list_value(
        receipt.get("claims_not_supported", receipt.get("unsupported_claims"))
    )
    limitations = _list_value(receipt.get("limitations"))
    validation = _build_validation(
        root=root,
        receipt=receipt,
        manifest=manifest,
        observation=observation,
        runtime_payload=runtime_payload,
        artifacts=artifacts,
        nodes=nodes,
        missing_files=missing_files,
        supported_claims=supported_claims,
        unsupported_claims=unsupported_claims,
        limitations=limitations,
    )

    workflow_slug = (
        _string_value(manifest.get("workflow_slug"))
        or _string_value(runtime_payload.get("workflow_slug"))
        or _string_value(observation.get("workflow_id"))
    )
    workflow = {
        "name": _string_value(receipt.get("workflow_name"))
        or _string_value(observation.get("workflow_name")),
        "slug": workflow_slug,
        "evidence_mode": _string_value(receipt.get("evidence_mode"))
        or _string_value(observation.get("evidence_mode"))
        or _string_value(runtime_payload.get("evidence_mode")),
        "n8n_project": _string_value(n8n_execution.get("workspace_url")),
        "n8n_workflow_id": _string_value(n8n_execution.get("workspace_workflow_id"))
        or _string_value(runtime_payload.get("n8n_workspace_workflow_id")),
        "n8n_execution_id": _string_value(n8n_execution.get("execution_id"))
        or _string_value(runtime_payload.get("n8n_execution_id")),
        "node_count": _int_value(n8n_execution.get("node_count"))
        or len(_list_value(n8n_execution.get("nodes_executed"))),
        "status": _string_value(n8n_execution.get("status")) or "unknown",
    }
    receipt_id = _string_value(receipt.get("receipt_id")) or root.name

    return {
        "receipt_id": receipt_id,
        "receipt_path": root.name,
        "receipt": {"id": receipt_id, "packet_path": root.name},
        "validator_title": VALIDATOR_TITLE,
        "validator_subtitle": VALIDATOR_SUBTITLE,
        "workflow": workflow,
        "nodes": nodes,
        "edges": _build_edges(nodes),
        "data_lanes": _build_data_lanes(),
        "artifacts": artifacts,
        "receipt_sections": _build_receipt_sections(receipt),
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "claims": {"supported": supported_claims, "unsupported": unsupported_claims},
        "limitations": limitations,
        "founder_claim": SAFE_FOUNDER_CLAIM,
        "product_safe_explanation": PRODUCT_SAFE_EXPLANATION,
        "proof_counters": _build_proof_counters(
            root=root,
            n8n_execution=n8n_execution,
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            artifacts=artifacts,
        ),
        "validation": validation,
        "verification": {
            "safe_founder_claim": SAFE_FOUNDER_CLAIM,
            "product_safe_explanation": PRODUCT_SAFE_EXPLANATION,
            "lineage_note": LINEAGE_NOTE,
            "missing_files": missing_files,
            "html_receipt_found": (root / "workflow_receipt.html").is_file(),
            "required_receipt_files": list(REQUIRED_RECEIPT_FILES),
        },
    }


def escape_text(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def render_aice_validator_view(model: dict[str, Any], *, local_url: str) -> str:
    """Render a scene-ready local HTML validator for an AICE receipt model."""

    title = escape_text(model.get("validator_title") or VALIDATOR_TITLE)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{title}</title>",
            f"  <style>{_validator_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="validator-shell" data-prof-demo="aice-validator">',
            _validation_header(model, local_url=local_url),
            _workflow_replay(model),
            _human_review_gate(model),
            _claim_boundary(model),
            _artifact_ledger(model),
            _receipt_viewer(model),
            _evidence_map(model),
            _validation_findings_panel(model),
            _founder_summary(model, local_url=local_url),
            "  </main>",
            "  <script>",
            "    function copyFounderProofSummary() {",
            '      const button = document.querySelector("[data-proof-summary]");',
            "      if (!button) return;",
            "      let payload = {};",
            "      try { payload = JSON.parse(button.dataset.proofSummary || '{}'); }",
            "      catch (error) { payload = { text: '' }; }",
            "      const text = payload.text || '';",
            "      if (navigator.clipboard && navigator.clipboard.writeText) {",
            "        navigator.clipboard.writeText(text);",
            "      } else {",
            "        const area = document.createElement('textarea');",
            "        area.value = text;",
            "        area.setAttribute('readonly', '');",
            "        document.body.appendChild(area);",
            "        area.select();",
            "        document.execCommand('copy');",
            "        document.body.removeChild(area);",
            "      }",
            "      button.textContent = 'Copied';",
            "      window.setTimeout(() => {",
            "        button.textContent = 'Copy Founder Proof Summary';",
            "      }, 1600);",
            "    }",
            "  </script>",
            "</body>",
            "</html>",
        ]
    )


def render_aice_hyperframes_view(
    model: dict[str, Any], *, local_url: str
) -> str:
    return render_aice_validator_view(model, local_url=local_url)


def _status_label(status: str) -> str:
    labels = {
        "validated_with_limitations": "Validated with limitations",
        "validated_with_warnings": "Validated with warnings",
        "validation_failed": "Validation failed",
    }
    return labels.get(status, status.replace("_", " ").title() if status else "Unknown")


def _validation_header(model: dict[str, Any], *, local_url: str) -> str:
    workflow = _dict_value(model.get("workflow"))
    counters = _dict_value(model.get("proof_counters"))
    validation = _dict_value(model.get("validation"))
    status = _status_label(_string_value(validation.get("validation_status")))
    counter_cards = "\n".join(
        [
            _counter_card("nodes executed", counters.get("nodes_executed")),
            _counter_card(
                "receipt artifacts found", counters.get("receipt_artifacts_found")
            ),
            _counter_card(
                "claim boundaries present", counters.get("claim_boundaries_present")
            ),
            _counter_card(
                "human review gate recorded",
                counters.get("human_review_gates_recorded"),
            ),
        ]
    )
    return f"""
    <section class="validator-section header-section" data-scene="validation-header">
      <div class="eyebrow">Local validator view</div>
      <div class="header-grid">
        <div>
          <h1>{escape_text(model.get("validator_title") or VALIDATOR_TITLE)}</h1>
          <p class="subtitle">{escape_text(model.get("validator_subtitle") or VALIDATOR_SUBTITLE)}</p>
          <p class="safe-claim">{escape_text(model.get("founder_claim") or SAFE_FOUNDER_CLAIM)}</p>
        </div>
        <aside class="status-panel">
          <span class="status-label">{escape_text(status)}</span>
          {_kv("Workflow", workflow.get("name"))}
          {_kv("Execution ID", workflow.get("n8n_execution_id"))}
          {_kv("Packet", model.get("receipt_path"))}
          {_kv("Viewer URL", local_url)}
        </aside>
      </div>
      <div class="counter-grid">
        {counter_cards}
      </div>
    </section>"""


def _workflow_replay(model: dict[str, Any]) -> str:
    workflow = _dict_value(model.get("workflow"))
    nodes = _list_value(model.get("nodes"))
    node_items = "\n".join(
        f"""
        <li class="node-row node-{escape_text(node.get("type"))}">
          <span class="node-order">{escape_text(node.get("order"))}</span>
          <div>
            <strong>{escape_text(node.get("label"))}</strong>
            <p>{escape_text(node.get("summary"))}</p>
          </div>
        </li>"""
        for node in nodes
        if isinstance(node, dict)
    )
    lanes = "".join(
        f'<span class="lane-pill">{escape_text(label)}</span>'
        for label in ("Execution", "Evidence", "Receipt")
    )
    return f"""
    <section class="validator-section" data-scene="workflow-replay">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Workflow replay</p>
          <h2>Execution trail</h2>
        </div>
        <div class="lane-strip">{lanes}</div>
      </div>
      <p class="section-note">{escape_text(LINEAGE_NOTE)}</p>
      <div class="workflow-meta">
        {_kv("Status", workflow.get("status"))}
        {_kv("Node count", workflow.get("node_count"))}
        {_kv("Workflow ID", workflow.get("n8n_workflow_id"))}
      </div>
      <ol class="node-list">
        {node_items}
      </ol>
    </section>"""


def _human_review_gate(model: dict[str, Any]) -> str:
    artifacts = [
        artifact
        for artifact in _list_value(model.get("artifacts"))
        if isinstance(artifact, dict)
        and artifact.get("artifact_type") == "human_editorial_review"
    ]
    rows = "\n".join(
        f"""
        <li>
          <strong>{escape_text(artifact.get("description") or "Human Editorial Review Gate")}</strong>
          <span>{escape_text(artifact.get("packet_path"))}</span>
        </li>"""
        for artifact in artifacts
    ) or "<li><strong>Human Editorial Review Gate</strong><span>missing</span></li>"
    return f"""
    <section class="validator-section" data-scene="human-review-gate">
      <p class="eyebrow">Human gate</p>
      <h2>Human Editorial Review Gate</h2>
      <p class="section-note">A recorded human review gate is required before founder-facing claims are treated as reviewable evidence.</p>
      <ul class="compact-list">{rows}</ul>
    </section>"""


def _claim_boundary(model: dict[str, Any]) -> str:
    supported = _claim_list(model.get("supported_claims"))
    unsupported = _claim_list(model.get("unsupported_claims"))
    limitations = _claim_list(model.get("limitations"))
    sections = _list_value(model.get("receipt_sections"))
    receipt_rows = "\n".join(
        _json_card(section.get("label"), section.get("value"))
        for section in sections
        if isinstance(section, dict)
    )
    return f"""
    <section class="validator-section" data-scene="claim-boundary">
      <p class="eyebrow">Claim boundary</p>
      <h2>Supported Claims</h2>
      {supported}
      <h2>Unsupported Claims</h2>
      {unsupported}
      <h2>Limitations</h2>
      {limitations}
      <div class="receipt-section-grid">
        {receipt_rows}
      </div>
    </section>"""


def _artifact_ledger(model: dict[str, Any]) -> str:
    rows = "\n".join(
        _artifact_row(artifact)
        for artifact in _list_value(model.get("artifacts"))
        if isinstance(artifact, dict)
    )
    return f"""
    <section class="validator-section" data-scene="artifact-ledger">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Evidence</p>
          <h2>Artifact Ledger</h2>
        </div>
      </div>
      <div class="artifact-table" role="table">
        <div class="artifact-head" role="row">
          <span>Artifact</span><span>Type</span><span>Path</span><span>Status</span>
        </div>
        {rows}
      </div>
    </section>"""


def _receipt_viewer(model: dict[str, Any]) -> str:
    verification = _dict_value(model.get("verification"))
    if verification.get("html_receipt_found") is True:
        action = '<a class="button-link" href="/receipt">Open finished receipt</a>'
    else:
        action = '<span class="unavailable">Open finished receipt unavailable</span>'
    return f"""
    <section class="validator-section receipt-viewer">
      <p class="eyebrow">Receipt</p>
      <h2>Receipt Viewer</h2>
      <p class="section-note">The finished receipt is served from the local packet route when the packet contains rendered HTML.</p>
      {action}
    </section>"""


def _evidence_map(model: dict[str, Any]) -> str:
    lanes = _list_value(model.get("data_lanes"))
    lane_items = "\n".join(
        f"<li>{escape_text(lane.get('label'))}</li>"
        for lane in lanes
        if isinstance(lane, dict)
    )
    return f"""
    <section class="validator-section evidence-map">
      <p class="eyebrow">Evidence map</p>
      <h2>Recorded Data Lanes</h2>
      <ul class="lane-list">{lane_items}</ul>
    </section>"""


def _validation_findings_panel(model: dict[str, Any]) -> str:
    validation = _dict_value(model.get("validation"))
    findings = _list_value(validation.get("validation_findings"))
    rows = "\n".join(
        f"""
        <li class="finding finding-{escape_text(finding.get("severity"))}">
          <span>{escape_text(finding.get("severity"))}</span>
          <strong>{escape_text(finding.get("code"))}</strong>
          <p>{escape_text(finding.get("message"))}</p>
        </li>"""
        for finding in findings
        if isinstance(finding, dict)
    )
    return f"""
    <section class="validator-section validation-findings">
      <p class="eyebrow">Validator checks</p>
      <h2>Validation Findings</h2>
      <ul class="finding-list">{rows}</ul>
    </section>"""


def _founder_summary(model: dict[str, Any], *, local_url: str) -> str:
    workflow = _dict_value(model.get("workflow"))
    validation = _dict_value(model.get("validation"))
    counters = _dict_value(model.get("proof_counters"))
    supported = [str(item) for item in _list_value(model.get("supported_claims"))]
    unsupported = [str(item) for item in _list_value(model.get("unsupported_claims"))]
    limitations = [str(item) for item in _list_value(model.get("limitations"))]
    proof_lines = [
        f"Validation status: {_status_label(_string_value(validation.get('validation_status')))}",
        f"Workflow name: {workflow.get('name') or ''}",
        f"Execution ID: {workflow.get('n8n_execution_id') or ''}",
        f"Node count: {counters.get('nodes_executed') or workflow.get('node_count') or 0}",
        f"Receipt packet: {model.get('receipt_path') or ''}",
        f"Safe claim: {model.get('founder_claim') or SAFE_FOUNDER_CLAIM}",
        f"Supported boundary: {'; '.join(supported)}",
        f"Unsupported boundary: {'; '.join(unsupported)}",
        f"Limitations: {'; '.join(limitations)}",
        f"Local viewer URL: {local_url}",
    ]
    proof_text = "\n".join(proof_lines)
    proof_payload = {"text": proof_text}
    proof_json = escape_text(json.dumps(proof_payload, ensure_ascii=True))
    preview = "<br>".join(escape_text(line) for line in proof_lines)
    return f"""
    <section class="validator-section founder-summary" data-scene="founder-summary">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Founder packet</p>
          <h2>Founder Proof Summary</h2>
        </div>
        <button type="button" class="copy-button" data-proof-summary="{proof_json}" onclick="copyFounderProofSummary()">Copy Founder Proof Summary</button>
      </div>
      <p class="proof-preview">{preview}</p>
    </section>"""


def _json_card(title: Any, value: Any) -> str:
    if isinstance(value, (dict, list)):
        rendered = json.dumps(value, ensure_ascii=True, indent=2)
        content = f"<pre>{escape_text(rendered)}</pre>"
    else:
        content = f"<p>{escape_text(value)}</p>"
    return f"""
    <article class="json-card">
      <h3>{escape_text(title)}</h3>
      {content}
    </article>"""


def _kv(label: str, value: Any) -> str:
    return (
        '<div class="kv">'
        f"<span>{escape_text(label)}</span>"
        f"<strong>{escape_text(value)}</strong>"
        "</div>"
    )


def _counter_card(label: str, value: Any) -> str:
    count = _int_value(value) if isinstance(value, int) else 0
    return f"""
    <article class="counter-card">
      <strong>{escape_text(count)} {escape_text(label)}</strong>
    </article>"""


def _claim_list(value: Any) -> str:
    items = _list_value(value)
    if not items:
        return '<p class="unavailable">None recorded</p>'
    return "<ul class=\"compact-list\">" + "\n".join(
        f"<li>{escape_text(item)}</li>" for item in items
    ) + "</ul>"


def _artifact_row(artifact: dict[str, Any]) -> str:
    href = _string_value(artifact.get("href"))
    exists = artifact.get("exists") is True
    packet_path = artifact.get("packet_path")
    if exists and _safe_artifact_href(href):
        path_cell = (
            f'<a href="{escape_text(href)}">{escape_text(packet_path)}</a>'
        )
        status = "available"
    elif exists:
        path_cell = escape_text(packet_path)
        status = "unavailable"
    else:
        path_cell = escape_text(packet_path)
        status = "missing"
    return f"""
    <div class="artifact-row" role="row">
      <span>{escape_text(artifact.get("description") or artifact.get("artifact_id"))}</span>
      <span>{escape_text(artifact.get("artifact_type"))}</span>
      <span>{path_cell}</span>
      <span class="artifact-status">{escape_text(status)}</span>
    </div>"""


def _safe_artifact_href(href: str) -> bool:
    return href.startswith("/packet/") and not href.startswith("//")


def _validator_css() -> str:
    return """
    :root {
      color-scheme: light;
      --bg: #f7f8f5;
      --ink: #20231f;
      --muted: #5f665d;
      --line: #d9ddd2;
      --panel: #ffffff;
      --accent: #2d6a4f;
      --warn: #8a5a00;
      --fail: #9d2f2f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }
    .validator-shell {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }
    .validator-section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 14px 0;
      padding: 20px;
      box-shadow: 0 1px 2px rgba(32, 35, 31, 0.05);
    }
    .header-grid,
    .section-heading,
    .workflow-meta,
    .counter-grid {
      display: grid;
      gap: 14px;
    }
    .header-grid {
      grid-template-columns: minmax(0, 1fr) minmax(280px, 360px);
      align-items: start;
    }
    .section-heading {
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
    }
    .workflow-meta,
    .counter-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-top: 16px;
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 { font-size: 30px; line-height: 1.1; margin-bottom: 8px; }
    h2 { font-size: 18px; margin-bottom: 10px; }
    h3 { font-size: 14px; margin-bottom: 8px; }
    .subtitle,
    .safe-claim,
    .section-note,
    .proof-preview,
    .json-card p,
    .node-row p {
      color: var(--muted);
    }
    .eyebrow {
      margin-bottom: 6px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0;
      text-transform: uppercase;
    }
    .status-panel,
    .counter-card,
    .json-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #fbfcfa;
    }
    .status-label {
      display: inline-block;
      margin-bottom: 12px;
      color: #0f5132;
      font-weight: 800;
    }
    .kv {
      display: grid;
      grid-template-columns: 112px minmax(0, 1fr);
      gap: 8px;
      padding: 7px 0;
      border-top: 1px solid var(--line);
    }
    .kv span,
    .artifact-head,
    .artifact-status,
    .lane-pill {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }
    .kv strong,
    .artifact-row span,
    .proof-preview {
      overflow-wrap: anywhere;
    }
    .counter-card strong {
      display: block;
      font-size: 26px;
      line-height: 1;
    }
    .node-list,
    .compact-list,
    .finding-list,
    .lane-list {
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .node-row,
    .compact-list li,
    .finding {
      display: grid;
      gap: 10px;
      padding: 12px 0;
      border-top: 1px solid var(--line);
    }
    .node-row {
      grid-template-columns: 42px minmax(0, 1fr);
    }
    .node-order {
      display: grid;
      place-items: center;
      width: 30px;
      height: 30px;
      border: 1px solid var(--line);
      border-radius: 50%;
      font-weight: 800;
    }
    .lane-strip,
    .lane-list,
    .receipt-section-grid {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .lane-pill {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      background: #eef4ef;
    }
    .receipt-section-grid {
      margin-top: 16px;
    }
    .json-card {
      flex: 1 1 260px;
    }
    pre {
      margin: 0;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 12px;
    }
    .artifact-table {
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    .artifact-head,
    .artifact-row {
      display: grid;
      grid-template-columns: minmax(180px, 1.4fr) minmax(130px, 0.8fr) minmax(220px, 1.1fr) 96px;
      gap: 10px;
      padding: 10px 12px;
    }
    .artifact-head { background: #eef1ea; }
    .artifact-row + .artifact-row { border-top: 1px solid var(--line); }
    a,
    .button-link,
    .copy-button {
      color: #174c37;
      font-weight: 800;
    }
    .button-link,
    .copy-button {
      display: inline-flex;
      align-items: center;
      min-height: 36px;
      border: 1px solid #7aa28f;
      border-radius: 6px;
      padding: 8px 12px;
      background: #eef8f1;
      text-decoration: none;
      cursor: pointer;
    }
    .finding {
      grid-template-columns: 68px 220px minmax(0, 1fr);
      align-items: start;
    }
    .finding-pass span { color: var(--accent); }
    .finding-warn span { color: var(--warn); }
    .finding-fail span { color: var(--fail); }
    .unavailable { color: var(--muted); font-weight: 700; }
    @media (max-width: 820px) {
      .header-grid,
      .section-heading,
      .workflow-meta,
      .counter-grid,
      .artifact-head,
      .artifact-row,
      .finding {
        grid-template-columns: 1fr;
      }
      .validator-shell {
        width: min(100% - 20px, 1180px);
        padding-top: 16px;
      }
    }
    """


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HyperframeReceiptError(f"invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise HyperframeReceiptError(f"JSON file must contain an object: {path.name}")
    return payload


def _build_nodes(n8n_execution: dict[str, Any]) -> list[dict[str, Any]]:
    labels = [str(label) for label in _list_value(n8n_execution.get("nodes_executed"))]
    nodes = [
        {
            "id": _slugify(label),
            "label": label,
            "type": _node_type(label),
            "order": index + 1,
            "summary": f"Recorded n8n node: {label}",
            "inputs": [],
            "outputs": [],
            "derived": False,
        }
        for index, label in enumerate(labels)
    ]
    nodes.append(
        {
            "id": "profusion-receipt-packet",
            "label": "Profusion Receipt Packet",
            "type": "receipt_packet",
            "order": len(nodes) + 1,
            "summary": "Derived terminal node for the generated receipt packet.",
            "inputs": ["runtime_payload", "artifact_manifest"],
            "outputs": ["workflow_receipt"],
            "derived": True,
        }
    )
    return nodes


def _build_edges(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{nodes[index]['id']}--{nodes[index + 1]['id']}",
            "source": nodes[index]["id"],
            "target": nodes[index + 1]["id"],
        }
        for index in range(len(nodes) - 1)
    ]


def _build_artifacts(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _list_value(manifest.get("artifacts"))
    artifacts: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        packet_path = _string_value(row.get("packet_path"))
        resolved = _safe_resolve(root, packet_path) if packet_path else None
        safe_path = _is_safe_relative_packet_path(root, packet_path, resolved)
        exists = bool(safe_path and resolved and resolved.is_file())
        seen_paths.add(packet_path)
        artifacts.append(
            {
                "artifact_id": _string_value(row.get("artifact_id")),
                "artifact_type": _string_value(row.get("artifact_type")),
                "description": _string_value(row.get("description")),
                "packet_path": packet_path,
                "sha256": _string_value(row.get("sha256")) or None,
                "exists": exists,
                "href": _packet_href(packet_path) if safe_path else None,
                "manifest_listed": True,
            }
        )

    for rel in REQUIRED_RECEIPT_FILES:
        if rel in seen_paths:
            continue
        path = root / rel
        artifacts.append(
            {
                "artifact_id": f"receipt.{rel.replace('/', '.')}",
                "artifact_type": "receipt_packet_file",
                "description": f"Required receipt packet file: {rel}",
                "packet_path": rel,
                "sha256": _sha256(path) if path.is_file() else None,
                "exists": path.is_file(),
                "href": _packet_href(rel),
                "manifest_listed": False,
            }
        )
    return artifacts


def _build_validation(
    *,
    root: Path,
    receipt: dict[str, Any],
    manifest: dict[str, Any],
    observation: dict[str, Any],
    runtime_payload: dict[str, Any],
    artifacts: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    missing_files: list[str],
    supported_claims: list[Any],
    unsupported_claims: list[Any],
    limitations: list[Any],
) -> dict[str, Any]:
    n8n_execution = _dict_value(observation.get("n8n_execution"))
    recorded_nodes = _list_value(n8n_execution.get("nodes_executed"))
    node_count = _int_value(n8n_execution.get("node_count")) or 0
    manifest_paths_safe = _manifest_paths_are_safe(root, manifest)
    hash_status, hash_message = _check_manifest_hashes(root, manifest)
    forbidden_found = _forbidden_overclaim_language_found(receipt, observation)
    workflow_slug_matches = _workflow_slugs_match(manifest, runtime_payload, observation)

    checks: dict[str, Any] = {
        "core_files_present": all((root / rel).is_file() for rel in CORE_JSON_FILES),
        "display_files_present": all((root / rel).is_file() for rel in DISPLAY_FILES),
        "runtime_payload_found": (root / "artifacts" / "runtime_payload.json").is_file(),
        "workflow_slug_matches": workflow_slug_matches,
        "n8n_execution_id_present": bool(
            _string_value(n8n_execution.get("execution_id"))
            or _string_value(runtime_payload.get("n8n_execution_id"))
        ),
        "node_count_matches_trail": bool(node_count and node_count == len(recorded_nodes)),
        "minimum_node_count_met": len(recorded_nodes) >= AICE_MINIMUM_NODE_COUNT,
        "human_review_artifact_present": any(
            artifact["artifact_type"] == "human_editorial_review" and artifact["exists"]
            for artifact in artifacts
        ),
        "supported_claims_present": bool(supported_claims),
        "unsupported_claims_present": bool(unsupported_claims),
        "limitations_present": bool(limitations),
        "path_safety_passed": manifest_paths_safe,
        "forbidden_overclaim_language_found": forbidden_found,
        "artifact_hashes_checked": hash_status,
    }

    findings: list[dict[str, str]] = []
    _add_bool_finding(
        findings,
        "core_files_present",
        checks["core_files_present"],
        "Core receipt JSON files are present.",
        "Core receipt JSON files are missing.",
    )
    _add_bool_finding(
        findings,
        "display_files_present",
        checks["display_files_present"],
        "Display receipt files are present.",
        "Display receipt files are missing: " + ", ".join(missing_files),
        false_severity="warn",
    )
    _add_bool_finding(
        findings,
        "runtime_payload_found",
        checks["runtime_payload_found"],
        "Runtime payload artifact is present.",
        "Runtime payload artifact is missing.",
    )
    _add_bool_finding(
        findings,
        "workflow_slug_matches",
        checks["workflow_slug_matches"],
        "Workflow slug matches manifest, runtime payload, and observation.",
        "Workflow slug does not match manifest, runtime payload, and observation.",
    )
    _add_bool_finding(
        findings,
        "n8n_execution_id_present",
        checks["n8n_execution_id_present"],
        "n8n execution ID is present.",
        "n8n execution ID is missing.",
    )
    _add_bool_finding(
        findings,
        "node_count_matches_trail",
        checks["node_count_matches_trail"],
        "Recorded node count matches the execution trail.",
        "Recorded node count does not match the execution trail.",
    )
    _add_bool_finding(
        findings,
        "minimum_node_count_met",
        checks["minimum_node_count_met"],
        f"Minimum AICE workflow node count of {AICE_MINIMUM_NODE_COUNT} is met.",
        f"Minimum AICE workflow node count of {AICE_MINIMUM_NODE_COUNT} is not met.",
    )
    _add_bool_finding(
        findings,
        "human_review_artifact_present",
        checks["human_review_artifact_present"],
        "Human review artifact is present.",
        "Human review artifact is missing.",
    )
    _add_bool_finding(
        findings,
        "supported_claims_present",
        checks["supported_claims_present"],
        "Supported claims are present.",
        "Supported claims are missing.",
    )
    _add_bool_finding(
        findings,
        "unsupported_claims_present",
        checks["unsupported_claims_present"],
        "Unsupported claims are present.",
        "Unsupported claims are missing.",
    )
    _add_bool_finding(
        findings,
        "limitations_present",
        checks["limitations_present"],
        "Limitations are present.",
        "Limitations are missing.",
    )
    _add_bool_finding(
        findings,
        "path_safety_passed",
        checks["path_safety_passed"],
        "Manifest paths resolve inside the receipt packet.",
        "Manifest contains a path outside the receipt packet.",
    )
    findings.append(
        {
            "severity": "fail" if forbidden_found else "pass",
            "code": "forbidden_overclaim_language",
            "message": (
                "Forbidden founder-facing overclaim language was found."
                if forbidden_found
                else "Forbidden founder-facing overclaim language was not found."
            ),
        }
    )
    findings.append(
        {
            "severity": "fail" if hash_status is False else "pass",
            "code": "artifact_hashes_checked",
            "message": hash_message or "Manifest-listed artifact hashes match.",
        }
    )

    fail_present = any(finding["severity"] == "fail" for finding in findings)
    warn_present = any(finding["severity"] == "warn" for finding in findings)
    status = (
        "validation_failed"
        if fail_present
        else "validated_with_warnings"
        if warn_present
        else "validated_with_limitations"
    )
    validation = {
        "validation_status": status,
        "validation_findings": findings,
        "artifact_hash_limitation": hash_message if hash_status == "partial" else "",
        "node_labels_observed": [node["label"] for node in nodes],
    }
    validation.update(checks)
    return validation


def _add_bool_finding(
    findings: list[dict[str, str]],
    code: str,
    passed: bool,
    pass_message: str,
    false_message: str,
    *,
    false_severity: str = "fail",
) -> None:
    findings.append(
        {
            "severity": "pass" if passed else false_severity,
            "code": code,
            "message": pass_message if passed else false_message,
        }
    )


def _check_manifest_hashes(root: Path, manifest: dict[str, Any]) -> tuple[bool | str, str]:
    checked = 0
    for row in _list_value(manifest.get("artifacts")):
        if not isinstance(row, dict):
            continue
        packet_path = _string_value(row.get("packet_path"))
        expected_hash = _string_value(row.get("sha256"))
        if not packet_path or not expected_hash:
            continue
        path = _safe_resolve(root, packet_path)
        if path is None or not _is_relative_to(path, root):
            return False, f"Manifest artifact path is unsafe: {packet_path}"
        if not path.is_file():
            return False, f"Manifest artifact is missing: {packet_path}"
        checked += 1
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            return False, f"Manifest hash mismatch for {packet_path}"
    if checked == 0:
        return "partial", "Only manifest-listed hashes were available for validation."
    return True, ""


def _manifest_paths_are_safe(root: Path, manifest: dict[str, Any]) -> bool:
    for row in _list_value(manifest.get("artifacts")):
        if not isinstance(row, dict):
            continue
        packet_path = _string_value(row.get("packet_path"))
        if not packet_path:
            continue
        path = _safe_resolve(root, packet_path)
        if path is None or not _is_relative_to(path, root):
            return False
    return True


def _workflow_slugs_match(
    manifest: dict[str, Any],
    runtime_payload: dict[str, Any],
    observation: dict[str, Any],
) -> bool:
    slugs = (
        _string_value(manifest.get("workflow_slug")),
        _string_value(runtime_payload.get("workflow_slug")),
        _string_value(observation.get("workflow_id")),
    )
    return all(slugs) and len(set(slugs)) == 1


def _forbidden_overclaim_language_found(
    receipt: dict[str, Any],
    observation: dict[str, Any],
) -> bool:
    fields_to_scan = [
        receipt.get("workflow_purpose"),
        receipt.get("evidence_boundary"),
        receipt.get("topic_episode_thesis"),
        receipt.get("what_happened"),
        receipt.get("where_ai_acted"),
        receipt.get("where_n8n_acted"),
        receipt.get("where_human_review_entered"),
        receipt.get("final_action"),
        receipt.get("narrative_decisions"),
        receipt.get("source_cards"),
        receipt.get("claims_and_quote_candidates"),
        receipt.get("quote_candidates"),
        receipt.get("rights_use_ambiguity_classification"),
        receipt.get("ambiguities_preserved"),
        receipt.get("attention_intelligence_mapping"),
        receipt.get("generated_synthetic_media_plan"),
        receipt.get("artifacts_reviewed"),
        receipt.get("next_recommended_review"),
        receipt.get("claims_supported"),
        observation.get("supported_claims"),
        observation.get("topic_brief"),
        observation.get("source_cards"),
        observation.get("claim_map"),
        observation.get("quote_candidates"),
        observation.get("rights_review"),
        observation.get("ambiguity_register"),
        observation.get("attention_intelligence_map"),
        observation.get("narrative_brief"),
        observation.get("visual_plan"),
        observation.get("artifacts_captured"),
        observation.get("ai_actions_observed"),
        observation.get("outcome"),
        observation.get("trigger_summary"),
        observation.get("workflow_boundary"),
    ]
    text = "\n".join(_flatten_text(value) for value in fields_to_scan).lower()
    return any(term in text for term in FORBIDDEN_FOUNDER_TERMS)


def _build_receipt_sections(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    section_keys = (
        "workflow_purpose",
        "what_happened",
        "where_n8n_acted",
        "where_ai_acted",
        "where_human_review_entered",
        "final_action",
        "narrative_decisions",
        "next_recommended_review",
    )
    return [
        {"key": key, "label": key.replace("_", " ").title(), "value": receipt[key]}
        for key in section_keys
        if receipt.get(key)
    ]


def _build_data_lanes() -> list[dict[str, str]]:
    lane_names = (
        "topic/thesis",
        "source card",
        "quote candidate",
        "claim map",
        "rights review",
        "ambiguity register",
        "human review state",
        "runtime payload",
        "receipt packet",
    )
    return [{"id": _slugify(name), "label": name} for name in lane_names]


def _build_proof_counters(
    *,
    root: Path,
    n8n_execution: dict[str, Any],
    supported_claims: list[Any],
    unsupported_claims: list[Any],
    artifacts: list[dict[str, Any]],
) -> dict[str, int]:
    human_review_gates = sum(
        1
        for artifact in artifacts
        if artifact["artifact_type"] == "human_editorial_review" and artifact["exists"]
    )
    return {
        "nodes_executed": len(_list_value(n8n_execution.get("nodes_executed"))),
        "receipt_artifacts_found": sum(
            1 for rel in REQUIRED_RECEIPT_FILES if (root / rel).is_file()
        ),
        "claim_boundaries_present": int(bool(supported_claims))
        + int(bool(unsupported_claims)),
        "human_review_gates_recorded": human_review_gates,
    }


def _node_type(label: str) -> str:
    lowered = label.lower()
    if "human" in lowered or "review" in lowered:
        return "human_review"
    if "receipt" in lowered:
        return "receipt"
    if "trigger" in lowered:
        return "trigger"
    return "n8n_node"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_resolve(root: Path, packet_path: str) -> Path | None:
    if not packet_path:
        return None
    candidate = Path(packet_path)
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _is_safe_relative_packet_path(
    root: Path,
    packet_path: str,
    resolved: Path | None,
) -> bool:
    return bool(
        packet_path
        and not Path(packet_path).is_absolute()
        and resolved
        and _is_relative_to(resolved, root)
    )


def _packet_href(packet_path: str) -> str:
    return "/packet/" + quote(packet_path, safe="/")


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _int_value(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(_flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(_flatten_text(item) for item in value)
    if value is None:
        return ""
    return str(value)
