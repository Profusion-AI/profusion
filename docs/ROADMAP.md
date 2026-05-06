# Profusion Roadmap

Date: 2026-05-06

## Current Definition

Profusion AI is evolving into a governed AI-mediated workflow evidence system.
The current codebase implements its first governed workflow: a local-first
content operating system for AI-assisted media creation, review, rendering,
publishing, and receipt generation.

This roadmap does not replace the M0-M6 content operating system. It puts that
system inside the broader evidence architecture.

## Completed Foundation: M0-M6

M0-M6 established the local operating substrate:

- topic and source intake
- structured brief generation
- script variant generation
- local render job tracking
- rendered artifact manifests
- QA checks
- human approval gates
- approval-gated publishing
- scheduling and cross-post coordination
- retry lineage
- status, inspect, jobs, renders, approvals, logs, and handoff surfaces
- offline smoke verification

Business meaning: Profusion has a real local workflow substrate. It is not yet a
customer-facing SaaS product.

## M7: Internal Operator Cockpit

Source of truth: `docs/milestones/M7_OPERATOR_COCKPIT_PRD_TTD.md`

Status: locked and shipped on 2026-05-06.

Final lock record:
`docs/milestones/M7_OPERATOR_COCKPIT_FINAL_CLOSEOUT_2026-05-06.md`

M7 makes Profusion operable.

M7 is the internal operator cockpit for Kyle, Codex, Claude Code, and future
operators. It is not the public website, not a customer portal, and not the Work
Trust product.

Implementation boundary:

- keep the public `dashboard/` Netlify website untouched
- create `apps/operator-cockpit/` as the internal cockpit Vite app
- run it against `uv run profusion serve`
- consume existing FastAPI/read-model contracts
- expose only guarded safe retry mutations
- show approve, schedule, and publish as next safe commands, not buttons

M7 closeout is complete. It has a browser smoke record against the local API
and cockpit, plus a fresh 2026-05-06 lock verification covering the backend
test suite, offline smoke, cockpit tests, cockpit lint, static Netlify build,
and static cockpit smoke.

## M7.5 / PP1: Reviewer-Readable Evidence

Source of truth: `docs/milestones/M7_5_REVIEWER_EVIDENCE_PRD_TTD.md`

M7.5 makes Profusion explainable.

The first B2B-facing surface is a reviewer-readable evidence package, not a
portal. The first receipt type is `content_video_receipt`, generated from the
existing content item, render, QA, approval, artifact, log, and handoff flow.

Initial architecture:

- typed Python models and templates first
- file-based generated artifacts under `data/evidence/` and `data/receipts/`
- no SQLite migrations until the receipt shape survives real demo or pilot use
- receipt approval separate from content approval

Receipt domain language:

```text
trust_domain: media_trust
receipt_type: content_video_receipt
```

Reserved for later:

```text
receipt_type: live_session_receipt
```

## M7.6 / PP1-W: Work Trust Alpha

Work Trust makes Profusion expandable.

This is deferred until the M7.5 receipt path can generate a credible packet from
the existing content workflow.

Initial internal archetype:

```text
agentic_qa_evaluation_analyst
```

Commercial wedge:

```text
privileged remote AI-mediated worker or contractor access-risk evaluation
```

The first scenario can be "Audit a failed AI support workflow," but it must be
framed around observed behavior, verification, escalation, tool-use judgment,
documentation quality, and human accountability.

Do not include ranking, hire/no-hire, role-fit recommendation, automated
selection, or automated rejection language.

## M8: Measurement And Learning Loops

M8 remains deferred.

Do not prioritize measurement loops until:

- M7 is cleanly operable
- M7.5 can generate a reviewer-readable evidence packet
- there is buyer signal that measurement should move back onto the critical path

## Deferred Surfaces

The following are out of scope for M7 and M7.5:

- customer portal
- organization management
- billing
- external reviewer queues
- employer dashboards
- candidate auth
- automated hiring decisions
- candidate ranking
- detector-grade synthetic media claims
- live webcam receipt implementation
- public website rewrite
- Work Trust marketing launch

## Current Verification Baseline

Verification run on 2026-05-03:

```bash
uv run pytest
uv run profusion smoke --offline
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
```

Observed results:

- `uv run pytest`: 171 passed
- `uv run profusion smoke --offline`: passed
- `cd dashboard && pnpm lint`: blocked by local asdf `pnpm` shim
- `cd dashboard && pnpm build`: blocked by local asdf `pnpm` shim
- `cd dashboard && corepack pnpm lint`: passed
- `cd dashboard && corepack pnpm build`: passed

Use `corepack pnpm` for dashboard checks in this local environment unless the
asdf `pnpm` shim is repaired.
