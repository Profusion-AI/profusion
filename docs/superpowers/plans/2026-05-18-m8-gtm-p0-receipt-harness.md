# M8-GTM P0 Receipt Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build the P0 fixture-backed Customer Trust Triage Receipt harness that generates one reproducible, buyer-readable receipt packet from local artifacts.

**Architecture:** Add a small `orchestrator.m8_gtm` package that loads local fixtures, validates the human-review boundary, snapshots artifacts into an atomic receipt packet, builds a receipt-local M8 observation, renders JSON/Markdown/HTML receipt outputs, and exposes it through `profusion m8 demo`. The package must not call live networks, mutate SQLite, touch lifecycle state, modify the cockpit, or change the public website.

**Tech Stack:** Python 3.11, Typer, pytest, stdlib `json`, `hashlib`, `html`, `shutil`, `tempfile`, `pathlib`, existing Profusion CLI/config patterns.

---

## Approval And Scope

- Approved source spec: `docs/superpowers/specs/2026-05-18-m8-gtm-n8n-receipt-harness-design.md`.
- Integrated QC handoff: `docs/profusion_operational_readiness_qc_codex_handoff_2026-05-18.md`.
- Output command: `uv run profusion m8 demo support-triage-human-review`.
- Evidence mode: `fixture_backed_local_demo`.
- P0 output root: `data/receipts/m8-gtm/support-triage-human-review/<receipt_id>/`.
- P1 HyperFrames and P2 cockpit visibility are deferred until P0 acceptance passes.

## File Map

