# Architecture Decisions

## M0 — Foundation

### Python version split
**Decision:** Orchestrator uses Python 3.11. Vendor deps are NOT installed in the orchestrator venv.

**Rationale:**
- System Python is 3.14.2, which is too new for most ML/AI deps in both vendor repos.
- MoneyPrinterTurbo declares `requires-python = ">=3.11,<3.13"` in its pyproject.toml.
- MoneyPrinterV2 README specifies Python 3.12 with `.python-version = 3.12`.
- Python 3.11 is the safe intersection for the orchestrator layer.
- Future vendor envs: Turbo will use a 3.11 or 3.12 venv (M2); V2 will use a 3.12 venv (M4).

### Submodule strategy
**Decision:** MoneyPrinterTurbo and MoneyPrinterV2 are managed as git submodules under `vendor/`.

**Rationale:**
- Upstream repos remain upgradeable independently.
- Submodule SHA pins prevent silent upstream breakage.
- No modifications to vendor code in M0 — adapters wrap them externally.
- PRD §3.3 explicitly warns against merging repos naively.

### LLM routing
**Decision:** All LLM calls go through the orchestrator's `claude.py` adapter (Anthropic SDK), not through MoneyPrinterTurbo's internal LLM layer.

**Rationale:**
- Both Claude Code and Codex are locally installed and already making API calls.
- MoneyPrinterTurbo's LLM layer is redundant overhead at the wrong layer boundary.
- This gives the orchestrator full editorial control before media generation begins.
- GPU (GTX 1050 Ti, 4GB VRAM) is freed from LLM inference and available for NVENC video encoding.

### State machine: §12.5 vs §13
**Decision:** Using PRD §13 as the canonical state list (12 states, includes `measured`).

**Rationale:**
- PRD §12.5 lists 11 states and omits `measured`.
- PRD §13 (Content State Machine) explicitly includes `measured` as state 10 between `published` and `archived`.
- §13 is the more detailed and intentional specification.
- `measured` enables a basic feedback loop (performance → next batch) which is a stated goal.

### src/ layout
**Decision:** Package lives at `src/orchestrator/` rather than `apps/orchestrator/`.

**Rationale:**
- `src/` layout is the standard Python packaging convention with hatchling.
- Avoids import ambiguity when running `uv run profusion` — hatchling knows exactly which directory to package.
- `pyproject.toml` declares `[tool.hatch.build.targets.wheel] packages = ["src/orchestrator"]`.
- Simpler than a monorepo `apps/` structure for a single-package project at this stage.

### sqlite3 vs sqlite-utils
**Decision:** `db.py` uses raw `sqlite3` for schema management and queries. `sqlite-utils` is retained as a dependency for CRUD helpers in M1+.

**Rationale:**
- `sqlite3` is sufficient for the M0 schema init (DDL, PRAGMA, indexes) and gives direct control over connection lifecycle and row_factory.
- `sqlite-utils` provides a more ergonomic API for INSERT/SELECT/UPDATE operations that will be needed in M1 when items flow through the pipeline.
- Splitting the concern (sqlite3 for schema, sqlite-utils for CRUD) avoids a larger M0 refactor while keeping the dependency justified.

### TTS engine
**Decision:** Edge-TTS as default voice synthesis engine (not OpenAI TTS, not local models).

**Rationale:**
- Edge-TTS is free (Microsoft Azure TTS over internet), no API key required.
- MoneyPrinterTurbo supports it natively.
- Quality is solid for educational short-form content.
- Avoids additional API cost on top of Claude.
- Can be swapped to OpenAI TTS or a local model later via config.

## M1 — Editorial Pipeline

### Structured Claude output, validated before persistence
**Decision:** All brief- and script-generation calls prompt Claude for a single JSON object, which is parsed and validated by Pydantic (`BriefDraft`, `ScriptBatch`) before anything is written to the DB. Failures abort the transition.

