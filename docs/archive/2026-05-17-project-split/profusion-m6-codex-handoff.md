# Profusion Media Engine — M6 Codex Handoff

**Version:** 1.0  
**Date:** April 20, 2026  
**Audience:** Codex (primary implementation agent for M6)  
**Project:** Profusion Media Engine / Profusion Content Pipeline

---

## 1. Purpose of this handoff

This document is the controlling handoff for **Milestone 6 (M6): Agent Hardening + Operational Durability**.

The project has already moved well beyond foundation work. M0 through M5 are complete. The pipeline can ingest topics, generate structured briefs, produce script variants, render MP4 artifacts through MoneyPrinterTurbo, run QA and approval gates, publish approved assets via the MoneyPrinterV2/PostBridge path, and schedule cross-postable publish jobs for future execution.

What is missing is not core capability. What is missing is **operational durability**.

M6 exists to make Profusion survivable under repeated use, failures, handoffs, retries, and agent interruptions without relying on tribal memory, direct SQLite edits, or terminal archaeology.

This milestone must also prepare the project for a future **M7 localhost dashboard** used by the operator. That dashboard is not the work of M6, but M6 must create the stable command, data, and diagnostics surfaces that M7 will consume.

---

## 2. Current state of the project

Profusion is a **local-first, approval-gated, CLI-first content operating system** for source-aware, high-trust short-form educational media.

The architectural center of gravity is still:

- Python CLI as the primary operator surface
- SQLite as local durable state
- local artifacts and manifests as the source of truth for generated media packages
- vendor adapters around MoneyPrinterTurbo and MoneyPrinterV2/PostBridge
- explicit state machine enforcement
- Pydantic validation before persistence
- operator approval before public posting

The editorial focus remains:

- U.S. education failure and reform
- AI labor disruption
- post-labor economics
- future learning models
- institutional adaptation and failure

### Completed milestones

#### M0 — Foundation
Delivered:
- Python 3.11 `uv` project
- CLI skeleton
- SQLite schema and migration setup
- canonical state machine
- config loading and `.env` support
- vendor submodule boundaries
- architecture decisions and licensing docs

#### M1 — Editorial pipeline
Delivered:
- topic ingest from manual input and CSV
- planning and scripting commands
- structured Claude JSON extraction and validation
- brief and script persistence
- source/risk metadata in schema

#### M2 — Rendering
Delivered:
- typed Turbo adapter over HTTP
- `profusion render`
- local MP4 artifact requirement before `scripted -> rendered`
- render manifest creation
- duplicate render guard and `--force`
- render failure logging

#### M3 — QA + approval gates
Delivered:
- `profusion qa`
- `qa_report.json`
- `profusion approve`
- atomic approval decision persistence
- rejection / revision-requested paths

#### M4 — Publishing
Delivered:
- typed PostBridge/V2 publishing adapter
- `profusion publish`
- package validation before publish
- `publish_jobs` persistence
- safe publish failure behavior

#### M5 — Scheduling + cross-posting
Delivered:
- scheduling metadata on `publish_jobs`
- `profusion schedule`
- `profusion publish-due`
- durable `scheduled` state for multi-target publishing
- partial cross-post failure visibility

### Test posture at handoff

At the time of this handoff, the status docs indicate:

- M5 complete
- M6 not started
- 138/138 tests passing after M5

Treat that as the current operating assumption unless the repo state shows otherwise.

---

## 3. The core problem M6 must solve

Profusion currently works, but too much recovery logic still lives in human judgment and ad hoc DB manipulation.

That is unacceptable for the next phase.

The system now needs to become:

- inspectable without SQLite spelunking
- retryable without manual row surgery
- handoff-safe across fresh agent contexts
- log-rich enough to support diagnosis after failure
- idempotent enough to rerun confidently
- structured enough that a future local dashboard can sit on top of it cleanly

M6 is **not** about adding new media features.
M6 is about making the current system operationally boring in the right way.

---

## 4. Roadmap correction that must be adopted now

