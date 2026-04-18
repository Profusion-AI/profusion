# Profusion Pipeline Status

## Current Milestone: M1 — Editorial Pipeline

### M0: Foundation (Zero to One) — COMPLETE

**Goal:** Durable editorial substrate — repo, state machine, storage, CLI skeleton, vendor submodules.

**Checklist:**
- [x] `uv sync` succeeds from clean clone (Python 3.11.14)
- [x] `uv run python --version` prints 3.11.14
- [x] `uv run profusion status` prints empty queue table
- [x] `uv run profusion check-env` reports ffmpeg present, NVENC not in this ffmpeg build (software encoding fallback active), API key and Firecrawl awaiting .env
- [x] `uv run pytest` — 18/18 passed
- [x] Both vendor submodules present and pinned (Turbo SHA pinned, V2 SHA pinned)
- [x] DECISIONS.md populated with 6 architecture decisions
- [x] THIRD_PARTY_LICENSES.md complete with AGPL-3.0 legal note

**Notes:**
- NVENC not compiled into the system ffmpeg build. Software x264 encoding will be used for now. A custom ffmpeg build with NVENC support can be swapped in later if render speed becomes a bottleneck.
- Firecrawl `/health` returns 404 — service is running but health endpoint path differs. Firecrawl ingest stub ready for M1.

---

## Milestone Roadmap

| Milestone | Focus | Status |
|-----------|-------|--------|
| M0 | Foundation: repo, state machine, DB, CLI skeleton | Complete |
| M1 | Editorial pipeline: topic intake, briefs, scripts | Not started |
| M2 | Rendering: MoneyPrinterTurbo integration | Not started |
| M3 | QA + approval gates | Not started |
| M4 | Publishing: MoneyPrinterV2 integration | Not started |
| M5 | Scheduling + cross-posting | Not started |
| M6 | Agent-hardening: runbooks, idempotency, handoff | Not started |
