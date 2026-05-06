# M7.5 Reviewer Evidence PRD / TTD

Date: 2026-05-03

## Purpose

M7.5 makes Profusion explainable.

The first B2B-facing surface is a reviewer-readable evidence package generated
from the existing Profusion content workflow. It is not a customer portal and
not a Work Trust launch.

## Canonical Strategy

Profusion AI is evolving into a governed AI-mediated workflow evidence system.
The current repo remains its first workflow: a local-first content operating
system for governed AI-assisted media production.

M7.5 adds an evidence/receipt layer on top of that existing workflow. It should
not disrupt M0-M6.

## Initial Receipt Scope

Implement only:

```text
trust_domain: media_trust
receipt_type: content_video_receipt
```

The first receipt is generated from the existing Profusion flow:

```text
content item -> brief -> script -> render -> QA -> approval -> schedule/publish state -> evidence packet
```

Defer:

```text
receipt_type: live_session_receipt
```

The separate live webcam/trust-session path is not the first M7.5 target.

## Non-Goals

M7.5 must not add:

- SQLite migrations for receipt tables unless the file-first model is impossible
- customer portal functionality
- public website changes
- live webcam receipt implementation
- Work Trust scenario runner
- candidate authentication
- employer dashboard
- automated hiring
- candidate ranking
- hire/no-hire language
- detector-grade synthetic media claims

## Evidence Packet Audience

The first packet should be one plain-English artifact for a skeptical pilot
buyer/evaluator, with enough structure for technical, security, and compliance
review.

Do not create separate executive, HR, security, and technical artifacts yet.

## Receipt Structure

The first `content_video_receipt` should include:

1. Plain-English summary
2. What workflow was run
3. What artifacts were produced
4. What QA/review/approval occurred
5. What evidence exists
6. What this proves
7. What this does not prove
8. Technical appendix and artifact links

## Boundary Language

Every receipt should include plain-English boundaries.

Recommended media-trust boundary:

> Profusion documents the declared workflow, generated artifacts, QA checks,
> review state, approval state, and evidence trail for this content workflow. It
> does not claim universal synthetic-media detection, identity verification,
> liveness verification, or proof that manipulation did not occur outside the
> captured workflow.

Reserved Work Trust boundary:

> This receipt documents observed behavior in a structured AI-assisted work
> simulation. It does not rank, select, reject, or recommend candidates.

## Receipt Approval

Receipt approval is separate from content approval.

Content approval means:

> This video/content item is cleared for publishing or scheduling.

Receipt approval means:

> This evidence artifact is accurate, appropriately bounded, and safe to show
> externally.

Initial receipt status values:

```text
draft
reviewed
approved_for_packet
delivered
```

A content item must already be QA-passed or approved before the receipt can
claim that state. The receipt still needs its own review status before it enters
an external evidence packet.

## Implementation Shape

Start with typed Python models and file/template artifacts.

Adapt to the existing source layout. The current repo package is
`src/orchestrator/`, so the likely implementation paths are:

```text
src/orchestrator/evidence/
  __init__.py
  models.py
  builders.py

src/orchestrator/receipts/
  __init__.py
  models.py
  generator.py
  templates/
    content_video_receipt.md.j2

data/evidence/
data/receipts/
```

Do not introduce a new top-level `src/profusion/` package unless the repo is
renamed later.

## Initial Data Model

Use file-first typed models. These names are conceptual and may be represented
as Pydantic models or dataclasses:

```text
TrustSession
  id
  trust_domain
  subject_type
  subject_id
  status
  policy_profile
  created_at
  updated_at

EvidenceEvent
  id
  trust_session_id
  event_type
  actor
  payload
  artifact_path
  created_at

ReviewRecord
  id
  trust_session_id
  reviewer
  decision
  notes
  rubric
  created_at

Receipt
  id
  trust_session_id
  receipt_type
  version
  receipt_status
  summary_md
  html_path
  pdf_path
  created_at
```

For M7.5, generated JSON/Markdown files are sufficient. SQLite tables are a
later hardening step after the receipt schema survives demo or pilot use.