There is a roadmap contradiction in the existing project docs.

Some prior project language describes **M7 as Measurement and Learning Loops**.
The operator’s current direction is different:

- **M6** should harden the CLI/operator contract surface
- **M7** should become a **localhost user-facing dashboard** for the operator
- the older “measurement and learning loops” work should move to **M8**

### Corrected milestone sequence

#### M6 — Agent Hardening + Operational Durability
CLI/operator hardening, retry semantics, handoff surfaces, logs, smoke tests, JSON contracts.

#### M7 — Local Operator Dashboard
A localhost React webapp used by the operator. This is a local UI surface over existing orchestration logic, not a replacement for the CLI and not a SaaS pivot.

#### M8 — Measurement + Learning Loops
Performance capture, measurement workflows, editorial comparisons, and closing the `published -> measured` loop.

### Important doctrine

Do **not** remove the `measured` concept from the project worldview. Keep it in the long-range state model. Just move the substantial implementation milestone later.

---

## 5. M6 goal statement

### Goal

Turn Profusion from a working pipeline into an **operator-grade, agent-resumable system** that can survive failures, retries, and handoffs without requiring direct database edits for normal recovery.

### M6 must also prepare for M7

M6 must establish stable, machine-readable operator surfaces that a future localhost dashboard can consume.

That means the command layer must become a contract layer.

---

## 6. M6 deliverables

### 6.1 Inspection commands

Add operator-facing inspection commands so agents and humans can inspect state without poking SQLite manually.

Likely CLI surface:

```bash
uv run profusion jobs --item-id <id>
uv run profusion renders --item-id <id>
uv run profusion approvals --item-id <id>
uv run profusion inspect --item-id <id>
uv run profusion logs --item-id <id>
uv run profusion logs --job-id <id>
```

#### Required behavior

`inspect` should become the canonical situational-awareness command.

For a specific content item, it should show:

- item metadata
- current lifecycle state
- current milestone context
- latest brief, script, render, QA, approval, and publish records
- artifact paths
- most recent failure or blockage
- retryability / recoverability hints
- exact next safe command

### 6.2 Retry commands

Make retry an explicit product surface.

Likely CLI surface:

```bash
uv run profusion retry --item-id <id>
uv run profusion retry --job-id <publish-job-id>
uv run profusion retry --render-job-id <id>
uv run profusion retry --item-id <id> --stage qa
```

#### Minimum useful behavior

- failed scheduled publish job: allow controlled `failed -> scheduled` recovery when safe
- failed immediate publish job: preserve history and create a new pending publish attempt
- QA failure: support controlled return path without silent state mutation
- render failure: allow explicit resubmission and preserve failed history
- retries must not mutate completed jobs

### 6.3 Handoff reports

Add a command that produces a concise markdown handoff report for a fresh context window.

Likely CLI surface:

```bash
uv run profusion handoff --item-id <id>
uv run profusion handoff --status scheduled
uv run profusion handoff --failed-only
```

#### Report contents

- current milestone
- git SHA / branch / dirty state
- queue summary
- blocked or failed jobs
- recent logs
- artifact locations
- exact next safe command
- explicit operator cautions if manual review is required

This command should directly solve the “agent timed out / context window refreshed” failure mode.

### 6.4 Durable logs and diagnostics

Standardize logs across commands and stages.

Recommended convention:

```text
data/logs/render-<task_id>.log
data/logs/publish-<job_id>.log
data/logs/qa-<item_id>-<timestamp>.log
data/logs/agent-run-<run_id>.log
```

#### Logging requirements

Each log should include, at minimum:

- timestamp
- stage
- item ID and/or job ID
- attempt number
- exception class
- exception message
- relevant context block
- redacted secrets by default

If useful, add paired machine-readable diagnostics such as `.jsonl` or `.json` metadata alongside the human-readable logs.

### 6.5 Idempotency rules

M6 must define and enforce safe-to-rerun behavior.

At minimum:

- `schedule` must not duplicate identical scheduled targets unless `--force` is given
- `publish-due` must skip completed and currently processing jobs
- `inspect` and `handoff` must be read-only
- retry must never mutate completed jobs
- failed jobs must preserve history
- if a new job is created on retry, it must be clearly linked to the old one

### 6.6 Smoke test / release checklist

Add a repeatable local smoke-test path that proves the system can walk critical lifecycle surfaces without live vendor calls.

Minimum command surface:

```bash
uv run pytest
uv run profusion check-env
uv run profusion status
uv run profusion smoke --offline
```

#### Offline smoke expectations

A fixture-backed or temp-DB smoke path should verify:

- command boot and environment sanity
- queue visibility
- inspect/handoff output
- safe retry surfaces
- due-runner behavior without live PostBridge
- idempotency on repeated invocation

### 6.7 Docs cleanup

Current docs are overburdened.

M6 should reorganize operational docs into clearer categories:

```text
docs/runbooks/daily-operations.md
docs/runbooks/failure-recovery.md
docs/runbooks/handoff-checklist.md
docs/runbooks/release-checklist.md
```

`STATUS.md` should remain milestone/status focused.
`DECISIONS.md` should remain architectural and doctrinal.

---

## 7. M7 preparation requirements baked into M6

This is a critical requirement.

M6 is not just CLI polish. It must become the backend contract layer that enables M7.

### M7 concept

M7 will scaffold a **localhost React webapp** used by the operator.

That dashboard should provide a local UI over queue status, item details, artifacts, approvals, retries, and logs.

### What M6 must do now so M7 is sane later

Every inspection-oriented command should support a machine-readable output mode.

Recommended rule:

- default output: human-readable CLI summary
- optional output: `--json`

Commands that should support this:

```bash
uv run profusion status --json
uv run profusion inspect --item-id <id> --json
uv run profusion jobs --item-id <id> --json
uv run profusion renders --item-id <id> --json
uv run profusion approvals --item-id <id> --json
uv run profusion handoff --item-id <id> --json
```

### Contract rules for M7 compatibility

- timestamps standardized as ISO 8601 UTC
- status enums documented and stable
- artifact paths normalized
- retryability exposed explicitly, not inferred by UI guesswork
- error payloads should include both `error_code` and `error_message` where practical
- read models should be shaped for UI consumption rather than forcing the UI to reconstruct business logic

### M7 doctrine

Do **not** make the future React app the source of truth.
Do **not** let the frontend query SQLite directly.
Do **not** move business logic into React.

The dashboard should sit on top of orchestrator services or a thin local API/service layer that reuses orchestrator logic.

---

## 8. Recommended implementation order for Codex

Codex is the primary implementation agent for this milestone. Favor small, reviewable, durable changes.

### Slice 1 — Highest leverage

Build these first:

1. `profusion inspect --item-id <id>`
2. `profusion jobs --item-id <id>`
3. `profusion retry --job-id <publish-job-id>`
4. `profusion handoff`

Why this order:

- it gives immediate operational lift
- it removes the biggest human bottleneck: situational awareness
- it solves the fresh-context recovery problem first
- it lays the read-model foundation for M7

### Slice 2 — Logging and JSON contracts

Then add:

- standardized logging helpers
- `--json` support on inspection commands
- normalized error and artifact payloads
- log lookup conveniences

### Slice 3 — Idempotency and smoke hardening

Then add:

- duplicate schedule guards if not already fully enforced
- retry lineage tracking
- `smoke --offline`
- release checklist and failure-recovery docs

### Slice 4 — Optional but useful

If time and repo shape permit:

- item/job lineage fields for retry history
- summarized “why blocked” diagnostics in inspect output
- stable local service/read-model layer that M7 can reuse later

---

## 9. Recommended command semantics

### `profusion inspect --item-id <id>`

Should answer, in one place:

- What is this item?
- What state is it in?
- What artifacts exist?
- What is the latest job at each stage?
- Did anything fail?
- Is it retryable?
- What is the next safe command?

### `profusion jobs --item-id <id>`