**Rationale:**
- Freeform prose would force the orchestrator to scrape structured fields out of vague output and hope for the best.
- Structured output lets us enforce the editorial contract (required thesis, enumerated risk categories, variant completeness) at the seam, not at read-time.
- Validation failures cleanly short-circuit state transitions, so a bad model response never leaves the DB in a half-advanced state.
- The brief-generation prompt lives in `src/orchestrator/prompts/planning/brief.md` so the contract is versioned with the code.

### Editorial metadata lives in the brief schema, not in prose
**Decision:** Extended `content_briefs` with `risk_flags` and `source_refs` JSON columns. Added a dedicated `source_documents` table for raw source material.

**Rationale:**
- Risks and verifiable claims are first-class editorial artifacts — burying them in `brand_notes` or `thesis` makes them unusable for later QA and approval gates.
- `source_documents` separates raw scraped/pasted material from the editorial synthesis that cites it. Firecrawl can populate the table later without schema churn.
- Schema bumped to v2 with an idempotent `ALTER TABLE ... ADD COLUMN` migration that is safe to run against existing v1 databases.

### Editorial logic lives outside the Claude adapter
**Decision:** Brief/script generation lives in `src/orchestrator/editorial.py`. The `claude.py` adapter stays transport-only.

**Rationale:**
- The adapter's only job is turning system+user text into a string and surfacing API errors. Prompt loading, JSON extraction, schema validation, and pipeline-specific invariants (e.g. "all requested variants must be returned") belong one layer up.
- This keeps the adapter trivially mockable — tests monkeypatch `claude.generate` without touching editorial logic.
- If the LLM provider changes, only the adapter is affected.

## M2 — Rendering

### Local MP4 required before state transition
**Decision:** The content item only advances from `scripted` to `rendered` after `final.mp4` exists at a local path and has a non-zero file size. If the MP4 download fails, the item stays `scripted` and the render job is marked `failed`.

**Rationale:**
- The M2 goal is a "local rendered MP4 artifact." Storing a remote URL that may later disappear violates the local-first principle.
- A zero-byte file is indistinguishable from a successful download in many checks; explicitly verifying `st_size > 0` catches partial writes.
- Conservative state advancement keeps the QA and approval gates in M3/M4 working against real local artifacts, not dead links.

### Turbo task_id as render_jobs primary key
**Decision:** `render_jobs.id` is set to MoneyPrinterTurbo's `task_id` (a UUID returned by `POST /api/v1/videos`).

**Rationale:**
- Avoids a schema v3 migration for an `external_task_id` column.
- The Turbo task ID is already globally unique (UUID4) and stable for the lifetime of the job.
- Makes polling and log correlation trivial: the job ID is the Turbo task ID everywhere.

### video_terms supplied to bypass Turbo's LLM
**Decision:** The `turbo.py` adapter always supplies both `video_script` (the Profusion-authored script) and `video_terms` (keywords derived from the topic via `_extract_terms()`) in the POST body.

**Rationale:**
- Turbo's `llm.generate_script()` is bypassed when `video_script` is non-empty.
- Turbo's `llm.generate_terms()` is bypassed when `video_terms` is provided.
- This preserves the "Claude is the only LLM" principle. No Turbo-side API key is required.
- `_extract_terms()` is a pure function (stop-word filter + length filter) that is deterministic and testable without mocking HTTP.

### Render manifest written alongside MP4
**Decision:** On successful render, a `manifest.json` is written to `data/renders/<task_id>/` alongside `final.mp4`. It records `content_item_id`, `script_variant_id`, `task_id`, `render_profile`, `output_path`, and `created_at`.

**Rationale:**
- Audits and re-renders need to answer "which script text produced this MP4?" without joining across the DB.
- The manifest is the artifact-level source-of-truth; the DB row is the process-level record.
- M3 QA and M4 publishing can load the manifest to validate the publication package without additional DB queries.

### Default script variants and target duration
**Decision:** `profusion script` generates three default variants per planned item — `straight_explainer`, `provocative_hook`, `myth_vs_reality` — at a 60-second target.

**Rationale:**
- Three variants give enough spread to pick a lane without producing noise.
- Short-form educational media on the target platforms lives at 30–90s; 60s is the safe middle.
- Variant names are declarative (specified in the prompt input) so we can validate that Claude returned every requested variant, not just some subset.

