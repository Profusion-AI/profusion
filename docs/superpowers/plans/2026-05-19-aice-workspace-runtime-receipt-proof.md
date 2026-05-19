# AICE Workspace Runtime Receipt Proof Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that an AICE workflow exists and executes in Kyle's n8n workspace, passes runtime payload data into Profusion, and generates a receipt packet from that runtime payload.

**Architecture:** Add a runtime-payload receipt path beside the existing fixture-backed demo path. Keep PR #3's fixture demo intact, but make PR #4's proof flow `n8n workspace workflow -> HTTP request or CLI payload handoff -> Profusion runtime receipt generator -> receipt packet with n8n workflow/execution evidence`.

**Tech Stack:** Python 3.11, Typer, FastAPI, pytest, n8n MCP Workflow SDK, n8n Manual Trigger/Webhook, Set, Code, HTTP Request, Respond to Webhook nodes.

---

## Current Verified State

- Local branch: `codex/p0-1-1-aice-live-receipt`, clean before this plan was written.
- PR #3: open, mergeable, CI green, titled `feat: add AICE live receipt workflow`.
- PR #3 proof mode: local n8n CLI plus fixture-backed Profusion receipt generation.
- Current weak point: `examples/n8n/aice-source-to-narrative-receipt.workflow.json` calls `uv run profusion m8 demo aice-source-to-narrative-receipt`, so Profusion loads committed fixture files instead of the data that moved through n8n.
- Read-only n8n MCP check on 2026-05-19 found accessible projects but no workflows matching `AICE`, `Profusion`, or `Source-to-Narrative`.
- Remote n8n create/update/execute is an external workspace mutation. Get Kyle's approval on target project before doing it.

## Execution Update

- Kyle approved target n8n project: `AttentionIntelligence-ContentEngine`.
- Kyle instructed PR4 should not branch; execution stayed on `codex/p0-1-1-aice-live-receipt`.

## File Structure

- Modify `src/orchestrator/m8_gtm/harness.py`: add runtime-payload packet generation while preserving `generate_demo_packet`.
- Create `src/orchestrator/m8_gtm/runtime_payloads.py`: validate and normalize AICE runtime payloads from n8n.
- Modify `src/orchestrator/cli.py`: add `profusion m8 generate-from-payload`.
- Modify `src/orchestrator/api.py`: add `POST /api/m8/aice/receipt` for n8n HTTP Request calls.
- Create `tests/test_m8_aice_runtime_payload.py`: runtime payload unit and CLI tests.
- Modify `tests/test_api.py`: API endpoint tests.
- Modify `tests/test_m8_aice_receipt_harness.py`: rename the PR #3 evidence mode expectation if the honesty patch is still desired.
- Optional after MCP creation: export workspace workflow JSON to `examples/n8n/aice-source-to-narrative-workspace-proof.workflow.json`, with no secrets and no private workspace URLs.
- Create private closeout evidence under `data/private/events/svb-ai-native-startup-2026-05-21/` or another ignored private path. Do not commit private n8n URLs, project IDs, execution IDs, or workspace metadata to the public repo unless Kyle explicitly approves.

## Task 1: Add Red Tests For Runtime Payload Receipts

**Files:**
- Create: `tests/test_m8_aice_runtime_payload.py`

- [ ] **Step 1: Write the failing runtime packet test**

