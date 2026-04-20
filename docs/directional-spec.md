# Profusion Directional Specification

## Purpose

Profusion is a local-first, approval-gated content operating system for credible
short-form educational media.

It is not a web app. The core product is a Python CLI, SQLite state machine, and
vendor-adapter pipeline that helps an operator move educational topics from raw
idea to scripted, rendered, reviewed, approved, scheduled, published, and
measured media.

The editorial center of gravity is:

- U.S. education failure and reform
- AI labor disruption
- post-labor economics
- future learning models
- institutional adaptation and failure

The operating principle is simple: no stage completes unless its guard passes.
Generated content is validated before persistence. Human approval remains a
first-class requirement before publishing.

## Current Status

Profusion is currently between M1 and M2.

M0 and M1 are complete. The system can ingest topics, generate structured briefs
with Claude, generate script variants, validate model output with Pydantic, and
advance items through the first editorial states.

Current implemented lifecycle:

```text
idea -> planned -> scripted
```

The next milestone, M2, turns Profusion from an editorial engine into a render
pipeline by integrating MoneyPrinterTurbo over HTTP.

Current target lifecycle after M2:

```text
scripted -> rendered
```

As of this checkpoint:

- `uv sync --frozen` passes.
- `uv run pytest` passes with 55 tests.
- `uv run profusion status` works.
- `uv run profusion check-env` works.
- The repo is clean on `main`.
- `render`, `qa`, `approve`, `publish`, `schedule`, and `retry` remain CLI stubs.
- The DB already contains future-facing tables for render, approval, and publish jobs.

This is roughly the halfway point in architectural development, not the halfway
point in user-visible capability. The hard substrate is in place: state machine,
schema, CLI, config, prompts, adapters, tests, and vendor boundaries. The
remaining work is where the pipeline becomes externally useful: rendering,
quality gates, approval, publishing, scheduling, and operational hardening.

## Product Direction

Profusion should become a durable operator cockpit for high-signal educational
media.

The operator should be able to:

1. Ingest topic ideas.
2. Generate a structured editorial brief.
3. Generate multiple script variants.
4. Select or default a script variant.
5. Render a local MP4 artifact.
6. Run QA against the rendered asset and editorial claims.
7. Approve or reject the item.
8. Publish or schedule the approved artifact.
9. Track outcomes and feed lessons back into future planning.

The project should preserve a narrow, reliable interface at every boundary. The
orchestrator owns state, validation, approvals, and editorial intent. Vendor
projects provide specialized execution engines and are called externally.

## Architecture Principles

### Local-first

The operator's source of truth is local SQLite state plus local artifacts. Remote
services may be used for generation, rendering assets, or publishing, but the
pipeline should remain inspectable and recoverable from local state.

### Approval-gated

Publishing should never become an accidental side effect of generation. A human
approval checkpoint must remain between QA and distribution.

### State-machine enforced

All lifecycle advancement must pass through `state.transition()`. Direct status
updates that bypass transition guards should be avoided in feature code.

### Pydantic before persistence

Any model, vendor, or API response that changes durable state must be validated
before it touches the database.

### Vendor isolation

The orchestrator must not import MoneyPrinterTurbo or MoneyPrinterV2 internals.
Turbo and V2 are external engines. The orchestrator calls them through adapters
over HTTP or process boundaries.

### Claude-only editorial LLM

Claude is the editorial LLM. Vendor LLM layers should be disabled or bypassed.
For Turbo, this means Profusion must provide both the final script and any
required video search terms or local materials.

### Tests avoid live services

Unit and CLI tests must not require live Turbo, V2, Firecrawl, or Claude calls.
Live-service verification belongs in runbooks and manual smoke checks.

## Milestone Plan

### M0: Foundation

Status: Complete.

Goal: establish the durable local substrate.

Delivered:

- Python 3.11 `uv` project
- Typer CLI entrypoint
- SQLite schema and idempotent migration path
- canonical content state machine
- Pydantic pipeline models
- config loader and `.env` support
- Claude adapter
- Turbo, V2, and Firecrawl adapter stubs
- vendor submodules under `vendor/`
- base tests
- architecture decisions

M0 turned the project from concept into a coherent local system.

### M1: Editorial Pipeline

Status: Complete.

Goal: move raw topics into validated script variants.

Delivered:

- `profusion ingest --topic`
- `profusion ingest --file`
- `profusion plan --item-id`
- `profusion script --item-id`
- schema v2 with `source_documents`, `risk_flags`, and `source_refs`
- structured prompt files
- Claude JSON extraction
- Pydantic validation before DB writes
- clean abort behavior on invalid model output
- status filtering via `profusion status --status`