## Evidence Packet Shape

Initial generated folder:

```text
data/receipts/<receipt_id>/
  receipt.md
  summary.md
  evidence.json
  reviewer_notes.md
  limitations.md
  artifacts/
```

PDF export is useful but not required before the first Markdown evidence packet
is credible.

## Acceptance Criteria

- A reviewed/approved content workflow can generate a draft
  `content_video_receipt`. Implemented first slice:
  `uv run profusion receipt draft --item-id <id> --json`.
- The receipt is generated from existing content item, render, QA, approval,
  artifact, log, and handoff state. The first slice uses the existing inspect
  read model as the input contract.
- The receipt includes plain-English summary and limitations. Implemented in
  generated `receipt.md`, `summary.md`, and `limitations.md`.
- The receipt has a receipt status separate from content approval. Initial
  generated status is `draft`.
- Generated artifacts are written under `data/evidence/` or `data/receipts/`.
  The first slice writes to `data/receipts/<receipt_id>/`.
- No SQLite migrations are added unless documented as necessary.
- No customer portal is added.
- No public website changes are made.
- No live-session receipt is implemented.
- No Work Trust scenario runner is implemented.
- No automated hiring/ranking/selection language appears.

## Implementation Progress

Started on 2026-05-03:

- `src/orchestrator/receipts/generator.py`
- `src/orchestrator/receipts/__init__.py`
- `tests/test_receipts.py`
- `profusion receipt draft --item-id <id> [--json]`
- `profusion receipt list --item-id <id> [--json]`
- `GET /api/items/{item_id}/receipts`
- cockpit static snapshot export for `api/items/<id>/receipts.json`
- cockpit Evidence page receipt presence/terminal-command visibility
- explicit static-preview demo fixture in `src/orchestrator/demo_fixtures.py`
- demo seeding script at `scripts/seed-m7-5-receipt-demo.py`
- static snapshot smoke script at
  `apps/operator-cockpit/scripts/smoke-static-snapshot.mjs`

Targeted verification:

```bash
uv run pytest tests/test_receipts.py tests/test_m6_ops.py tests/test_api.py -q
```

Observed result:

```text
36 passed
```

Full verification after receipt API/cockpit wiring:

```bash
uv run pytest
uv run profusion smoke --offline
uv run python scripts/seed-m7-5-receipt-demo.py
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm smoke:static
cd apps/operator-cockpit && corepack pnpm build:netlify
cd apps/operator-cockpit && COCKPIT_BASE_URL=https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app corepack pnpm smoke:static
```

Observed results:

```text
179 passed
offline smoke passed
demo receipt seed created or reused m75-demo-content-video-receipt
dashboard lint/build passed
cockpit Vitest: 8 passed
cockpit lint: passed
cockpit static smoke passed
cockpit build:netlify: passed
remote cockpit static smoke passed
```

Receipt-aware Netlify draft:

```text
https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app/queue
```

## Verification Baseline

Before M7.5 closeout, rerun:

```bash
uv run pytest
uv run profusion smoke --offline
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
```

If `apps/operator-cockpit/` exists by then, also run:

```bash
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm build
```

Any failure should be recorded in the closeout notes as:

```text
Command:
Result:
Failure:
Likely cause:
Blocking M7.5 closeout: yes/no
Next fix:
```

## Future Work Trust Notes

Work Trust remains deferred until the content receipt path works.

Implementation term:

```text
work_trust
```

Internal business-line/R&D label:

```text
Profusion Work Trust Lab
```

Initial internal archetype:

```text
agentic_qa_evaluation_analyst
```

Commercial wedge:

```text
privileged remote AI-mediated worker or contractor access-risk evaluation
```

Future Agentic Capability Receipts may include:

- observed strengths
- observed risks
- evidence of verification behavior
- evidence of escalation judgment
- reviewer notes
- limitations
- conditions of assessment

They must not include:

- recommended role fit
- hire recommendation
- candidate ranking
- candidate selection recommendation
- automated rejection language