```python
from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.m8_gtm.harness import generate_packet_from_runtime_payload

AICE_SLUG = "aice-source-to-narrative-receipt"


def sample_runtime_payload() -> dict:
    return {
        "workflow_slug": AICE_SLUG,
        "n8n_workspace_workflow_id": "wf_runtime_aice_20260519",
        "n8n_execution_id": "exec_runtime_aice_20260519",
        "n8n_execution_url": "https://n8n.example.invalid/workflow/wf_runtime_aice_20260519/executions/exec_runtime_aice_20260519",
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
            "working_thesis": "Runtime payload evidence should be visible in the generated receipt.",
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
            "reviewed_artifacts": ["topic_brief", "source_cards", "claim_map", "ambiguity_register"],
            "approval_summary": "Runtime payload is acceptable for internal proof only.",
            "reviewed_at": "2026-05-19T16:05:00Z",
        },
        "narrative_brief": {
            "allowed_use": "internal_demo_only",
            "brief": ["Show that runtime data, not committed fixtures, appears in the receipt."],
        },
        "visual_plan": {
            "allowed_use": "planning_only",
            "generated_media_state": "not_generated",
            "notes": ["No third-party audio/video is downloaded."],
        },
        "limitations": [
            "No third-party media downloaded.",
            "Receipt does not certify factual truth, copyright clearance, fair use, platform compliance, journalistic neutrality, or publication safety.",
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
    assert observation["n8n_execution"]["workspace_workflow_id"] == "wf_runtime_aice_20260519"
    assert observation["n8n_execution"]["execution_id"] == "exec_runtime_aice_20260519"
    assert observation["n8n_execution"]["node_count"] == 7
    assert len(observation["n8n_execution"]["nodes_executed"]) >= 3
    assert any(row["artifact_type"] == "runtime_payload" for row in manifest["artifacts"])


def test_generate_packet_from_runtime_payload_rejects_media_download_claim(tmp_path: Path):
    payload = sample_runtime_payload()
    payload["quote_candidates"][0]["audio_visual_downloaded"] = True

    try:
        generate_packet_from_runtime_payload(AICE_SLUG, payload, output_root=tmp_path)
    except ValueError as exc:
        assert "must not download audio/video" in str(exc)
    else:
        raise AssertionError("runtime payload with downloaded media should fail")
```

- [ ] **Step 2: Run the red test**

```bash
uv run pytest tests/test_m8_aice_runtime_payload.py::test_generate_packet_from_runtime_payload_uses_runtime_values -q
```

Expected: fail because `generate_packet_from_runtime_payload` does not exist.

## Task 2: Implement Runtime Payload Validation

**Files:**
- Create: `src/orchestrator/m8_gtm/runtime_payloads.py`
- Test: `tests/test_m8_aice_runtime_payload.py`

- [ ] **Step 1: Add the validator module**

```python
"""Validate n8n runtime payloads for AICE receipt generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from orchestrator.m8_gtm.registry import AICE_SLUG
from orchestrator.m8_gtm.schemas import FixtureValidationError

WORKSPACE_RUNTIME_EVIDENCE_MODE = "workspace_runtime_n8n_payload"


def validate_aice_runtime_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    if normalized.get("workflow_slug") != AICE_SLUG:
        raise FixtureValidationError(f"runtime payload workflow_slug must be {AICE_SLUG!r}")

    required = (
        "n8n_workspace_workflow_id",
        "n8n_execution_id",
        "executed_at",
        "node_count",
        "nodes_executed",
        "topic_brief",
        "source_cards",
        "quote_candidates",
        "claim_map",
        "rights_review",
        "ambiguity_register",
        "human_editorial_review",
        "narrative_brief",
        "visual_plan",
    )
    missing = [key for key in required if key not in normalized]
    if missing:
        raise FixtureValidationError(f"runtime payload missing required fields: {', '.join(missing)}")

    if int(normalized["node_count"]) < 3:
        raise FixtureValidationError("runtime payload requires node_count >= 3")
    if not isinstance(normalized["nodes_executed"], list) or len(normalized["nodes_executed"]) < 3:
        raise FixtureValidationError("runtime payload requires at least 3 executed nodes")

    quotes = normalized["quote_candidates"]
    if not isinstance(quotes, list) or not quotes:
        raise FixtureValidationError("runtime payload requires at least one quote candidate")
    for candidate in quotes:
        if candidate.get("audio_visual_downloaded") is not False:
            raise FixtureValidationError("runtime payload media candidates must not download audio/video")
        if candidate.get("storage_mode") != "metadata_only":
            raise FixtureValidationError("runtime payload media candidates must use metadata_only storage")
        if "local_media_path" in candidate or "transcript_full_text" in candidate:
            raise FixtureValidationError("runtime payload media candidates must remain reference-only")

    if not normalized.get("limitations"):
        normalized["limitations"] = [
            "No third-party media downloaded.",
            "Receipt does not certify factual truth, copyright clearance, fair use, platform compliance, journalistic neutrality, or publication safety.",
        ]
    normalized["evidence_mode"] = WORKSPACE_RUNTIME_EVIDENCE_MODE
    return normalized
```

- [ ] **Step 2: Run validator tests**

