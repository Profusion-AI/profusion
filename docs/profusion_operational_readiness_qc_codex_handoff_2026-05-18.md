# Profusion Operational-Readiness QC + Product Direction Codex Handoff

Date: 2026-05-18
Prepared for: Kyle / Profusion
Intended recipient: Codex
Purpose: major operational-readiness QC of the attached Profusion direction docs, plus a CEO-level product direction summary and Codex execution note.

---

## 1. Executive verdict

**Verdict: GREEN for product direction, YELLOW-GREEN for operational execution.**

The attached documents now converge on a coherent Profusion direction:

> Profusion is the reliability / evidence layer for high-risk AI-assisted and agentic workflows. It turns one workflow into reviewable process evidence: artifacts, review gates, approvals, limitations, and a buyer-readable receipt.

The immediate executable path is also clear:

```text
P0: CLI + durable artifacts + generated workflow receipt
P1: HyperFrames-rendered demo video from receipt outputs
P2: optional read-only cockpit visibility
```

The core operating rule is:

```text
Receipt-real first. HyperFrames-rendered second. Cockpit-visible later.
```

The main readiness caveat: the M8-GTM receipt harness spec is marked as a draft for Kyle review. Codex should not implement against it until Kyle explicitly approves it or the spec status is changed to `Approved for implementation`.

---

## 2. Overall product direction analysis

Profusion should not be positioned publicly as a generic AI governance platform, a support automation product, a content tool, a recruiting tool, or an AI observability dashboard.

The durable company direction is:

```text
Workflow evidence and receipting for high-risk AI-assisted work.
```

The buyer-readable offer is:

```text
Governed AI Workflow Receipt Pilot
```

The sharper wedge is:

```text
AI Workflow Reliability Pilot
```

The commercial pain is not "people need more AI output." The pain is that AI-native teams can generate code, content, analysis, and workflow outputs faster than they can reliably review, approve, and defend them. Profusion's value is to close that reliability gap by making the process inspectable.

### Recommended public positioning

```text
Profusion helps teams turn high-risk AI-assisted workflows into reviewable evidence.
```

Or, for the event / founder pitch:

```text
AI made output cheap. Profusion makes AI-assisted work reviewable enough to trust.
```

### Product mechanism

A Profusion receipt should answer:

- What workflow ran?
- What inputs were used?
- Where did AI act?
- Where did human review occur?
- What final action happened?
- What artifacts were captured?
- What claim does the receipt support?
- What claim does the receipt not support?
- What are the limitations?
- What should be reviewed next?

### Strategic hierarchy

```text
Company category: AI workflow trust / workflow reliability infrastructure
Current offer: Governed AI Workflow Receipt Pilot
Near-term proof: Customer Trust Triage Receipt
Technical artifact: M8 file-first workflow outcome observation + workflow receipt
Demo layer: HyperFrames MP4 after P0 works
Internal visibility: M7/M7.5 cockpit/evidence surfaces, read-only only for this sprint
Future extension: MCP/event capture for agentic and coding-agent workflows
```

### What Profusion must not claim

Do not claim:

- live n8n execution in P0
- live Gmail, Slack, HubSpot, Sheets, OpenAI, Anthropic, or Google credentials
- automated support sending
- compliance certification
- legal assurance
- hiring decisions or candidate ranking
- AI observability platform coverage
- cross-machine deterministic video rendering unless Docker render succeeded
- production readiness
- customer traction
- "certified truth," "fully verified," or similar overclaims

Profusion should use bounded evidence language:

```text
Evidence available.
Human review occurred.
Receipt generated.
Supported claim.
Claim not supported.
Limitation stated.
Next recommended review.
```

---

## 3. Operational-readiness QC

### 3.1 Direction and scope

**Status: strong.**

The M8-GTM Overlay is correctly scoped as a manual/file-first workflow outcome observation layer, not a live integration platform. n8n is the proving-ground substrate, and the receipt is the buyer-readable artifact. The first demo workflow is `support-triage-human-review`, externally framed as `Customer Trust Triage Receipt`.

The product sentence is excellent and should remain the controlling narrative:

```text
The demo is not "AI answers support tickets."
The demo is "Profusion shows when AI work was safe to approve."
```

### 3.2 P0 execution readiness

**Status: ready after Kyle approval.**

P0 is sufficiently specified for Codex implementation. The command, fixture structure, output packet, data contracts, test plan, and acceptance gates are explicit.

Required command:

