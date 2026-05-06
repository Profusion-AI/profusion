# M7 To M8 Execution Map

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Carry the approved M7 cockpit direction into the next production-useful slices: M7 closeout, M7.5 reviewer evidence, and then M8 measurement loops.

**Architecture:** Keep the public website in `dashboard/`, the internal cockpit in `apps/operator-cockpit/`, and all workflow truth in the existing Python CLI/FastAPI/read-model layer. Add receipt/evidence primitives file-first under `src/orchestrator/receipts/` and `data/receipts/`; do not add receipt tables until the packet format survives real review.

**Tech Stack:** Python 3.11, Typer, Pydantic, FastAPI read models, React/Vite cockpit, static Netlify snapshot deploys.

---

## Milestone Order

### M7.0 Closeout: Operator Cockpit

Status: functionally complete after the visual port.

- [x] Preserve public `dashboard/` website boundary.
- [x] Keep cockpit as `apps/operator-cockpit/`.
- [x] Consume FastAPI/read-model contracts only.
- [x] Show queue, item detail, failures, approvals, evidence placeholders, logs, handoff, and next safe commands.
- [x] Keep approve, schedule, publish, and archive as terminal commands rather than broad cockpit buttons.
- [x] Deploy draft Netlify cockpit preview from static snapshot API.

### M7.1 Closeout Hardening

Goal: make the approved cockpit easier to preserve while M7.5 work lands.

- [x] Add a cockpit closeout note that points to the current draft URL, local commands, static deploy boundary, and known non-live mutations.
- [x] Add route-level smoke coverage for `/queue`, `/failures`, `/approvals`, `/evidence`, `/logs`, `/system`, and `/items/:id` against the static snapshot.
- [x] Add a compact screenshot checklist for desktop and mobile cockpit review.
- [x] Keep Netlify draft deploys separate from `profusion.ai` production promotion unless Kyle explicitly approves production changes.

### M7.5 Reviewer Evidence

Goal: generate the first reviewer-readable evidence packet from an existing content workflow.

- [x] Create `src/orchestrator/receipts/` with typed receipt models and a file-first generator.
- [x] Add `uv run profusion receipt draft --item-id <id> --json` to generate a draft `content_video_receipt`.
- [x] Write generated packet files to `data/receipts/<receipt_id>/`: `receipt.md`, `summary.md`, `limitations.md`, `reviewer_notes.md`, and `evidence.json`.
- [x] Include plain-English boundaries: workflow evidence, not identity verification, liveness verification, universal synthetic-media detection, or proof of no external manipulation.
- [x] Keep receipt status separate from content approval with initial status `draft`.
- [x] Add `GET /api/items/{item_id}/receipts` after the CLI/file contract is stable enough for the cockpit to consume.
- [x] Update the cockpit Evidence page to show real receipt draft presence and command visibility.
- [x] Deploy a new cockpit draft with receipt-aware Evidence view after backend and static snapshot export are updated.

### M7.6 Pilot Packet

Goal: package one credible demo artifact for buyer/reviewer conversations.

- [x] Generate a sample receipt packet from a local approved or QA-passed item.
- [x] Add a short `docs/milestones/M7_5_REVIEWER_EVIDENCE_SMOKE_2026-05-03.md` closeout note with commands, generated paths, limitations, and verification.
- [x] Confirm the packet contains no customer-portal, Work Trust, candidate ranking, automated hiring, or detector-grade claims.

### M8 Measurement And Learning Loops

Goal: close the published-to-measured loop after evidence receipts exist.

- [ ] Add file-first/manual measurement imports for published content metrics.
- [ ] Add read models for item-level and aggregate measurement state.
- [ ] Add CLI commands to record measurement observations and transition eligible `published` items to `measured`.
- [ ] Add cockpit measurement visibility only after CLI/read-model behavior is tested.
- [ ] Defer platform automation, optimization loops, and model feedback until manual measurement is reliable.

## First Execution Slice

Start with M7.5 Task 1:

- [x] Write failing tests for a draft `content_video_receipt` generated from an approved content item.
- [x] Implement file-first receipt models and generator.
- [x] Add `profusion receipt draft --item-id <id> --json`.
- [x] Add `profusion receipt list --item-id <id> --json`.
- [x] Add receipt read API and static snapshot route.
- [x] Connect cockpit Evidence view to receipt summaries.
- [x] Verify targeted receipt tests, then run the relevant M6/M7 smoke checks.
