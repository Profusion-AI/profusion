# M7.5 Reviewer Evidence Smoke

Date: 2026-05-03

## Scope

This smoke pass covers the first implemented M7.5 slice:

- file-first `content_video_receipt` generation
- CLI receipt drafting and listing
- receipt read API
- static cockpit snapshot export
- receipt-aware cockpit Evidence page

This now closes the first M7.5 reviewer-evidence slice. It proves a draft
receipt packet can be generated for an eligible content workflow and rendered
in the static cockpit evidence view while staying inside the approved boundary:
reviewer evidence for the content workflow, not a customer portal,
live-session receipt, Work Trust runner, or detector-grade claim.

## Implemented

- `src/orchestrator/receipts/generator.py`
- `src/orchestrator/receipts/__init__.py`
- `uv run profusion receipt draft --item-id <id> --json`
- `uv run profusion receipt list --item-id <id> --json`
- `GET /api/items/{item_id}/receipts`
- `apps/operator-cockpit` static snapshot export for
  `/api/items/:id/receipts`
- cockpit Evidence page receipt presence and terminal command visibility
- explicit M7.5 demo fixture seeding via `scripts/seed-m7-5-receipt-demo.py`
- static cockpit smoke via `apps/operator-cockpit/scripts/smoke-static-snapshot.mjs`

Generated draft packets write to:

```text
data/receipts/<receipt_id>/
  receipt.md
  summary.md
  limitations.md
  reviewer_notes.md
  evidence.json
```

Sample local demo packet:

```text
data/receipts/content-video-m75-demo-con-20260503T155812Z-ceb13ddd/
```

Sample item:

```text
m75-demo-content-video-receipt
```

The sample item is explicitly marked with `source=m7.5-demo-receipt`. It is a
static cockpit preview fixture, not a claim that live vendor render/publish
infrastructure ran during the Netlify deploy.

## Local Verification

Commands run:

```bash
uv run pytest
uv run profusion smoke --offline
uv run python scripts/seed-m7-5-receipt-demo.py
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm smoke:static
cd apps/operator-cockpit && corepack pnpm build:netlify
cd apps/operator-cockpit && COCKPIT_BASE_URL=https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app corepack pnpm smoke:static
```

Observed:

```text
uv run pytest: 179 passed
uv run profusion smoke --offline: passed
seed-m7-5-receipt-demo.py: created or reused m75-demo-content-video-receipt
cockpit Vitest: 8 passed
cockpit lint: passed
cockpit static smoke: passed for 2 items
cockpit build:netlify: passed
remote cockpit static smoke: passed for 2 items
```

## Netlify Draft

Receipt-aware draft URL:

```text
https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app/queue
```

Deploy logs:

```text
https://app.netlify.com/projects/profusionai/deploys/69f770eec1439a4cd6b2a8c9
```

Remote checks:

```text
/queue: 200
/api/queue: 200
/api/items/m75-demo-content-video-receipt/receipts: 200 application/json
https://profusion.ai: 200
```

Receipt snapshot response:

```json
{"receipt_count":1,"receipts":[{"receipt_status":"draft","receipt_type":"content_video_receipt"}]}
```

The cockpit Evidence page now has a receipt-backed demo row rather than only
the terminal-only draft command state.

## Closeout Boundary

- Receipt status is still `draft`; receipt approval/review transitions are a
  later operator-control decision, not hidden inside content approval.
- The sample packet contains no customer portal, Work Trust, candidate ranking,
  automated hiring, hire/no-hire, identity-verification, liveness-verification,
  or detector-grade claims.
- M8 may start manual measurement loops after Kyle confirms whether draft
  receipts are enough for the first reviewer conversation or whether a
  `reviewed -> approved_for_packet -> delivered` receipt lifecycle command is
  required first.
