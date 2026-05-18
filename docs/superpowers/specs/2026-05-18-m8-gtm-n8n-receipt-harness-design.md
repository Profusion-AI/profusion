# M8-GTM n8n Receipt Harness Design and TDD Spec

Date: 2026-05-18

Status: Approved for P0 implementation by Kyle on 2026-05-18.
Scope lock: P0 receipt harness only. P1 HyperFrames and P2 cockpit visibility
must not delay P0.

Integrated handoff:
`docs/profusion_operational_readiness_qc_codex_handoff_2026-05-18.md`
has been acknowledged as the controlling QC handoff for implementation. Its
operating rule is binding here: receipt-real first, HyperFrames-rendered
second, cockpit-visible later.

## Executive Decision

M8-GTM Overlay is approved as the scoped M8 prototype path.

M8 keeps its repo-defined technical meaning: manual/file-first workflow outcome
observations. The GTM overlay gives M8 its first commercially useful proving
ground: an n8n-style support triage workflow wrapped by a Profusion receipt
harness.

The release hierarchy is:

```text
P0: CLI + durable artifacts + generated receipt
P1: HyperFrames-rendered demo video from receipt outputs
P2: optional read-only cockpit visibility
```

Working rule:

```text
Receipt-real first. HyperFrames-rendered second. Cockpit-visible later.
```

## Repo Truth

Current Profusion state:

- M7 is locked as the internal operator cockpit in `apps/operator-cockpit/`.
- M7.5 has file-first reviewer evidence packets under `src/orchestrator/receipts/`.
- M8 is active as manual/file-first workflow outcome observations under
  `src/orchestrator/measurements.py` and `data/measurements/`.
- The public website in `dashboard/` is out of scope.
- The education/content engine and Substack work live in
  `/home/kyle/attention-media-lab`, not Profusion.

This prototype must preserve those boundaries.

## Problem

AI-assisted workflows can produce customer-facing work faster than teams can
review and defend it. For a support triage workflow, the buyer-readable
questions are:

- What workflow ran?
- Where did AI act?
- Why did the workflow pause?
- What did a human review?
- What final action occurred?
- What artifacts were captured?
- What claims does the evidence support?
- What claims are not proven?

The prototype should answer those questions without requiring live Gmail,
Slack, HubSpot, Google Sheets, n8n credentials, or cockpit UI work.

## First Demo

External demo name:

```text
Customer Trust Triage Receipt
```

Internal workflow slug:

```text
support-triage-human-review
```

Product sentence:

```text
The demo is not "AI answers support tickets."
The demo is "Profusion shows when AI work was safe to approve."
```

The demo uses two cases:

- Routine invoice request: "Hi, can you resend my invoice for April?"
- Sensitive billing complaint: "I was charged twice, support ignored me, and
  I am considering filing a complaint."

The routine case proves Profusion does not slow every workflow. The sensitive
case is the hero moment: AI drafts, the workflow hits a review boundary, a
human edits or approves, and Profusion generates the receipt.

## Source Check

The selected n8n public workflow is directionally fit because it captures
incoming support messages from email or Slack, classifies category/sensitivity,
drafts AI replies, pauses sensitive cases for human review, allows approve,
edit, or reject, sends a final reply, and logs interactions.

HyperFrames is approved for P1 because its public README describes an
HTML-native, agent-friendly local preview and render loop. The rendering docs
distinguish local mode from Docker mode: local mode is faster for iteration but
may vary across platforms; Docker mode is preferred when reproducible output is
needed.

Local tool check on 2026-05-18:

```text
node --version -> v22.22.0
ffmpeg -version -> 8.0.1
npx hyperframes --version -> 0.6.22
docker server version -> 29.4.3
```

Sources:

- n8n workflow template:
  `https://n8n.io/workflows/15120-route-support-messages-with-gpt-41-mini-slack-email-and-human-review/`
- HyperFrames GitHub:
  `https://github.com/heygen-com/hyperframes`
- HyperFrames rendering guide:
  `https://hyperframes.mintlify.app/guides/rendering`
- HyperFrames quickstart:
  `https://hyperframes.mintlify.app/quickstart`

## Approaches Considered

### A. Fixture-first receipt harness, then HyperFrames