```bash
uv run profusion m8 demo support-triage-human-review
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

The runbook must explain:

- what is real
- what is mocked
- how to reproduce the demo
- what must be hardened before live customer-facing use

### 3.3 P1 readiness

**Status: clear, but must not begin before P0 acceptance.**

HyperFrames is approved as the P1 demo-video path, not as a product dependency and not as a P0 blocker.

Required P1 artifacts:

```text
demo_storyboard.md
hyperframes_video_manifest.json
customer_trust_triage_receipt.mp4
```

P1 must obey the claim drift rule:

```text
Every text claim shown in the HyperFrames video must be sourced from workflow_receipt.json,
workflow_receipt.md, m8_observation.json, or demo_storyboard.md generated from those files.
```

If HyperFrames threatens the P0 receipt target, Codex should stop video work and ship the receipt loop.

### 3.4 P2 readiness

**Status: intentionally deferred.**

Cockpit visibility is optional and must stay read-only. It may show receipt summary, artifact list, observation status, and supported/unsupported claims.

Do not add:

- approval buttons
- mutation logic
- scheduling/publishing controls
- new workflow state machine
- public website changes
- cockpit work exceeding 90 minutes before P0/P1 are clean

---

## 4. Top operational risks

### Risk 1: Draft-status ambiguity

The spec says "Do not implement until this spec is approved," while the broader plan says no CEO/PM blocker remains except approval. Codex needs a clean signal.

**Fix:** Kyle should explicitly approve the spec or Codex should update status only after approval:

```text
Status: Approved for implementation by Kyle on 2026-05-18.
```

### Risk 2: Overclaiming fixture-backed evidence

The demo is fixture-backed and local. It must not imply live n8n, Gmail, Slack, Sheets, HubSpot, or customer delivery.

**Fix:** make `source_system` and receipt limitation language unmistakable:

```text
This fixture simulates an n8n-style run with local artifacts; it does not prove live Gmail, Slack, Google Sheets, or n8n API execution.
```

### Risk 3: "send_final_reply" wording may imply live sending

The data contract includes `send_final_reply`, but P0 has no live external sends.

**Fix:** in P0 fixture/runbook/receipt copy, clarify that this is a simulated or fixture-recorded final action, not a live customer send. If the fixture calls it `send_final_reply`, the receipt should say something like:

```text
Final reply artifact was marked ready in the fixture execution log; no live customer message was sent by P0.
```

### Risk 4: Receipt JSON may become too implementation-oriented

The receipt must be buyer-readable. It can have machine fields, but the generated Markdown and HTML should not feel like developer telemetry.

**Fix:** render plain-English sections first; expose artifact IDs as evidence references, not the main story.

### Risk 5: HyperFrames can accidentally outrun the evidence

Video can introduce claims, polish, or product implication that the receipt does not support.

**Fix:** P1 storyboard must be generated from P0 receipt data, and the MP4 must be reviewed for claim drift before sharing.

### Risk 6: P2 cockpit temptation

It will be tempting to make the cockpit impressive. That is dangerous before the receipt loop works.

**Fix:** Codex should treat P2 as optional read-only visibility only, and should not build any mutation UI.

### Risk 7: Incomplete packet writes

A failed run could leave a half-valid receipt packet and confuse future reviewers.

**Fix:** implement atomic packet creation via temp directory + rename. If short on time, mark incomplete directories with `.partial` and print a clear CLI failure.

---

## 5. Proposed changes to relay to Codex

Codex should apply these changes before or during P0 implementation.

### Change 1: Add an implementation approval banner

At the top of the spec, after Kyle approval:

```markdown
Status: Approved for P0 implementation by Kyle on 2026-05-18.
Scope lock: P0 receipt harness only. P1 and P2 must not delay P0.
```

### Change 2: Add a `NO_CLAIMS` section to the runbook

The runbook should explicitly state what P0 does not prove:

```text
P0 does not prove live n8n execution.
P0 does not prove live Gmail/Slack/Sheets/HubSpot integration.
P0 does not send customer messages.
P0 does not certify compliance.
P0 does not provide legal assurance.
P0 does not prove the billing complaint is factually true.
P0 does not make support automation a product.
```

### Change 3: Make fixture-backed status explicit in every output

Add a field to `workflow_receipt.json` if compatible with the current contract:

```yaml
evidence_mode: fixture_backed_local_demo
```

If Codex wants to avoid contract expansion, include this in `limitations` and `evidence_boundary`.

### Change 4: Treat P0 as a pure file/CLI harness

Do not mutate SQLite. Do not alter content item lifecycle state. Do not touch the public website. Do not add cockpit mutation. Do not call live networks.

### Change 5: Make receipt rendering safe and readable

Markdown and HTML must include all required receipt sections. HTML must escape fixture text.

### Change 6: Add atomic packet write behavior

Generate into a temporary packet directory and rename only after all required artifacts are written. On failure, exit non-zero and avoid writing a completed packet.

### Change 7: Add a Codex-readable implementation summary after P0

Codex should write a short closeout note with:

```text
What was implemented
What tests passed
Where output artifacts are written
Known limitations
What is safe to do next
What remains blocked/deferred
```

---

## 6. Codex P0 execution brief

Codex should execute P0 in this order.

### Step 1: Read source docs and preserve boundaries

Read:

```text
/home/kyle/profusion/docs/superpowers/specs/2026-05-18-m8-gtm-n8n-receipt-harness-design.md
```

Confirm boundaries:

```text
M7 cockpit remains in apps/operator-cockpit/.
M7.5 reviewer evidence packets remain under src/orchestrator/receipts/.
M8 remains manual/file-first under src/orchestrator/measurements.py and data/measurements/.
Public website in dashboard/ is out of scope.
Education/content engine and Substack remain in /home/kyle/attention-media-lab, not Profusion.
```

### Step 2: Create fixtures

Create:

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

The sensitive case must include a human review event.

### Step 3: Implement P0 modules

Create:

```text
src/orchestrator/m8_gtm/__init__.py
src/orchestrator/m8_gtm/fixtures.py
src/orchestrator/m8_gtm/harness.py
src/orchestrator/m8_gtm/schemas.py
src/orchestrator/m8_gtm/renderers.py
```

Update:

```text
src/orchestrator/cli.py
```

### Step 4: Generate packet

Successful command:

```bash
uv run profusion m8 demo support-triage-human-review
```

Expected packet:

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
    run_002_sensitive_billing_complaint/
```