Should summarize all relevant jobs associated with an item, including:

- render jobs
- publish jobs
- attempts and statuses
- latest error summary
- related artifact/log paths

### `profusion renders --item-id <id>`

Should provide a render-centered view:

- render job history
- selected script variant linkage
- manifest path
- final MP4 path
- current / latest render status
- retry hints

### `profusion approvals --item-id <id>`

Should show:

- approval history
- decision chronology
- current effective decision posture
- notes
- whether the item is eligible for publish or schedule

### `profusion retry ...`

Should be conservative and explicit.

The operator should always be able to see whether retry will:

- reuse an existing job
- requeue an existing failed job
- create a new job lineage node
- refuse because the target is completed / not retryable

### `profusion handoff ...`

Should produce:

- clean markdown for human/agent paste into a new context
- optional JSON for machine consumption later

---

## 10. Data and schema recommendations for M6

These are recommendations, not absolute mandates, but they are likely worth implementing if the current schema makes retry lineage ambiguous.

### Potential additions

For job lineage and retry clarity, consider adding fields such as:

- `retry_of_job_id`
- `supersedes_job_id`
- `attempt_group_id`
- `attempt_number`

For diagnostics, consider:

- `error_code`
- `log_path`
- `diagnostic_path`
- `retryable` or derived retryability metadata where appropriate

If schema changes are made, keep them minimal, documented, and migration-safe.

---

## 11. Guardrails for implementation

### Do not do these

- Do not introduce a public-facing web product in M6
- Do not build M7 inside M6
- Do not normalize direct DB mutation as a standard recovery flow
- Do not move core business logic into UI-facing code
- Do not deepen coupling to vendor internals unless absolutely necessary
- Do not add “smart” retry behavior that silently mutates history
- Do not break existing CLI flows in pursuit of cleaner abstractions

### Preserve these project doctrines

- local-first
- approval-gated
- state-machine enforced
- Pydantic before persistence
- vendor isolation
- auditability by default
- respectability over throughput

---

## 12. Suggested docs updates after implementation

When M6 lands, update at least these project surfaces:

- `STATUS.md`
- `DECISIONS.md`
- runbooks docs
- any CLI help text or README command references

### `STATUS.md` should reflect

- M6 objective
- completed slices
- command additions
- smoke-test posture
- remaining work toward M7

### `DECISIONS.md` should reflect

- roadmap correction: M7 dashboard, M8 measurement
- CLI JSON contract doctrine for future local dashboard
- explicit prohibition on direct-DB recovery as normal operations
- any schema changes made for retry lineage or diagnostics

---

## 13. Acceptance criteria for M6

M6 is accepted when all of the following are true:

1. A human or agent can diagnose any item with a single `inspect` command.
2. Normal recovery does not require direct SQLite edits.
3. Retry flows preserve history and make lineage visible.
4. Logs are standardized across stages and sufficient for diagnosis.
5. A fresh agent can resume work from a generated handoff report.
6. Inspection-oriented commands expose stable machine-readable output suitable for future UI use.
7. An offline smoke path verifies inspection, retry, and handoff behavior without live vendor calls.
8. Documentation clearly separates daily operations, failure recovery, handoff, and release procedures.

---

## 14. Definition of done for Codex

Codex’s mission is not to theorize endlessly. It is to make Profusion operationally durable without bloating the system or derailing the architecture.

A successful M6 implementation will leave the repo in this state:

- the system still feels CLI-first and local-first
- operator visibility is dramatically improved
- failure recovery becomes explicit and safe
- handoffs become pasteable and sane
- logs become useful rather than ornamental
- M7 can later scaffold a React dashboard on top of stable contracts instead of reverse-engineering the CLI from scratch

That is the bar.

---

## 15. Final instruction to Codex

Build M6 as if the next person to touch this repo has no tribal memory and no patience for ambiguity.

Do not build a prettier mess.
Build the contract layer that makes the current system durable, inspectable, retryable, and ready for a local dashboard in the next milestone.
