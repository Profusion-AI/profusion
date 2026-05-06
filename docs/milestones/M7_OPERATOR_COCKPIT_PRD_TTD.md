# M7 Operator Cockpit PRD / TTD

Date: 2026-05-03

## Purpose

M7 makes Profusion operable.

The M7 operator cockpit is an internal local UI for inspecting, recovering, and
handing off Profusion workflow state. It is not the public Profusion AI website,
not a customer portal, and not the Work Trust product.

## Primary Users

- Kyle
- Codex and other coding agents
- Claude Code or future implementation agents
- future Profusion operators or contractors

## Non-Goals

M7 must not add:

- customer portal functionality
- public website changes
- organization management
- billing
- external review queues
- broad approve, schedule, publish, or archive buttons
- Work Trust scenario execution
- receipt generation as a primary cockpit feature
- automated hiring, ranking, or decisioning

## Current Repo Reality

The public website currently lives in `dashboard/` and is deployed by
`netlify.toml`.

The prior operator UI source still exists under `dashboard/src/`, including
operator routes in `dashboard/src/router.tsx`, but `dashboard/src/main.tsx`
currently renders the public website app.

The M7 boundary decision is to leave `dashboard/` alone and create a separate
operator cockpit at:

```text
apps/operator-cockpit/
```

This should be a standalone Vite app for now, not a full monorepo conversion.

## Local Development Flow

Run the API:

```bash
uv run profusion serve
```

Run the cockpit:

```bash
cd apps/operator-cockpit
pnpm dev
```

If the local asdf `pnpm` shim is broken, use:

```bash
cd apps/operator-cockpit
corepack pnpm dev
```

## Technical Contracts

The cockpit must consume the existing FastAPI/read-model contracts. It must not
query SQLite directly and must not duplicate lifecycle logic in React.

Required API surfaces:

- `GET /api/queue`
- `GET /api/items/{item_id}`
- `GET /api/items/{item_id}/jobs`
- `GET /api/items/{item_id}/renders`
- `GET /api/items/{item_id}/approvals`
- `GET /api/logs`
- guarded retry endpoints already exposed by the local API

The Python orchestration layer remains the source of truth for:

- lifecycle state
- retryability
- blockage/failure explanations
- artifact presence
- approval state
- next safe command

## Required Screens

### Queue View

Shows:

- all active content items
- lifecycle state
- blocked/failed items
- awaiting QA or approval
- scheduled/published items
- summary counts

### Item Detail View

Shows:

- item metadata
- current lifecycle state
- latest brief
- script variants
- render jobs
- publish jobs
- artifacts
- QA result
- approval state
- blockage
- recent logs
- retry status
- next safe command

### Job / Failure View

Shows:

- failed jobs
- failure stage
- failure message
- error code when present
- retryability
- exact retry command when safe

### Approval View

Shows:

- latest approval decision
- approval history
- publish eligibility
- relevant artifact state

### Handoff View

Shows enough context for a fresh operator or agent to resume work without
reconstructing state from terminal history.

## Mutating Actions

M7 mutating actions are limited to guarded safe retry paths.

The cockpit may show commands such as:

```bash
uv run profusion approve --item-id <id>
uv run profusion schedule --item-id <id> --at <iso-datetime> --target <platform:account-id>
uv run profusion publish-due
```

But those commands should be displayed as next safe commands, not exposed as
clickable broad controls.

## Acceptance Criteria

- `apps/operator-cockpit/` exists as the internal cockpit app.
- `dashboard/` remains the public Netlify website and is not modified for M7.
- The cockpit launches locally against `uv run profusion serve`.
- The cockpit can inspect the queue.
- The cockpit can open an item detail view.
- The item detail view shows lifecycle state, artifacts, jobs, approvals, logs,
  blockage, retryability, and next safe command.
- Failed jobs explain what happened and whether retry is safe.
- Safe retry actions are conservative and map to existing orchestration logic.
- Approve, schedule, publish, and archive are not exposed as broad buttons.
- No customer portal functionality is added.
- No Work Trust scenario functionality is added.
- A browser smoke test is documented.

## Browser Smoke Test

After implementation, run:

```bash
uv run profusion serve
cd apps/operator-cockpit
corepack pnpm dev
```

Smoke:

- load the cockpit root
- load queue view
- open at least one item detail route
- inspect artifacts, jobs, approvals, logs, blockage, retry, and next safe command
- verify a deep link refresh works
- verify invalid API paths return real API errors, not the SPA shell
- verify no public website route is needed for cockpit operation

## Verification Baseline

Current pre-implementation verification run on 2026-05-03:

```bash
uv run pytest
uv run profusion smoke --offline
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
```

Observed results:

- `uv run pytest`: 171 passed
- `uv run profusion smoke --offline`: passed
- `corepack pnpm lint` in `dashboard/`: passed
- `corepack pnpm build` in `dashboard/`: passed

Direct `pnpm` was blocked by the local asdf shim. Use `corepack pnpm` in this
environment unless that shim is repaired.

## Closeout Checklist

- [x] `apps/operator-cockpit/` created
- [x] cockpit dev command documented
- [x] public website untouched
- [x] queue view implemented
- [x] item detail view implemented
- [x] failure/retry view implemented
- [x] approval state visible
- [x] logs visible
- [x] next safe command visible
- [x] no broad dangerous controls
- [x] local browser smoke documented in `docs/milestones/M7_OPERATOR_COCKPIT_SMOKE_2026-05-03.md`
- [x] verification commands rerun
- [x] STATUS.md updated with actual result