### Step 5: Add runbook

Create:

```text
docs/runbooks/m8_gtm_n8n_receipt_harness.md
```

It must include:

- how to run the demo
- what outputs are generated
- what is real
- what is mocked
- what is not proven
- troubleshooting
- next hardening steps before live customer-facing use

### Step 6: Add tests

Create:

```text
tests/test_m8_gtm_receipt_harness.py
```

Minimum tests:

1. fixture loader accepts happy path
2. fixture validator rejects missing sensitive human review
3. artifact manifest copies and hashes files
4. observation builder requires supported claims, unsupported claims, and limitations
5. receipt JSON mirrors observation
6. Markdown and HTML include required sections and escape fixture text
7. CLI produces complete packet
8. CLI rejects unknown slugs

P1 tests may be deferred until P1 starts.

### Step 7: Run acceptance checks

P0 acceptance:

```bash
uv run profusion m8 demo support-triage-human-review
uv run pytest tests/test_m8_gtm_receipt_harness.py
uv run pytest tests/test_receipts.py tests/test_measurements.py tests/test_m8_gtm_receipt_harness.py
```

Full baseline before milestone closeout:

```bash
uv run pytest
uv run profusion smoke --offline
git diff --check
```

P0 is not accepted unless supported claims, unsupported claims, and limitations are all non-empty, and the sensitive billing complaint includes human review.

---

## 7. CEO-level deliverables

These are Kyle-level decisions and deliverables, not Codex-only implementation tasks.

### CEO Deliverable 1: Approve the product direction

Approve this as the controlling company/product direction:

```text
Profusion turns high-risk AI-assisted workflows into reviewable evidence.
```

Approve this as the immediate productized offer:

```text
Governed AI Workflow Receipt Pilot / AI Workflow Reliability Pilot.
```

### CEO Deliverable 2: Approve the M8-GTM P0 spec

Explicitly approve the P0 fixture-backed receipt harness for implementation.

Decision line:

```text
Approved: implement P0 receipt harness first. P1 HyperFrames and P2 cockpit must not delay P0.
```

### CEO Deliverable 3: Approve claim boundaries

Approve the No-Claims policy:

```text
No live integration claims.
No compliance certification claims.
No legal assurance claims.
No automated hiring/support/customer-send claims.
No platform maturity claims.
No "certified truth" language.
```

### CEO Deliverable 4: Approve the first buyer-readable story

Approve:

```text
Customer Trust Triage Receipt
```

Approve the story:

```text
A routine invoice request proceeds normally. A sensitive billing complaint triggers review. AI drafts. Human review happens. Profusion produces a receipt showing what happened, what was reviewed, what is supported, what is not proven, and what to review next.
```

