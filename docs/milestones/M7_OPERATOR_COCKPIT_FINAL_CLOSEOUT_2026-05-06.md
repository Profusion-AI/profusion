# M7 Operator Cockpit Final Closeout

Date: 2026-05-06

## Verdict

M7 is locked and shipped as the internal operator cockpit milestone.

The shipped M7 surface is the standalone cockpit app at:

```text
apps/operator-cockpit/
```

The public Profusion AI website remains the separate Vite app at:

```text
dashboard/
```

M7 is not a customer portal, not a public product launch, not Work Trust, and not
M8 measurement loops. It is the internal cockpit that makes the existing
Profusion workflow operable by Kyle, Codex, Claude Code, and future operators.

## What M7 Shipped

- Standalone internal Vite/React cockpit under `apps/operator-cockpit/`.
- Queue view with active item state, summary metrics, filters, and operator
  context.
- Item detail route with lifecycle state, artifacts, jobs, approvals, logs,
  blockage, retryability, handoff, and next safe command visibility.
- Failure/retry view that explains failed stages and keeps retry actions mapped
  to existing guarded orchestration logic.
- Approval visibility without turning approve, schedule, publish, archive, or
  receipt drafting into broad UI buttons.
- Logs and system/handoff surfaces for operator and agent continuity.
- Static Netlify preview path for remote review, using generated read-only
  `/api/*` snapshots.
- Browser-smoke and static-smoke documentation.

## Boundary Locked

M7 remains an internal operator cockpit over the existing FastAPI/read-model
contracts. The cockpit does not query SQLite directly, does not duplicate
lifecycle rules in React, and does not replace the CLI/backend source of truth.

Allowed M7 mutation lane:

- guarded safe retry only, through existing orchestration/API logic

Displayed but not exposed as broad cockpit buttons:

- `uv run profusion approve --item-id <id>`
- `uv run profusion schedule --item-id <id> --at <iso-datetime> --target <platform:account-id>`
- `uv run profusion publish-due`

Out of scope and still deferred:

- customer portal
- organization management
- billing
- external reviewer queues
- broad approve/schedule/publish/archive controls
- Work Trust scenario execution
- candidate ranking or hiring decision language
- M8 measurement and learning loops
- production customer-facing cockpit

## Progress From M6

M6 made the backend workflow inspectable, retryable, and handoff-safe from the
CLI and API. M7 converts those operator contracts into a local UI surface.

The meaningful progress is not new automation volume. It is operability:

- operators can scan workflow health without reconstructing state from terminal
  history
- failed and blocked work is visible with exact recovery context
- artifacts, jobs, approvals, logs, and handoff information are co-located
- risky lifecycle actions remain deliberate backend/terminal commands
- future agents can resume work from a cockpit view instead of a cold repo read

## Current Verification

Fresh verification run on 2026-05-06:

```bash
uv run pytest
uv run profusion smoke --offline
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm build:netlify
cd apps/operator-cockpit && corepack pnpm smoke:static
```

Observed results:

- `uv run pytest`: 182 passed
- `uv run profusion smoke --offline`: passed
- `cd apps/operator-cockpit && corepack pnpm test`: 3 files passed, 9 tests passed
- `cd apps/operator-cockpit && corepack pnpm lint`: passed
- `cd apps/operator-cockpit && corepack pnpm build:netlify`: exported 2 static item snapshots and built successfully
- `cd apps/operator-cockpit && corepack pnpm smoke:static`: passed for 2 items

The earlier M7 browser smoke remains documented in:

```text
docs/milestones/M7_OPERATOR_COCKPIT_SMOKE_2026-05-03.md
```

The earlier M7 closeout remains documented in:

```text
docs/milestones/M7_OPERATOR_COCKPIT_CLOSEOUT_2026-05-03.md
```

This file is the final lock record after the May 6 verification pass.

## Ship State

M7 should now be treated as closed for roadmap purposes.

Do not reopen M7 unless the internal cockpit breaks against the existing
FastAPI/read-model contracts. New buyer-facing receipt work belongs to M7.5 or
M7.75. Measurement loops remain M8 and are still deferred until receipt/pilot
buyer signal justifies them.