Build a local fixture-backed harness around the support triage workflow. It
loads workflow/run JSON, copies durable artifacts into a receipt packet,
generates `m8_observation.json`, `workflow_receipt.json`,
`workflow_receipt.md`, and `workflow_receipt.html`, then optionally creates a
HyperFrames video from those outputs.

Tradeoff: It is not a live n8n integration. Benefit: it proves the evidence
loop quickly and honestly.

Recommendation: choose this.

### B. Live n8n API integration first

Connect to local n8n, import the template, execute real nodes, and read
execution history.

Tradeoff: This is more impressive technically, but it introduces credentials,
node setup, webhook state, API shape, and network failures before the receipt
contract is proven.

Recommendation: defer.

### C. Cockpit-first receipt preview

Make the M7 cockpit display the new receipt before the CLI artifact loop is
complete.

Tradeoff: It improves visibility but risks UI state work, routing, static
snapshot updates, and cockpit mutation confusion.

Recommendation: defer to P2 only if P0 and P1 are already clean.

## P0 Scope

P0 ships a reproducible CLI demo that consumes local fixtures and writes a
durable receipt packet.

Required command:

```bash
uv run profusion m8 demo support-triage-human-review
```

Required successful output:

```text
Loaded workflow fixture: support-triage-human-review
Loaded run artifacts: routine_invoice, sensitive_billing_complaint
Validated artifact manifest
Generated M8 observation
Generated workflow receipt JSON
Generated workflow receipt Markdown
Generated workflow receipt HTML
Receipt: data/receipts/m8-gtm/support-triage-human-review/<receipt_id>/workflow_receipt.html
```

Required P0 artifacts:

```text
artifact_manifest.json
m8_observation.json
workflow_receipt.json
workflow_receipt.md
workflow_receipt.html
```

Required P0 runbook:

```text
docs/runbooks/m8_gtm_n8n_receipt_harness.md
```

The runbook must state what is real, what is mocked, how to reproduce the demo,
and what must be hardened before any live customer-facing use.

P0 evidence mode:

```text
fixture_backed_local_demo
```

P0 must make this evidence mode explicit in `workflow_receipt.json` either as
`evidence_mode` or, if contract expansion would be risky, in
`evidence_boundary` and `limitations`.

P0 no-claims policy:

```text
P0 does not prove live n8n execution.
P0 does not prove live Gmail, Slack, Google Sheets, HubSpot, or n8n integration.
P0 does not send customer messages.
P0 does not certify compliance.
P0 does not provide legal assurance.
P0 does not prove the billing complaint is factually true.
P0 does not make support automation a product.
```

## P1 Scope

P1 starts only after the P0 receipt gate passes.

P1 generates a short HyperFrames demo video from P0 receipt outputs. The video
explains the receipt. It does not create new product evidence.

Required P1 artifacts:

```text
demo_storyboard.md
hyperframes_video_manifest.json
customer_trust_triage_receipt.mp4
```

Claim drift rule:

```text
Every text claim shown in the HyperFrames video must be sourced from
workflow_receipt.json, workflow_receipt.md, m8_observation.json, or
demo_storyboard.md generated from those files.
```

Rendering rule:

```text
Local HyperFrames render is acceptable for iteration.
Final shareable render should prefer Docker mode when available.
If Docker mode is unavailable or fails, record that limitation in
hyperframes_video_manifest.json.
Do not claim cross-machine deterministic rendering unless Docker mode was used.
```

## P2 Scope

Cockpit visibility is optional and must stay read-only.

Allowed:

- show generated receipt summary
- show artifact list
- show observation status
- show supported and unsupported claims

Not allowed:

- approval buttons
- mutation logic
- scheduling or publishing controls
- new workflow state machine
- public website changes
- cockpit work taking more than 90 minutes before P0/P1 are clean

## Non-Goals

This sprint does not build:

- a live n8n integration platform
- an n8n consultancy offer
- support automation as a product
- live Gmail, Slack, OpenAI, Anthropic, or Google Sheets credentials
- automated customer sends
- AI observability
- compliance certification
- legal assurance
- public website copy
- MoneyPrinterTurbo replacement work
- generalized video marketing pipeline
- HyperFrames as a Profusion product dependency

## Proposed File Layout

Input fixtures:

```text
examples/m8/support-triage-human-review/
  workflow.json
  README.md
  runs/
    run_001_routine_invoice/
      run.json
      inbound_message.md
      ai_classification.json
      ai_draft_reply.md
      final_reply.md
      execution_log.json
    run_002_sensitive_billing_complaint/
      run.json
      inbound_message.md
      ai_classification.json
      ai_draft_reply.md
      human_review_event.json
      final_reply.md
      execution_log.json
```

Generated packet:

```text
data/receipts/m8-gtm/support-triage-human-review/<receipt_id>/
  artifact_manifest.json
  m8_observation.json
  workflow_receipt.json
  workflow_receipt.md
  workflow_receipt.html
  artifacts/
    workflow.json
    run_001_routine_invoice/
      ...
    run_002_sensitive_billing_complaint/
      ...
```

Implementation units:

```text
src/orchestrator/m8_gtm/__init__.py
src/orchestrator/m8_gtm/fixtures.py
src/orchestrator/m8_gtm/harness.py
src/orchestrator/m8_gtm/schemas.py
src/orchestrator/m8_gtm/renderers.py
```

Tests:

```text
tests/test_m8_gtm_receipt_harness.py
```

CLI integration:

```text
src/orchestrator/cli.py
```

## Data Contracts

### ArtifactManifest

`artifact_manifest.json` records the fixture snapshot used to generate the
receipt.

Required fields:

```yaml
manifest_id: string
workflow_slug: support-triage-human-review
generated_at: ISO-8601 UTC timestamp
source_fixture_path: string
packet_dir: string
artifacts:
  - artifact_id: string
    case_id: routine_invoice | sensitive_billing_complaint | workflow
    artifact_type: workflow_json | run_log | inbound_message | ai_classification | ai_draft | human_review | final_reply | execution_log
    source_path: string
    packet_path: string
    sha256: string
    description: string
    redaction_state: none | redacted | metadata_only
limitations:
  - string
```

### M8Observation

`m8_observation.json` is the file-first M8 outcome observation for the demo
run. It is receipt-local in P0. It does not mutate SQLite and does not require a
content item lifecycle transition.

Required fields:

```yaml
observation_id: string
workflow_id: support-triage-human-review
workflow_name: Customer Trust Triage Receipt
source_system: n8n
run_id: string
case_ids:
  - routine_invoice
  - sensitive_billing_complaint
observed_at: ISO-8601 UTC timestamp
workflow_boundary: string
trigger_summary: string
ai_actions_observed:
  - case_id: string
    action: classify_message | draft_reply
    input_artifact_id: string
    output_artifact_id: string
    risk_signal: string
tool_actions_observed:
  - case_id: string
    action: route | send_final_reply | log_interaction
    artifact_id: string
human_review_events:
  - case_id: sensitive_billing_complaint
    reviewer: string
    decision: approved | edited | rejected | escalated
    reviewed_artifact_ids:
      - string
    resulting_artifact_id: string
artifacts_captured:
  - artifact_id: string
outcome:
  routine_invoice: string
  sensitive_billing_complaint: string
failure_or_retry_state:
  status: none | failed | retried | blocked
  details: string
supported_claims:
  - string
unsupported_claims:
  - string
limitations:
  - string
next_recommended_review: string
```

### WorkflowReceipt

`workflow_receipt.json` is the buyer-readable machine payload used to generate
Markdown and HTML.

Required fields:

```yaml
receipt_id: string
source_observation_id: string
source_manifest_id: string
workflow_name: Customer Trust Triage Receipt
workflow_purpose: string
evidence_boundary: string
what_happened:
  - string
where_ai_acted:
  - string
where_human_review_entered:
  - string
artifacts_reviewed:
  - artifact_id: string
    label: string
    packet_path: string
final_action:
  routine_invoice: string
  sensitive_billing_complaint: string
QA_or_review_status: string
claims_supported:
  - string
claims_not_supported:
  - string
limitations:
  - string
next_recommended_review: string
generated_at: ISO-8601 UTC timestamp
```

### HyperFramesVideoManifest

`hyperframes_video_manifest.json` is P1-only.

Required fields:

```yaml
video_id: string
source_receipt_id: string
source_observation_id: string
source_artifacts:
  - string
composition_path: string
render_command: string
render_mode: local | docker
hyperframes_version: string
node_version: string
ffmpeg_version: string
docker_version: string | null
output_path: string
generated_at: ISO-8601 UTC timestamp
limitations:
  - string
```

## P0 Data Flow