## M3 — QA + Approval Gates

### Claude QA uses updated post-render editorial_risk.md prompt
**Decision:** `profusion qa` runs the `editorial_risk.md` prompt against the rendered artifact's script and brief. The prompt was updated from "before rendering" to post-render context. Output is validated via `QAResult` Pydantic model.

**Rationale:**
- Reusing the existing editorial risk prompt avoids a new prompt with new schema and test surface.
- Post-render QA catches risks that survive scripting: stale facts, changed context, render-specific framing.
- Pydantic validation before state advance means Claude must return well-formed output; malformed output leaves the item in `rendered` rather than silently advancing.

### Approval is a single atomic DB transaction
**Decision:** `profusion approve` calls `record_approval_decision()` — a single connection that validates precondition, inserts the audit record, and walks `qa_passed → awaiting_approval → final` in one commit.

**Rationale:**
- The previous design used three separate DB calls, which could strand state without an audit record (if insert_approval_record succeeded but the final status update failed) or create a record without advancing state (if commit ordering was wrong).
- A single transaction with rollback-on-exception guarantees that either the full decision is recorded or nothing changes.

### revision_requested transitions to scripted, not archived
**Decision:** A `revision_requested` approval decision returns the item to `scripted` status, enabling new script variants and a re-render without losing the content item.

**Rationale:**
- `archived` is terminal; revision implies the content concept is sound but the execution needs work.
- Returning to `scripted` lets the operator run `profusion script` again and pick a better variant, then re-render.
- Requires the `awaiting_approval → scripted` transition in state.py (added in M3).

## M4 — Publishing

### Immediate publish keeps scheduled transient
**Decision:** `profusion publish` records a pending `publish_jobs` row, calls the V2/PostBridge adapter immediately, and uses `record_publish_complete()` to walk `approved → scheduled → published` in one transaction.

**Rationale:**
- Immediate publish is an operator-triggered action, not a durable scheduled state.
- Keeping both transitions in one transaction prevents an immediate publish from stranding an item in `scheduled`.
- M5 can introduce real scheduled jobs through separate helpers without changing the M4 command's behavior.

## M5 — Scheduling + Cross-Posting

### publish_jobs is the scheduling table
**Decision:** Scheduling metadata lives on `publish_jobs` via schema v3 columns rather than a new `schedule_jobs` table.

**Rationale:**
- A scheduled post is still a publish job; splitting the concept would create unnecessary coordination tables.
- One row per platform/account target naturally models cross-posting.
- Existing M4 job inspection and completion semantics remain useful with richer metadata.

### Profusion owns scheduling; PostBridge owns publishing
**Decision:** M5 stores future publish intent locally and executes due jobs through `profusion publish-due`; it does not delegate future scheduling to PostBridge.

**Rationale:**
- Local scheduling keeps the approval gate and state machine authoritative.
- Operators can see items resting in `scheduled` before distribution.
- PostBridge API scheduling can be added later, but local due execution is easier to test and recover.

### Scheduled completion waits for every target
**Decision:** A scheduled item transitions `scheduled → published` only after every scheduled target job for that item is `completed`.

**Rationale:**
- Cross-posting is a coordinated distribution action; one successful target should not make the whole item look published.
- Partial failures remain visible through failed `publish_jobs` and `last_error`.
- This gives M6 a clear recovery surface for idempotent retries.

## M6 — Agent Hardening + Operational Durability

### CLI read models are dashboard contracts
**Decision:** M6 inspection commands expose both human CLI output and `--json` read models generated by orchestrator code, not direct SQLite queries from future UI code.

**Rationale:**
- M7 will need stable localhost cockpit payloads without moving business logic into React.
- Retryability, blockage, artifact presence, and next safe commands are orchestration concepts, not presentation-layer guesses.
- Keeping read models in Python preserves SQLite as the source of truth while making the command layer contract-shaped.

### Retry preserves failed history
**Decision:** M6 retries never mutate completed jobs and do not erase failed rows. Scheduled publish retries requeue the failed job; immediate publish and render retries create linked attempts.

