# P0.1.2 AICE Workspace Receipt Closeout

Date: 2026-05-19

Branch: `codex/p0-1-1-aice-live-receipt`

## Verdict

PR #4 closes the core PR #3 gap: Profusion can now generate an AICE receipt
from a runtime payload produced by Kyle's n8n workspace, rather than only from
committed fixture files.

This is a workspace-backed runtime-payload proof, not a public production
integration. The local Profusion API was not exposed through a public tunnel.
The workspace execution produced the runtime payload, Codex read that execution
payload through the authorized n8n MCP, and Profusion generated the receipt from
that payload through the new runtime ingestion path.

## What Changed

- Added runtime-payload validation for `aice-source-to-narrative-receipt`.
- Added `profusion m8 generate-from-payload`.
- Added `POST /api/m8/aice/receipt` for local n8n HTTP Request integration when
  a reachable Profusion API URL exists.
- Added tests proving runtime payload values appear in the generated receipt.
- Created and executed the workspace workflow in the approved n8n project.
- Added a sanitized workspace-proof n8n workflow export under `examples/n8n/`
  to distinguish runtime-payload proof from the older local fixture demo.
- Tightened runtime payload validation for topic brief, rights review, human
  editorial review, and narrative-use fields.
- Improved receipt Markdown/HTML rendering so source cards, claims, rights
  review, and ambiguity records render as readable field/value rows instead of
  Python object strings.

## Workspace Proof

- n8n project: `AttentionIntelligence-ContentEngine`
- n8n workflow name: `AICE Source-to-Narrative Receipt - Workspace Proof`
- n8n workflow ID: `OGMdBpOOVXRMSzR6`
- n8n execution ID: `1`
- n8n execution status: `success`
- n8n execution mode: `manual`
- n8n execution started: `2026-05-19T14:03:06.908Z`
- n8n execution stopped: `2026-05-19T14:03:08.695Z`
- node count: `7`

Nodes executed:

1. Manual Trigger
2. Build Topic Brief
3. Build Source Cards
4. Extract Claim and Quote Candidates
5. Rights and Ambiguity Classification
6. Human Editorial Review Stub
7. Return Runtime Payload for Profusion

## Receipt Proof

Runtime payload input:

```text
/tmp/profusion-aice-workspace-runtime-payload-exec-1.json
```

Generated packet:

```text
/tmp/profusion-aice-workspace-proof/aice-source-to-narrative-receipt/receipt-20260519T140536Z-33a72562/
```

Generated HTML receipt:

```text
/tmp/profusion-aice-workspace-proof/aice-source-to-narrative-receipt/receipt-20260519T140536Z-33a72562/workflow_receipt.html
```

The receipt records:

- evidence mode: `workspace_runtime_n8n_payload`
- workspace workflow ID: `OGMdBpOOVXRMSzR6`
- execution ID: `1`
- node count and node trail
- runtime topic/thesis
- runtime source card
- runtime quote candidate
- runtime claim map
- rights review
- ambiguity register
- human editorial review state
- supported claims
- unsupported claims
- limitations

## Repo Demo Artifacts

The repo now intentionally carries two different n8n example files:

```text
examples/n8n/aice-source-to-narrative-receipt.workflow.json
examples/n8n/aice-source-to-narrative-workspace-proof.workflow.json
```

The first file is the local child-process fixture-backed demo. It calls
`uv run profusion m8 demo aice-source-to-narrative-receipt` and therefore loads
committed fixture files.

The second file is the sanitized workspace-runtime proof export. It does not
call `child_process`, does not assume `/home/kyle/profusion`, and returns a
runtime payload that can be passed to `profusion m8 generate-from-payload` or
the local API route.

## Supported Claims

- The n8n workspace workflow executed and returned a workspace runtime payload
  used for Profusion receipt generation.
- At least three n8n workspace nodes participated in the run; the recorded node
  count is `7`.
- The receipt was generated from runtime payload artifacts with hashes.
- Source cards, quote candidates, claim mappings, rights/ambiguity review, and
  human editorial review state were preserved in the packet.

## Claims Not Supported

- This does not prove public production deployment.
- This does not prove live external source credentials.
- This does not prove direct n8n Cloud HTTP reachability to Kyle's local
  Profusion API.
- This does not download, package, edit, republish, or monetize third-party
  audio/video.
- This does not certify factual truth, copyright clearance, fair use, platform
  compliance, legal compliance, journalistic neutrality, or publication safety.

## Remaining Limitation

The cleanest future production shape is still:

```text
n8n workspace -> HTTP Request -> reachable Profusion receipt API
```

This closeout intentionally avoided exposing Kyle's local API through a public
tunnel. The implemented API endpoint and runtime CLI now support that direct
HTTP path once a governed network route exists.

Before any tunnel, public domain, or cloud route exposes
`POST /api/m8/aice/receipt`, add at minimum:

- `PROFUSION_AICE_RECEIPT_TOKEN`
- `Authorization: Bearer <token>`
- n8n project or workflow allowlisting
- payload-size limits
- source/review-data redaction rules

## Verification

Commands run:

```bash
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-support-baseline-verify
uv run profusion m8 demo aice-source-to-narrative-receipt --output-dir /tmp/profusion-aice-p0-1
uv run pytest tests/test_m8_gtm_receipt_harness.py tests/test_m8_aice_receipt_harness.py tests/test_m8_aice_runtime_payload.py tests/test_api.py::test_post_aice_runtime_receipt_generates_packet -q
uv run pytest -q
uv run profusion smoke --offline
git diff --check
```

Results:

- support-triage demo: passed
- AICE fixture-backed demo: passed
- targeted runtime/API/harness tests: `18 passed`
- full backend tests: `211 passed`
- offline smoke: passed
- diff check: passed