- Modify: `docs/superpowers/specs/2026-05-18-m8-gtm-n8n-receipt-harness-design.md` to reflect approval and handoff integration.
- Create: `examples/m8/support-triage-human-review/README.md` for fixture explanation and no-claims boundary.
- Create: `examples/m8/support-triage-human-review/workflow.json` for the static n8n-style workflow snapshot.
- Create: `examples/m8/support-triage-human-review/runs/run_001_routine_invoice/*` for the routine case artifacts.
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/*` for the sensitive case artifacts with `human_review_event.json`.
- Create: `src/orchestrator/m8_gtm/__init__.py` for public package exports.
- Create: `src/orchestrator/m8_gtm/schemas.py` for typed aliases, constants, and validation exceptions.
- Create: `src/orchestrator/m8_gtm/fixtures.py` for fixture loading and validation.
- Create: `src/orchestrator/m8_gtm/harness.py` for atomic packet generation, manifest hashing, observation building, and receipt JSON building.
- Create: `src/orchestrator/m8_gtm/renderers.py` for Markdown and HTML rendering with escaped fixture text.
- Modify: `src/orchestrator/cli.py` to add `m8 demo`.
- Create: `tests/test_m8_gtm_receipt_harness.py` for P0 coverage.
- Create: `docs/runbooks/m8_gtm_n8n_receipt_harness.md` for reproduction, real/mock boundary, no-claims, troubleshooting, and hardening steps.
- Create: `docs/milestones/M8_GTM_P0_RECEIPT_HARNESS_CLOSEOUT_2026-05-18.md` after implementation with exact verification results.
- Update: `/home/kyle/memory/2026-05-18.md` with the approval and implementation boundary.

## Task 1: Lock Approval And Handoff Boundary

**Files:**
- Modify: `docs/superpowers/specs/2026-05-18-m8-gtm-n8n-receipt-harness-design.md`
- Update: `/home/kyle/memory/2026-05-18.md`

- [x] **Step 1: Confirm the spec approval line exists**

Expected text:

```text
Status: Approved for P0 implementation by Kyle on 2026-05-18.
Scope lock: P0 receipt harness only. P1 HyperFrames and P2 cockpit visibility must not delay P0.
```

- [x] **Step 2: Confirm the P0 no-claims policy exists**

Required claims boundary:

```text
P0 does not prove live n8n execution.
P0 does not prove live Gmail, Slack, Google Sheets, HubSpot, or n8n integration.
P0 does not send customer messages.
P0 does not certify compliance.
P0 does not provide legal assurance.
P0 does not prove the billing complaint is factually true.
P0 does not make support automation a product.
```

- [x] **Step 3: Add daily memory entry**

Append:

```markdown
- Kyle approved the Profusion M8-GTM P0 spec for implementation on 2026-05-18.
  Scope lock: fixture-backed local receipt harness only; P1 HyperFrames and P2
  cockpit visibility must not delay P0.
```

## Task 2: Write Failing P0 Tests

**Files:**
- Create: `tests/test_m8_gtm_receipt_harness.py`

- [x] **Step 1: Add tests for the public behavior**

Test names to implement:

```python
def test_fixture_loader_accepts_support_triage_happy_path(): ...
def test_fixture_validator_rejects_missing_sensitive_human_review(tmp_path): ...
def test_artifact_manifest_copies_and_hashes_files(tmp_path): ...
def test_observation_builder_requires_honest_claims(tmp_path): ...
def test_receipt_json_mirrors_observation(tmp_path): ...
def test_markdown_and_html_receipts_contain_required_sections_and_escape_text(tmp_path): ...
def test_cli_produces_complete_packet(tmp_path): ...
def test_cli_rejects_unknown_workflow_slug(tmp_path): ...
```

- [x] **Step 2: Run the new test file and verify red**

Run:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py -q
```

Expected before implementation:

```text
ModuleNotFoundError: No module named 'orchestrator.m8_gtm'
```

## Task 3: Create Local Fixture Packet

**Files:**
- Create: `examples/m8/support-triage-human-review/README.md`
- Create: `examples/m8/support-triage-human-review/workflow.json`
- Create: `examples/m8/support-triage-human-review/runs/run_001_routine_invoice/run.json`
- Create: `examples/m8/support-triage-human-review/runs/run_001_routine_invoice/inbound_message.md`
- Create: `examples/m8/support-triage-human-review/runs/run_001_routine_invoice/ai_classification.json`
- Create: `examples/m8/support-triage-human-review/runs/run_001_routine_invoice/ai_draft_reply.md`
- Create: `examples/m8/support-triage-human-review/runs/run_001_routine_invoice/final_reply.md`
- Create: `examples/m8/support-triage-human-review/runs/run_001_routine_invoice/execution_log.json`
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/run.json`
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/inbound_message.md`
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/ai_classification.json`
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/ai_draft_reply.md`
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/human_review_event.json`
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/final_reply.md`
- Create: `examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/execution_log.json`

- [x] **Step 1: Create fixture content with these case IDs**

Required case IDs:

```text
routine_invoice
sensitive_billing_complaint
```

Required sensitive review decision:

```json
{
  "case_id": "sensitive_billing_complaint",
  "reviewer": "Kyle",
  "decision": "edited",
  "reviewed_artifact_ids": ["sensitive_billing_complaint.ai_draft_reply"],
  "resulting_artifact_id": "sensitive_billing_complaint.final_reply"
}
```

- [x] **Step 2: Run tests and keep expected failures implementation-related**

Run:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py -q
```

Expected: imports may still fail or fixture loader APIs may be missing. Fixture syntax must not produce JSON parse errors.

## Task 4: Implement Fixture Loader And Validator

**Files:**
- Create: `src/orchestrator/m8_gtm/__init__.py`
- Create: `src/orchestrator/m8_gtm/schemas.py`
- Create: `src/orchestrator/m8_gtm/fixtures.py`

- [x] **Step 1: Define constants and exceptions**

Public names:

```python
WORKFLOW_SLUG = "support-triage-human-review"
WORKFLOW_NAME = "Customer Trust Triage Receipt"
EVIDENCE_MODE = "fixture_backed_local_demo"
class M8GTMError(ValueError): ...
class UnknownWorkflowError(M8GTMError): ...
class FixtureValidationError(M8GTMError): ...
```

- [x] **Step 2: Implement fixture APIs**

Public functions:

```python
def default_fixture_root() -> Path: ...
def load_workflow_fixture(workflow_slug: str, fixture_root: Path | None = None) -> dict[str, Any]: ...
def validate_workflow_fixture(fixture: dict[str, Any]) -> None: ...
```

Required validation error:

```text
sensitive_billing_complaint requires a human_review_event.json artifact
```

- [x] **Step 3: Run the loader tests**

Run:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py::test_fixture_loader_accepts_support_triage_happy_path tests/test_m8_gtm_receipt_harness.py::test_fixture_validator_rejects_missing_sensitive_human_review -q
```

Expected: both pass.

## Task 5: Implement Atomic Packet Generation

**Files:**
- Create: `src/orchestrator/m8_gtm/harness.py`

- [x] **Step 1: Implement manifest and copy behavior**

Public functions:

```python
def build_artifact_manifest(fixture: dict[str, Any], packet_dir: Path) -> dict[str, Any]: ...
def generate_demo_packet(workflow_slug: str, output_root: Path | None = None, fixture_root: Path | None = None) -> dict[str, Any]: ...
```

Atomic behavior:

```text
write to <receipt_id>.partial
write all required files inside the partial directory
rename <receipt_id>.partial to <receipt_id> only after all files are present
raise non-zero CLI error without a completed packet if generation fails
```

- [x] **Step 2: Implement M8 observation and receipt builders**

Public functions:

```python
def build_m8_observation(fixture: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]: ...
def build_workflow_receipt(observation: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]: ...
```

Required non-empty fields:

```text
supported_claims
unsupported_claims
limitations
```

Required unsupported claim:

```text
The receipt does not prove that the customer's billing claim was factually correct.
```

- [x] **Step 3: Run manifest, observation, and receipt tests**

Run:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py::test_artifact_manifest_copies_and_hashes_files tests/test_m8_gtm_receipt_harness.py::test_observation_builder_requires_honest_claims tests/test_m8_gtm_receipt_harness.py::test_receipt_json_mirrors_observation -q
```

Expected: all pass.

## Task 6: Implement Markdown And HTML Rendering

**Files:**
- Create: `src/orchestrator/m8_gtm/renderers.py`

- [x] **Step 1: Implement renderer APIs**

Public functions:

```python
def render_receipt_markdown(receipt: dict[str, Any]) -> str: ...
def render_receipt_html(receipt: dict[str, Any]) -> str: ...
```

Required sections:

```text
Customer Trust Triage Receipt
Workflow Boundary
What Happened
Where AI Acted
Where Human Review Entered
Artifacts Captured
Final Outcome
Supported Claims
Claims Not Supported
Limitations
Next Recommended Review
```

HTML rule:

```python
from html import escape
```

All fixture-derived strings rendered into HTML must pass through `escape`.

- [x] **Step 2: Run renderer test**

Run:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py::test_markdown_and_html_receipts_contain_required_sections_and_escape_text -q
```

Expected: pass.

## Task 7: Wire The CLI

**Files:**
- Modify: `src/orchestrator/cli.py`

- [x] **Step 1: Add the `m8` Typer group**

Expected CLI shape:

```bash
uv run profusion m8 demo support-triage-human-review
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-m8-demo
```

- [x] **Step 2: Map errors to exit code 1**

Unknown slug output must contain:

```text
Unknown M8 demo workflow
```

- [x] **Step 3: Run CLI tests**

Run:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py::test_cli_produces_complete_packet tests/test_m8_gtm_receipt_harness.py::test_cli_rejects_unknown_workflow_slug -q
```

Expected: both pass.

## Task 8: Write Runbook And Closeout Note

**Files:**
- Create: `docs/runbooks/m8_gtm_n8n_receipt_harness.md`
- Create: `docs/milestones/M8_GTM_P0_RECEIPT_HARNESS_CLOSEOUT_2026-05-18.md`

- [x] **Step 1: Runbook sections**

Required sections:

```text
Purpose
Quick Start
Generated Files
What Is Real
What Is Mocked
NO_CLAIMS
Troubleshooting
Before Live Customer-Facing Use
Deferred Work
```

- [x] **Step 2: Closeout sections**

Required sections:

```text
What Was Implemented
Verification
Output Packet
Known Limitations
Safe Next Step
Deferred To P1/P2
```

Use actual verification results after commands have run. Do not pre-fill passing claims.

## Task 9: Run P0 Acceptance Checks

**Files:**
- No new files unless generated packet output under ignored `data/receipts/`.

- [x] **Step 1: Run demo command**

Run:

```bash
uv run profusion m8 demo support-triage-human-review
```

Expected: exits 0 and prints the generated `workflow_receipt.html` path.

- [x] **Step 2: Run targeted tests**

Run:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py
```

Expected: pass.

- [x] **Step 3: Run nearby regression tests**

Run:

```bash
uv run pytest tests/test_receipts.py tests/test_measurements.py tests/test_m8_gtm_receipt_harness.py
```

Expected: pass.

- [x] **Step 4: Run baseline before closeout**

Run:

```bash
uv run pytest
uv run profusion smoke --offline
git diff --check
```

Expected: all pass before claiming P0 is complete.

## Plan Self-Review

Spec coverage: The plan maps every P0 requirement from the approved spec and QC handoff to fixtures, loader validation, atomic packet generation, receipt rendering, CLI integration, runbook, closeout, and acceptance checks.

Placeholder scan: No TBD/TODO placeholders are present. The closeout note explicitly waits for actual command output before recording verification claims.

Type consistency: Public API names in the tests and implementation tasks are consistent across fixture loading, harness generation, rendering, and CLI wiring.

Scope check: P1 HyperFrames, P2 cockpit visibility, public website changes, live n8n integration, external sends, SQLite mutation, and support automation are explicitly out of scope.
