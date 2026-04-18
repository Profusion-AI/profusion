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

### Default script variants and target duration
**Decision:** `profusion script` generates three default variants per planned item — `straight_explainer`, `provocative_hook`, `myth_vs_reality` — at a 60-second target.

**Rationale:**
- Three variants give enough spread to pick a lane without producing noise.
- Short-form educational media on the target platforms lives at 30–90s; 60s is the safe middle.
- Variant names are declarative (specified in the prompt input) so we can validate that Claude returned every requested variant, not just some subset.