```bash
uv run pytest tests/test_m8_aice_runtime_payload.py -q
```

Expected: still fail until Task 3 adds packet generation.

## Task 3: Generate Packets From Runtime Payloads

**Files:**
- Modify: `src/orchestrator/m8_gtm/harness.py`
- Test: `tests/test_m8_aice_runtime_payload.py`

- [ ] **Step 1: Add runtime fixture and manifest helpers**

Add helpers that convert the normalized payload into the same in-memory shape used by `_build_aice_observation`, but write runtime artifacts directly into the packet instead of copying committed fixture files.

```python
def generate_packet_from_runtime_payload(
    workflow_slug: str,
    payload: dict[str, Any],
    output_root: Path | None = None,
) -> dict[str, Any]:
    """Generate a receipt packet from n8n runtime payload data."""
    if workflow_slug != AICE_SLUG:
        raise M8GTMError("runtime payload generation is currently supported only for AICE")

    from orchestrator.m8_gtm.runtime_payloads import validate_aice_runtime_payload

    normalized = validate_aice_runtime_payload(payload)
    fixture = _aice_runtime_payload_to_fixture(normalized)

    if output_root is None:
        from orchestrator import config

        output_root = config.RECEIPTS_DIR / "m8-gtm"

    receipt_id = f"receipt-{_now_iso().replace(':', '').replace('-', '')}-{uuid4().hex[:8]}"
    slug_root = output_root / workflow_slug
    final_dir = slug_root / receipt_id
    partial_dir = slug_root / f"{receipt_id}.partial"
    if partial_dir.exists() or final_dir.exists():
        raise M8GTMError(f"Receipt packet already exists: {final_dir}")

    try:
        manifest = _build_runtime_artifact_manifest(fixture, normalized, partial_dir)
        manifest["packet_dir"] = str(final_dir)
        _write_json(partial_dir / "artifact_manifest.json", manifest)
        observation = build_m8_observation(fixture, manifest)
        receipt = build_workflow_receipt(observation, manifest)
        receipt["receipt_id"] = receipt_id
        _write_json(partial_dir / "m8_observation.json", observation)
        _write_json(partial_dir / "workflow_receipt.json", receipt)
        (partial_dir / "workflow_receipt.md").write_text(render_receipt_markdown(receipt), encoding="utf-8")
        (partial_dir / "workflow_receipt.html").write_text(render_receipt_html(receipt), encoding="utf-8")
        _assert_required_packet_files(partial_dir)
        partial_dir.rename(final_dir)
    except Exception:
        if partial_dir.exists():
            shutil.rmtree(partial_dir)
        raise

    return {
        "receipt_id": receipt_id,
        "packet_dir": final_dir,
        "workflow_receipt_html": final_dir / "workflow_receipt.html",
        "manifest": manifest,
        "observation": observation,
        "receipt": receipt,
    }
```

- [ ] **Step 2: Ensure n8n metadata lands in observation**

In `_build_aice_observation`, include these fields under `n8n_execution` when present in `n8n_run_summary`:

```python
"workspace_workflow_id": n8n_run.get("workspace_workflow_id"),
"workspace_url": n8n_run.get("workspace_url"),
"execution_url": n8n_run.get("execution_url"),
```

- [ ] **Step 3: Run runtime tests**

```bash
uv run pytest tests/test_m8_aice_runtime_payload.py -q
```

Expected: pass.

## Task 4: Add CLI Runtime Payload Command

**Files:**
- Modify: `src/orchestrator/cli.py`
- Test: `tests/test_m8_aice_runtime_payload.py`

- [ ] **Step 1: Add CLI test**

```python
def test_m8_generate_from_payload_cli_writes_runtime_receipt(tmp_path: Path):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(sample_runtime_payload()), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "m8",
            "generate-from-payload",
            "aice-source-to-narrative-receipt",
            "--input",
            str(payload_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["workflow_slug"] == "aice-source-to-narrative-receipt"
    assert payload["n8n_execution_id"] == "exec_runtime_aice_20260519"
    assert Path(payload["workflow_receipt_html"]).exists()
```

- [ ] **Step 2: Implement the command**