1. CLI receives `support-triage-human-review`.
2. Fixture loader resolves `examples/m8/support-triage-human-review/`.
3. Fixture validator checks required workflow and run artifacts.
4. Artifact copier snapshots source files into the packet directory.
5. Manifest builder computes stable SHA-256 hashes and writes
   `artifact_manifest.json`.
6. Harness builder extracts observed AI actions, tool actions, human review
   events, outcomes, failures, supported claims, unsupported claims, and
   limitations.
7. Observation writer writes `m8_observation.json`.
8. Receipt builder writes `workflow_receipt.json`.
9. Markdown renderer writes `workflow_receipt.md`.
10. HTML renderer writes `workflow_receipt.html`.
11. CLI prints paths and exits 0.

No live network calls are allowed in P0.

## Error Handling

The CLI exits non-zero and writes no completed packet when:

- workflow slug is unknown
- required fixture file is missing
- a JSON fixture is invalid
- a sensitive case lacks a human review event
- supported claims are empty
- unsupported claims are empty
- limitations are empty
- artifact copy or hashing fails

Partial writes should use a temporary packet directory and rename only after all
required artifacts are written. If implementation time is tight, an incomplete
packet may be left on disk only when it is clearly named with a `.partial`
suffix and the CLI explains the failure.

## Receipt Content Requirements

`workflow_receipt.md` and `workflow_receipt.html` must include these sections:

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

Minimum claim language:

Supported:

```text
Human review occurred before the sensitive billing complaint final response was marked ready to send.
```

Not supported:

```text
The receipt does not prove that the customer's billing claim was factually correct.
```

Required limitation:

```text
The fixture simulates an n8n-style run with local artifacts; it does not prove live Gmail, Slack, Google Sheets, or n8n API execution.
```

## P1 HyperFrames Requirements

P1 begins only after the P0 receipt gate passes.

Video length:

```text
60-90 seconds
```

Format:

```text
16:9, 1920x1080 unless render constraints force a lower local preview resolution.
```

Scene structure:

1. Problem: AI can draft replies faster than teams can explain what happened.
2. Routine case: invoice request flows through standard handling.
3. Sensitive case: billing complaint triggers the review boundary.
4. Human review: reviewer edits or approves before final response.
5. Profusion receipt: supported claims, unsupported claims, limitations.
6. Closing line: Profusion shows when AI work was safe to approve.

P1 commands:

```bash
npx hyperframes doctor
npx hyperframes preview
npx hyperframes render --output customer_trust_triage_receipt.mp4
npx hyperframes render --docker --output customer_trust_triage_receipt.docker.mp4
```

Docker render may be skipped only if Docker or HyperFrames Docker mode fails;
the failure must be recorded in `hyperframes_video_manifest.json`.

No TTS, music, avatars, vertical cuts, public website capture, or secondary
campaign video is allowed in the first P1 pass.

## TDD Plan

### Test 1: Fixture Loader Accepts The Happy Path

Write a unit test that loads `support-triage-human-review` and asserts:

- workflow name is present
- both case IDs are present
- routine case has AI classification and final reply
- sensitive case has AI classification, human review, and final reply

Expected failing reason before implementation:

```text
ModuleNotFoundError: No module named 'orchestrator.m8_gtm'
```

### Test 2: Fixture Validator Rejects Missing Human Review

Create a temporary fixture missing
`runs/run_002_sensitive_billing_complaint/human_review_event.json`.

Assert the validator raises an error containing:

```text
sensitive_billing_complaint requires a human_review_event.json artifact
```

### Test 3: Artifact Manifest Copies And Hashes Files

Run the manifest builder against the fixture into a temp packet directory.

Assert:

- `artifact_manifest.json` exists
- every required source artifact has a packet copy
- every artifact has a 64-character SHA-256 hash
- `workflow.json` is included
- both cases are included

### Test 4: Observation Builder Requires Honest Claims

Generate an observation from the happy-path fixture.

Assert:

- `source_system == "n8n"`
- `workflow_id == "support-triage-human-review"`
- `case_ids` contains both cases
- `human_review_events` contains the sensitive case
- `supported_claims` is non-empty
- `unsupported_claims` is non-empty
- `limitations` is non-empty
- one unsupported claim says the receipt does not prove billing truth

### Test 5: Receipt JSON Mirrors The Observation