**Rationale:**
- The operator must be able to audit what failed and what retry attempt replaced it.
- `retry_of_job_id` and `attempt_group_id` provide lineage without a separate attempts table.
- Completed jobs are treated as immutable because retrying them would obscure actual distribution history.

### Measurement remains M8
**Decision:** The `measured` state remains in the canonical state machine, but
measurement and learning-loop implementation belongs to M8 after the M7
operator cockpit boundary is in place.

**Rationale:**
- M6 hardens current operations; M7 gives the operator a local cockpit.
- Measurement depends on durable operator surfaces and should not be conflated with recovery work.
- Keeping `measured` in the model avoids churn when M8 closes the published -> measured loop.

## M8 — Measurement + Learning Loops

### Manual comparison dimensions stay file-first
**Decision:** Hook variant, content format, and editorial pillar comparison
metadata lives inside each measurement observation JSON file, not in a new
SQLite table.

**Rationale:**
- Early M8 still needs manual observation quality more than schema ceremony.
- The comparison vocabulary will change as real content and buyer demos produce
  evidence, so file-first metadata keeps the loop editable without migrations.
- Aggregate read models can still compare hooks, formats, and pillars while the
  operator cockpit remains read-only over FastAPI/CLI JSON contracts.

## 2026-05-03 — M7/M7.5 Strategic Boundary

### Broader evidence system without erasing the content OS
**Decision:** Profusion AI is evolving into a governed AI-mediated workflow evidence system, while the current repo remains the first governed workflow inside that architecture: a local-first content operating system for AI-assisted media creation, review, rendering, publishing, and receipt generation.

**Rationale:**
- M0-M6 already established a working content operating substrate.
- Reframing the repo too aggressively would turn M7 into a pivot project and obscure what has already been built.
- The broader evidence architecture gives M7.5 receipts and later Work Trust a coherent home without disrupting the current state machine.

### M7 cockpit is separate from the public website
**Decision:** Keep `dashboard/` as the public Netlify website for now and create the internal operator cockpit under `apps/operator-cockpit/`.

**Rationale:**
- `dashboard/` is the current Netlify build base and public website entrypoint.
- The prior operator routes still exist, but the active Vite entrypoint now renders the public site.
- A separate cockpit app gives M7 a clear internal boundary without renaming or moving the deployed website.
- The repo does not need a full monorepo conversion yet; a standalone Vite app is enough for M7.

### M7 mutating actions are safe retry only
**Decision:** M7 may expose guarded safe retry actions. Approve, schedule, publish, archive, and other broad state-moving operations should be displayed as next safe commands, not clickable cockpit controls.

**Rationale:**
- The original pipeline is approval-gated and operator-controlled.
- Retry semantics are already conservative and auditable.
- Broad action buttons would increase operational risk before the cockpit has earned that authority.

### M7.5 receipts are file-first
**Decision:** Start receipt/evidence primitives as typed Python models, templates, and generated files. Do not add SQLite receipt tables in the first M7.5 pass unless file-first generation proves impossible.

**Rationale:**
- The receipt shape needs to survive a real demo or pilot before being locked into migrations.
- File artifacts are easier to inspect, revise, and package for buyer review.
- The existing content workflow already has enough state to generate the first receipt without changing the core schema.

### First receipt is content_video_receipt
**Decision:** The first receipt is `content_video_receipt` under `trust_domain: media_trust`, generated from the existing content item, render, QA, approval, artifact, log, and handoff flow. `live_session_receipt` is reserved for the separate live webcam/trust-session path later.

**Rationale:**
- The content workflow exists now and can produce evidence without a new product surface.
- `video_trust` alone is ambiguous because it can mean content-pipeline video or live webcam sessions.
- Splitting receipt types keeps the architecture extensible without pretending both modes are ready.

### Receipt approval is separate from content approval
**Decision:** Receipt artifacts have their own status: `draft`, `reviewed`, `approved_for_packet`, and `delivered`.

**Rationale:**
- Content approval means a media item is cleared for publishing or scheduling.
- Receipt approval means the evidence artifact is accurate, bounded, and safe to show externally.
- Those are different claims and should not be collapsed.

