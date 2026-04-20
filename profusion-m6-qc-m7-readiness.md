# Profusion M6 QC and M7 Readiness Check

Date: 2026-04-20

## Verdict

M6 is QC-passed for local operator use and is ready to hand off into M7 planning.

M7 is implementation-ready with one clear constraint: build the dashboard on top
of the M6 read-model layer or a thin local API that reuses it. Do not let React
query SQLite directly or duplicate lifecycle/retry logic.

## Verification Run

Commands run:

```bash
uv run pytest
uv run profusion smoke --offline
uv run profusion check-env
uv run profusion status
uv run profusion status --json
uv run profusion inspect --item-id 5f062aa8 --json
uv run profusion handoff --failed-only
uv run profusion logs --limit 5 --json
git diff --check
```

Results:

- `uv run pytest`: 148 passed.
- `uv run profusion smoke --offline`: passed.
- `git diff --check`: clean.
- `status --json` and `inspect --json`: emit ISO 8601 UTC timestamp strings.
- `handoff --failed-only`: no failed or blocked local items.
- `check-env`: ffmpeg present; NVENC unavailable; `ANTHROPIC_API_KEY` not set;
  Firecrawl returns 404; MoneyPrinterTurbo is not reachable. Those are expected
  local service/config conditions, not M6 contract failures.

## M6 Acceptance Criteria

1. Diagnose an item with one command: met via `profusion inspect --item-id`.
2. Normal recovery without SQLite edits: met via `retry`, `publish-due`, and
   stage-specific inspection commands.
3. Retry lineage visible: met via `retry_of_job_id` and `attempt_group_id` on
   render and publish jobs.
4. Standardized logs: met via paired `.log` and `.json` diagnostics.
5. Fresh-agent handoff: met via `profusion handoff`.
6. Machine-readable outputs: met for `status`, `inspect`, `jobs`, `renders`,
   `approvals`, `logs`, `handoff`, and `retry`.
7. Offline smoke: met via `profusion smoke --offline`.
8. Runbook separation: met via `docs/runbooks/`.

## QC Fixes Applied

- Normalized read-model timestamp fields to ISO 8601 UTC with `Z` suffix.
- Hardened diagnostic context redaction for nested secret-like keys and inline
  secret strings.
- Updated `docs/directional-spec-revised.md` so M7 is the local dashboard and
  M8 is measurement/learning loops.
- Added tests covering timestamp normalization and diagnostic context redaction.

## M7 Readiness

Ready backend surfaces:

- Queue overview: `status_payload()`, `profusion status --json`
- Item detail: `inspect_payload()`, `profusion inspect --json`
- Job history: `jobs_payload()`, `renders_payload()`
- Approval posture: `approvals_payload()`
- Logs: `diagnostics.list_logs()`, `profusion logs --json`
- Handoff view: `handoff_payload()`
- Retry actions: `retry_publish_job()`, `retry_render_job()`, `retry_qa_stage()`

Recommended M7 shape:

- Add a local backend service module that imports `orchestrator.read_models`,
  `orchestrator.retry`, and `orchestrator.diagnostics`.
- Put FastAPI or another thin Python local API in front of those services.
- Add a React/Vite dashboard as a local UI client.
- Keep CLI parity by ensuring every dashboard action maps to an existing CLI
  command or orchestration function.
- Treat SQLite as private to Python. React should consume JSON contracts only.

Suggested first M7 slices:

1. Scaffold local API endpoints for queue, item inspection, jobs, approvals,
   logs, and handoff.
2. Scaffold React dashboard with queue list and item detail.
3. Add read-only dashboard smoke tests using fixture DBs.
4. Add guarded mutation endpoints for retry actions only.
5. Add operator UX for next safe command, blockage, artifacts, and recent logs.

## Remaining Risks

- The worktree is dirty and includes many untracked M6 files. M7 should start
  after the M6 patchset is committed or otherwise snapshotted.
- Local live services are not fully available in this environment. M7 can start
  against fixture/local DB contracts, but live render/publish workflows still
  require configured Anthropic, Turbo, and PostBridge services.
- M7 needs an explicit choice of local API framework and frontend packaging.
  The current Python project has no web backend or JS toolchain dependencies.