Generate `workflow_receipt.json`.

Assert:

- `source_observation_id` matches `m8_observation.json`
- `claims_supported` equals or is a direct subset of observation supported
  claims
- `claims_not_supported` equals or is a direct subset of observation
  unsupported claims
- every displayed claim is sourced from the observation
- `where_human_review_entered` is non-empty

### Test 6: Markdown And HTML Receipts Contain Required Sections

Generate Markdown and HTML.

Assert both contain:

- `Customer Trust Triage Receipt`
- `Workflow Boundary`
- `Where AI Acted`
- `Where Human Review Entered`
- `Supported Claims`
- `Claims Not Supported`
- `Limitations`
- `Next Recommended Review`

Assert HTML escapes fixture text instead of injecting raw HTML.

### Test 7: CLI Produces The Complete Packet

Use `CliRunner` to run:

```text
m8 demo support-triage-human-review --output-dir <tmpdir>
```

Assert exit code 0 and generated files:

- `artifact_manifest.json`
- `m8_observation.json`
- `workflow_receipt.json`
- `workflow_receipt.md`
- `workflow_receipt.html`

Assert CLI output includes the HTML receipt path.

### Test 8: CLI Rejects Unknown Slugs

Use `CliRunner` to run:

```text
m8 demo not-a-real-workflow --output-dir <tmpdir>
```

Assert exit code 1 and output contains:

```text
Unknown M8 demo workflow
```

### Test 9: P1 Storyboard Is Downstream From Receipt

After P0 is implemented, add a P1 test that generates `demo_storyboard.md`
from `workflow_receipt.json` and `m8_observation.json`.

Assert every claim line in the storyboard appears in, or is directly mapped
from, the receipt or observation payload.

This test may be deferred until P1 starts.

### Test 10: HyperFrames Video Manifest Records Render Limits

After P1 is implemented, add a test for manifest creation.

Assert:

- `source_receipt_id` matches the receipt
- `source_observation_id` matches the observation
- `render_mode` is `local` or `docker`
- tool versions are present
- limitations are non-empty when local mode is used

This test may be deferred until P1 starts.

## P0 Acceptance Gate

P0 is accepted when all are true:

- `uv run profusion m8 demo support-triage-human-review` succeeds
- `artifact_manifest.json` exists
- `m8_observation.json` exists
- `workflow_receipt.json` exists
- `workflow_receipt.md` exists
- `workflow_receipt.html` exists
- supported claims are non-empty
- unsupported claims are non-empty
- limitations are non-empty
- routine and sensitive cases are both represented
- sensitive case has a human review event
- demo can be reproduced from a fresh checkout or documented local state
- `uv run pytest tests/test_m8_gtm_receipt_harness.py` passes
- `uv run pytest tests/test_receipts.py tests/test_measurements.py tests/test_m8_gtm_receipt_harness.py` passes

Full baseline before milestone closeout:

```bash
uv run pytest
uv run profusion smoke --offline
git diff --check
```

Cockpit, dashboard, and HyperFrames checks are not P0 blockers.

## P1 Acceptance Gate

P1 is accepted when all are true:

- P0 gate passed first
- `demo_storyboard.md` is generated from receipt outputs
- HyperFrames composition reads receipt/storyboard data, not hand-coded product
  claims
- `npx hyperframes doctor` passes or failure is documented
- `npx hyperframes preview` works
- `npx hyperframes render --output ...` works
- Docker render is attempted if available
- `hyperframes_video_manifest.json` is written
- MP4 is reviewed against the receipt for claim drift

## Open Decisions

No CEO/PM blocker remains before writing the implementation plan.

Implementation should preserve one assumption:

```text
P0 receipt harness is the deliverable. P1 video and P2 cockpit must not delay it.
```

The only review gate now is Kyle's approval of this spec before coding starts.

## Spec Self-Review

Placeholder scan: no TBD/TODO placeholders remain.

Scope check: the spec is decomposed into one P0 implementation, one P1 demo
layer, and one P2 optional cockpit layer. Only P0 is required for the first
implementation plan.

Ambiguity check: command shape, fixture paths, output artifacts, required
schemas, non-goals, and acceptance gates are explicit.

Claim check: the spec does not claim live n8n execution, compliance approval,
cross-machine deterministic HyperFrames rendering, customer traction, or
production readiness.
