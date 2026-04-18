# Profusion Pipeline Status

## Current Milestone: M2 — Rendering (not started)

### M1: Editorial Pipeline — COMPLETE

**Goal:** Move content from raw topic → structured brief → script variants, with claims/risks captured and the state machine enforced throughout.

**Checklist:**
- [x] SQLite schema v2: `source_documents` table + `risk_flags` / `source_refs` on `content_briefs`
- [x] v1 → v2 migration is idempotent and preserves legacy rows (tested)
- [x] `profusion ingest --topic` and `--file CSV` create `idea`-stage items
- [x] `profusion plan --item-id <id>` generates a Claude-validated brief, transitions `idea → planned`
- [x] `profusion script --item-id <id>` generates 3 validated variants, transitions `planned → scripted`
- [x] Pydantic draft models validate all Claude output before DB insert (`BriefDraft`, `ScriptBatch`, `RiskFlag`, `ClaimToVerify`, `SourceRef`)
- [x] Prompts seeded under `src/orchestrator/prompts/{planning,scripting,qa}/`
- [x] `profusion status --status <state>` supports lifecycle filtering
- [x] All state transitions go through the `state.transition` guard — invalid transitions surface as CLI errors
- [x] 43/43 tests passing, no live API key required

**Notes:**
- Claude output is parsed as JSON (bare or markdown-fenced) and validated via Pydantic. Failures do not advance state.
- `data/topics/example.csv` seeded as an ingest smoke-test fixture.
- Firecrawl remains stubbed. `source_documents` can be populated manually (CLI surface deferred until scraping is required).

---

### M0: Foundation (Zero to One) — COMPLETE

**Goal:** Durable editorial substrate — repo, state machine, storage, CLI skeleton, vendor submodules.

**Checklist:**
- [x] `uv sync` succeeds from clean clone (Python 3.11.14)
- [x] `uv run python --version` prints 3.11.14
- [x] `uv run profusion status` prints empty queue table
- [x] `uv run profusion check-env` reports ffmpeg present, NVENC not in this ffmpeg build (software encoding fallback active), API key and Firecrawl awaiting .env
- [x] `uv run pytest` — 18/18 passed
- [x] Both vendor submodules present and pinned (Turbo SHA pinned, V2 SHA pinned)
- [x] DECISIONS.md populated with 7 architecture decisions
- [x] THIRD_PARTY_LICENSES.md complete with AGPL-3.0 legal note

**Notes:**
- NVENC not compiled into the system ffmpeg build. Software x264 encoding will be used for now. A custom ffmpeg build with NVENC support can be swapped in later if render speed becomes a bottleneck.
- Firecrawl `/health` returns 404 — service is running but health endpoint path differs. Firecrawl ingest stub ready for M1.

---

## Milestone Roadmap

| Milestone | Focus | Status |
|-----------|-------|--------|
| M0 | Foundation: repo, state machine, DB, CLI skeleton | Complete |
| M1 | Editorial pipeline: topic intake, briefs, scripts | Complete |
| M2 | Rendering: MoneyPrinterTurbo integration | Not started |
| M3 | QA + approval gates | Not started |
| M4 | Publishing: MoneyPrinterV2 integration | Not started |
| M5 | Scheduling + cross-posting | Not started |
| M6 | Agent-hardening: runbooks, idempotency, handoff | Not started |