### CEO Deliverable 5: Approve first demo assets after P0

After Codex completes P0, Kyle should review:

- workflow_receipt.html
- workflow_receipt.md
- workflow_receipt.json
- m8_observation.json
- artifact_manifest.json
- runbook

Kyle should decide whether the generated receipt is credible enough for:

- internal demo
- event conversation
- design-partner follow-up
- P1 HyperFrames video

### CEO Deliverable 6: Prepare GTM companion materials

Once P0 output exists, prepare:

- one-page Profusion pitch summary
- sample workflow receipt screenshot or HTML link
- conversation capture sheet
- three follow-up templates
- short "what Profusion does / does not do" explanation
- 20-second and 45-second pitch

### CEO Deliverable 7: Decide first design-partner wedge

Initial ranking:

1. AI-forward engineering/product teams using coding agents and feeling review/reliability pain
2. AI content/media teams needing approval evidence
3. AI automation agencies needing a client-facing evidence layer
4. recruiting/staffing firms as a design-partner track, without ranking or hiring automation claims
5. internal AI governance/risk teams that need one workflow made inspectable

### CEO Deliverable 8: Decide when to start P1

Only start P1 after P0 acceptance and CEO review of receipt quality.

P1 goal:

```text
Explain the receipt. Do not create new product evidence.
```

### CEO Deliverable 9: Decide when to start P2

Only start P2 if P0/P1 are clean and cockpit work remains read-only.

P2 goal:

```text
Show generated receipt summary, artifact list, observation status, and supported/unsupported claims.
```

No approval buttons. No scheduling. No publishing. No mutation logic.

---

## 8. Codex prompt to paste

```text
You are Codex acting as the implementation and QC agent for Profusion's M8-GTM receipt harness.

Read the attached operational-readiness QC and the M8-GTM n8n Receipt Harness Design and TDD Spec before making changes.

Mission:
Implement P0 only: a fixture-backed CLI receipt harness for `support-triage-human-review`, externally framed as `Customer Trust Triage Receipt`.

Controlling rule:
Receipt-real first. HyperFrames-rendered second. Cockpit-visible later.

Do not start P1 HyperFrames work or P2 cockpit work until P0 passes its acceptance gate.

Product boundary:
This is not support automation. This is not live n8n integration. This is not AI observability. This is not compliance certification. This is not a public website change. The demo shows when AI work was safe to approve, using local fixtures and durable artifacts.

Implement:
- examples/m8/support-triage-human-review fixtures
- src/orchestrator/m8_gtm package
- fixture loader and validator
- artifact copier and manifest builder with SHA-256 hashes
- M8 observation builder
- workflow receipt JSON builder
- Markdown and HTML receipt renderers
- CLI command `uv run profusion m8 demo support-triage-human-review`
- docs/runbooks/m8_gtm_n8n_receipt_harness.md
- tests/test_m8_gtm_receipt_harness.py

Required generated P0 files:
- artifact_manifest.json
- m8_observation.json
- workflow_receipt.json
- workflow_receipt.md
- workflow_receipt.html

Hard requirements:
- no live network calls in P0
- no live Gmail/Slack/HubSpot/Sheets/n8n credentials
- no SQLite mutation
- no content lifecycle transition
- no public website changes
- no cockpit mutation logic
- supported claims must be non-empty
- unsupported claims must be non-empty
- limitations must be non-empty
- sensitive billing complaint must have a human review event
- HTML must escape fixture text
- failed runs must not leave a completed packet; use temp directory + rename or `.partial` with clear CLI failure

Run acceptance checks:
- uv run profusion m8 demo support-triage-human-review
- uv run pytest tests/test_m8_gtm_receipt_harness.py
- uv run pytest tests/test_receipts.py tests/test_measurements.py tests/test_m8_gtm_receipt_harness.py
- before milestone closeout: uv run pytest; uv run profusion smoke --offline; git diff --check

Closeout note required:
- what was implemented
- tests run and results
- output packet path
- limitations
- safe next step
- what remains deferred to P1/P2
```

---

## 9. Final recommendation

Approve the P0 spec and send Codex into implementation with a narrow mandate.

The strategic move is not to build a bigger platform today. The strategic move is to produce one honest, reproducible, buyer-readable receipt packet that proves Profusion's core mechanism:

```text
AI-assisted workflow -> captured artifacts -> human review boundary -> M8 observation -> workflow receipt -> supported and unsupported claims
```

Once that exists, the demo video, cockpit visibility, event pitch, design-partner conversations, and CEO-facing one-pager all become much easier and much more credible.