Default script variants:

- `straight_explainer`
- `provocative_hook`
- `myth_vs_reality`

M1 produced the editorial engine. Profusion can now plan and script content
without corrupting state when generation fails.

### M2: Rendering

Status: Planned / next.

Goal: turn scripted items into local rendered MP4 artifacts.

Target lifecycle:

```text
scripted -> rendered
```

Core deliverables:

- configure Turbo as a separate vendor environment
- add `TURBO_URL`
- implement the Turbo adapter over HTTP
- implement `profusion render`
- create `render_jobs` rows before polling
- support async submission and `--wait`
- normalize Turbo task responses into a validated Profusion render result
- copy or resolve completed MP4 artifacts into `data/renders`
- store final `output_path`
- leave the item `scripted` on render failure
- optionally add `profusion jobs`

Important M2 hardening decisions:

- Do not rely on `/api/v1/ping`; Turbo's ping controller exists but is not
  currently mounted. Use a real mounted route such as `/api/v1/tasks`.
- Turbo accepts aspect ratios like `9:16`, not friendly names like `portrait`,
  unless the adapter maps them.
- Passing `video_script` bypasses Turbo script generation, but Turbo may still
  call its own LLM for video terms. Profusion should supply `video_terms` or use
  local materials.
- If possible, use the Turbo task ID as `render_jobs.id` to avoid a schema bump.
- Store failure details in a log file and put that path in `render_jobs.log_path`.

M2 is the moment Profusion becomes an artifact-producing system.

### M3: QA and Approval Gates

Status: Planned.

Goal: prevent rendered content from advancing without quality and editorial
review.

Target lifecycle:

```text
rendered -> qa_passed -> awaiting_approval -> approved
rendered -> qa_failed -> rendered
```

Expected deliverables:

- implement `profusion qa`
- validate rendered outputs exist and are readable
- run editorial risk checks against the final script and brief
- capture QA failures without advancing state
- implement `profusion approve`
- write approval decisions to `approval_records`
- distinguish approved, rejected, and revision-requested outcomes
- prevent publishing from anything short of approval

M3 is the governance layer. It keeps the system from becoming an automated
content cannon.

### M4: Publishing

Status: Planned.

Goal: publish approved artifacts through MoneyPrinterV2.

Target lifecycle:

```text
approved -> published
```

Expected deliverables:

- implement the V2 adapter
- preserve V2 as a separate vendor environment
- create and update `publish_jobs`
- support at least one publishing target
- store external post IDs and published URLs
- surface authentication or browser-session issues cleanly
- keep publishing gated behind approval

M4 connects Profusion to distribution.

### M5: Scheduling and Cross-Posting

Status: Planned.

Goal: support timed distribution and broader platform coordination.

Target lifecycle:

```text
approved -> scheduled -> published
```

Expected deliverables:

- implement `profusion schedule`
- schedule approved artifacts for future publication
- support platform-specific scheduling metadata
- prepare cross-posting workflows
- avoid automatic publishing without explicit approval state

M5 moves the system from one-off execution toward an operating rhythm.

### M6: Agent Hardening and Operational Durability

Status: Planned.

Goal: make Profusion reliable for repeated agent and operator use.

Expected deliverables:

- stronger runbooks
- safer retry semantics
- better handoff reports
- clearer job inspection commands
- idempotent recovery paths
- durable logs and diagnostics
- release and smoke-test checklists
- tighter docs around local state and artifacts

M6 makes the system boring in the right way: recoverable, inspectable, and hard
to misuse.

## Target End State

The intended end-to-end lifecycle is:

```text
idea
  -> planned
  -> scripted
  -> rendered
  -> qa_passed
  -> awaiting_approval
  -> approved
  -> scheduled
  -> published
  -> measured
  -> archived
```

Failure and revision paths should be explicit:

```text
rendered -> qa_failed -> rendered
scripted -> rendered failure leaves item scripted
awaiting_approval -> rejected or revision_requested should not publish
```

The system should favor conservative, visible operator control over hidden
automation.

## Near-Term Priority

The next useful work is M2.

Implementation should focus on the smallest render path that preserves the
architecture:

1. Add Turbo config.
2. Implement typed HTTP adapter.
3. Normalize and validate Turbo responses.
4. Implement `profusion render`.
5. Create `render_jobs` before polling.
6. Store local MP4 artifact path on completion.
7. Keep item state unchanged on render failure.
8. Add tests with mocked HTTP.
9. Update runbooks and decisions.

Do not expand into QA, approval, publishing, scheduling, dashboards, retries, or
Firecrawl during M2. Those are separate milestones for a reason.