### Work Trust remains additive and deferred
**Decision:** Treat "Profusion Work Trust Lab" as an internal business-line/R&D label for now. The implementation term is `work_trust`, and the future receipt mode is `agentic_capability_receipt`.

**Rationale:**
- Work Trust should enter through the evidence/receipt architecture after M7.5, not as a separate app or M7 pivot.
- The first internal scenario archetype can be `agentic_qa_evaluation_analyst`.
- Buyer-facing language should avoid automated hiring, ranking, hire/no-hire, and role-fit recommendation claims.

## Historical pre-split context

The 2026-05-08 M8 measurement decision below predates the 2026-05-17 split,
but still maps to current Profusion work as generic workflow outcome
observations. The old Substack publishing and evidence-loop decisions were
superseded by the split and archived in
`docs/archive/2026-05-17-project-split/DECISIONS_substack_spike_2026-05-17.md`.

## 2026-05-08 — M8 Measurement First Slice

### Measurements are manual and file-first before automation
**Decision:** Start M8 with manual measurement observations written under `data/measurements/<item_id>/`, plus CLI/API/cockpit read models. A valid first observation transitions eligible content from `published` to `measured`.

**Rationale:**
- The `measured` state already exists in the canonical state machine, but it needed a small real behavior.
- Manual observations let Profusion capture reviewer feedback, controlled-demo outcomes, or published metrics without committing to platform API imports too early.
- File-first artifacts preserve inspectability while the useful measurement shape is still being learned.
- Before the split, M8 was framed as content measurement loops; after the
  split, Profusion keeps only generic workflow outcome observations.

## 2026-05-17 — Profusion / Attention Media Lab split

**Decision:** Profusion and the education/content engine are separate projects.

**Rationale:**
- Profusion's near-term commercial lane is B2B workflow trust and evidence receipts.
- The education/content engine is a real project, but it should not define Profusion's product promise.
- MoneyPrinterTurbo, MoneyPrinterV2, Substack packaging, source packs, voice guides, and owned-media drafts belong in `/home/kyle/attention-media-lab`.
- Profusion keeps a sanitized demo workflow only to demonstrate receipt mechanics.
- M8 remains in Profusion only as generic workflow outcome observations.

## 2026-05-18 — M8-GTM Overlay and n8n proving ground

### M8 technical meaning stays intact
**Decision:** Use an M8-GTM Overlay for the next Profusion prototype. Do not
redefine M8 and do not create an M8.5 detour. M8 remains manual/file-first
workflow outcome observations; the first commercially useful M8 observation
loop will use an n8n workflow receipt harness as the proving ground.

**Rationale:**
- This preserves the current repo truth and milestone trail.
- n8n can provide the executable workflow substrate while Profusion captures
  evidence, records outcome observations, and generates the buyer-readable
  receipt.
- The overlay keeps Profusion out of AI observability, support automation,
  compliance automation, website redesign, and broad n8n-platform claims.
- The ship test is whether Profusion can take one AI-assisted workflow and
  produce a receipt showing what happened, what artifacts exist, what a human
  reviewed, what passed or failed, and what the receipt does not prove.

### First proving-ground workflow is support triage with human review
**Decision:** The first demo workflow is `support-triage-human-review`, framed
externally as a Customer Trust Triage Receipt or Sensitive Support Response
Receipt. Do not present the demo as generic support automation.

**Rationale:**
- The demo has a clear buyer-readable sequence: inbound customer message, AI
  classification, AI-drafted response, sensitive-case boundary, human
  approve/edit/reject event, final action, execution log, and Profusion receipt.
- The intended story is not "AI answers support tickets"; it is "Profusion shows
  when AI work was safe to approve."
- The first scenario should contrast one routine case with one sensitive billing
  complaint so the value of human judgment and reviewable evidence is visible.
- Live Gmail, Slack, customer data, and production n8n API integration are not
  required for the first prototype; realistic local JSON artifacts and a
  markdown receipt are acceptable if the evidence loop is durable and
  reproducible.