```python
@m8_app.command("generate-from-payload")
def m8_generate_from_payload(
    workflow_slug: str = typer.Argument(..., help="M8 workflow slug."),
    input_path: Path = typer.Option(..., "--input", help="Runtime n8n payload JSON."),
    output_dir: Path | None = typer.Option(None, "--output-dir", help="Receipt output root."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Generate an M8-GTM receipt packet from runtime n8n payload data."""
    from orchestrator.m8_gtm.harness import generate_packet_from_runtime_payload

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        result = generate_packet_from_runtime_payload(workflow_slug, payload, output_root=output_dir)
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    response = {
        "workflow_slug": workflow_slug,
        "receipt_id": result["receipt_id"],
        "packet_dir": str(result["packet_dir"]),
        "workflow_receipt_html": str(result["workflow_receipt_html"]),
        "n8n_workspace_workflow_id": result["observation"]["n8n_execution"].get("workspace_workflow_id"),
        "n8n_execution_id": result["observation"]["n8n_execution"]["execution_id"],
        "node_count": result["observation"]["n8n_execution"]["node_count"],
    }
    if json_output:
        _emit_json(response)
        return
    _print_key_values("AICE Runtime Receipt Packet", list(response.items()))
```

- [ ] **Step 3: Run CLI tests**

```bash
uv run pytest tests/test_m8_aice_runtime_payload.py -q
```

Expected: pass.

## Task 5: Add Local API Endpoint For n8n HTTP Request

**Files:**
- Modify: `src/orchestrator/api.py`
- Modify: `tests/test_api.py`

- [ ] **Step 1: Add API test**

```python
def test_post_aice_runtime_receipt_generates_packet(monkeypatch, tmp_path):
    import orchestrator.config as config
    from orchestrator.api import create_app
    from tests.test_m8_aice_runtime_payload import sample_runtime_payload

    monkeypatch.setattr(config, "RECEIPTS_DIR", tmp_path)
    tc = TestClient(create_app(dev=True))

    resp = tc.post("/api/m8/aice/receipt", json=sample_runtime_payload())

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["workflow_slug"] == "aice-source-to-narrative-receipt"
    assert payload["n8n_execution_id"] == "exec_runtime_aice_20260519"
    assert payload["node_count"] == 7
    assert Path(payload["workflow_receipt_html"]).exists()
```

- [ ] **Step 2: Implement API route**

```python
    @app.post("/api/m8/aice/receipt")
    def post_aice_runtime_receipt(payload: dict[str, Any]) -> dict[str, Any]:
        from orchestrator.m8_gtm.harness import generate_packet_from_runtime_payload
        from orchestrator.m8_gtm.registry import AICE_SLUG

        try:
            result = generate_packet_from_runtime_payload(AICE_SLUG, payload)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        n8n_execution = result["observation"]["n8n_execution"]
        return {
            "workflow_slug": AICE_SLUG,
            "receipt_id": result["receipt_id"],
            "packet_dir": str(result["packet_dir"]),
            "workflow_receipt_html": str(result["workflow_receipt_html"]),
            "n8n_workspace_workflow_id": n8n_execution.get("workspace_workflow_id"),
            "n8n_execution_id": n8n_execution["execution_id"],
            "node_count": n8n_execution["node_count"],
            "nodes_executed": n8n_execution["nodes_executed"],
            "limitations": result["receipt"]["limitations"],
            "claims_supported": result["receipt"]["claims_supported"],
            "claims_not_supported": result["receipt"]["claims_not_supported"],
        }
```

- [ ] **Step 3: Run API tests**

```bash
uv run pytest tests/test_api.py tests/test_m8_aice_runtime_payload.py -q
```

Expected: pass.

## Task 6: Create Or Update The n8n Workspace Workflow

**Files:**
- Optional Create: `examples/n8n/aice-source-to-narrative-workspace-proof.workflow.json`
- Private evidence: `data/private/events/svb-ai-native-startup-2026-05-21/pr4_workspace_receipt_closeout.md`

- [ ] **Step 1: Confirm target project before mutation**

Run read-only MCP checks:

```text
mcp__n8n_mcp__.search_projects(limit=100)
mcp__n8n_mcp__.search_workflows(query="AICE", limit=50)
```

Expected: record target project choice in private closeout before creating or updating anything. If project choice is ambiguous, ask Kyle.

- [ ] **Step 2: Build workflow SDK code**

Use SDK imports:

```javascript
import { workflow, node, trigger, expr, placeholder } from '@n8n/workflow-sdk';
```

Required workflow name:

```text
AICE Source-to-Narrative Receipt - Workspace Proof
```

Required node chain:

```text
Manual Trigger
  -> Build Topic Brief
  -> Build Source Cards
  -> Extract Claim and Quote Candidates
  -> Rights and Ambiguity Classification
  -> Human Editorial Review Stub
  -> Generate Profusion Receipt via HTTP Request
  -> Return Receipt Summary
```

The HTTP Request node must call a configurable Profusion URL. Use a placeholder value, not a committed private URL:

```javascript
url: placeholder('PROFUSION_RECEIPT_API_URL, for example http://127.0.0.1:8000/api/m8/aice/receipt')
```

- [ ] **Step 3: Validate workflow code before create/update**

```text
mcp__n8n_mcp__.validate_workflow(code=<full SDK workflow code>)
```

Expected: valid workflow JSON returned.

- [ ] **Step 4: Create or update through n8n MCP**

Use `create_workflow_from_code` if no AICE workspace workflow exists. Use `update_workflow` if an AICE workspace workflow already exists.

Expected evidence to record privately:

```text
n8n workspace workflow name:
n8n workspace workflow ID:
n8n workspace project:
n8n workspace URL:
created_or_updated_at:
```

- [ ] **Step 5: Execute only after local API is running**

Start local Profusion API:

```bash
uv run profusion serve --dev
```

Execute through n8n MCP:

```text
mcp__n8n_mcp__.get_workflow_details(workflowId=<workflow_id>)
mcp__n8n_mcp__.execute_workflow(workflowId=<workflow_id>, executionMode="manual")
mcp__n8n_mcp__.get_execution(workflowId=<workflow_id>, executionId=<execution_id>, includeData=true, truncateData=1)
```

Expected: successful execution with at least 3 nodes executed and a Profusion receipt summary returned by the final node.

## Task 7: Closeout, Docs, And Verification

**Files:**
- Create: `docs/milestones/P0_1_2_AICE_WORKSPACE_RECEIPT_CLOSEOUT_2026-05-19.md`
- Create or update private evidence file under `data/private/events/svb-ai-native-startup-2026-05-21/`

- [ ] **Step 1: Run local baseline checks**

```bash
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-support-baseline-verify
uv run profusion m8 demo aice-source-to-narrative-receipt --output-dir /tmp/profusion-aice-p0-1
uv run pytest tests/test_m8_gtm_receipt_harness.py -q
uv run pytest tests/test_m8_aice_receipt_harness.py -q
uv run pytest tests/test_m8_aice_runtime_payload.py -q
uv run pytest -q
uv run profusion smoke --offline
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Write closeout note**

The closeout note must include:

```text
PR #4 verdict:
n8n workspace workflow name:
n8n workspace workflow ID:
n8n execution ID:
n8n execution timestamp:
nodes executed:
receipt packet path:
receipt HTML path:
commands run:
tests passed:
supported claims:
unsupported claims:
limitations:
remaining gaps:
```

Use a private ignored note for private workspace URLs and full execution URLs unless Kyle explicitly approves putting those values in the public repo.

- [ ] **Step 3: Final acceptance gate**

Do not mark PR #4 complete unless all are true:

```text
Workspace workflow exists.
Workspace workflow executed.
Runtime payload data appears in the receipt.
Receipt records workflow ID, execution ID, node count, and nodes executed.
Support-triage baseline still passes.
AICE fixture-backed demo still passes.
Full backend tests pass.
No third-party audio/video downloaded.
No publication, public website, legal, fair-use, compliance, platform-policy, truth-certification, or publication-safety claim was made.
```

## Self-Review

- Spec coverage: The plan covers runtime payload ingestion, CLI, API, n8n MCP workflow creation/update, execution evidence, support-triage preservation, AICE fixture preservation, no media download, and no-claims boundaries.
- Placeholder scan: The only intentional placeholder is the n8n HTTP Request URL placeholder, which prevents committing private local or workspace URLs.
- Type consistency: The same `n8n_workspace_workflow_id`, `n8n_execution_id`, `node_count`, `nodes_executed`, and `workflow_receipt_html` names are used across tests, CLI, API, and closeout.
