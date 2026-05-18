# M8-GTM QC Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up the public Profusion repo after the M8-GTM QC audit without starting P0.1 or P1 implementation.

**Architecture:** Treat P0/P0.1 as receipt-first and fixture-backed. Add repo guardrails, runbooks, CI, and public/private artifact boundaries while freezing legacy MPT/V2 surfaces for P1.

**Tech Stack:** Markdown docs, Bash scripts, GitHub Actions, Python 3.11, `uv`, pytest.

---

### Task 1: Public Active-Surface Map

**Files:**
- Create: `docs/ACTIVE_SURFACES.md`
- Modify: `README.md`
- Modify: `AGENTS.md`

- [x] Add a public map that identifies active P0/P0.1 files, specified-but-not-started P1 artifacts, deferred P2 cockpit visibility, frozen legacy MPT/V2 surfaces, and ignored local artifact lanes.
- [x] Link the map from README and AGENTS so future agents start from the same project boundary.

### Task 2: Path C Turnkey Bootstrap

**Files:**
- Create: `scripts/bootstrap_uv.sh`
- Create: `scripts/path_c_smoke.sh`
- Create: `docs/runbooks/path_c_turnkey_reproduction.md`
- Modify: `docs/runbooks/README.md`
- Modify: `README.md`

- [x] Add a `uv` bootstrap script that installs `uv` with `python3 -m pip install --user uv` only when missing.
- [x] Add a Path C smoke script that generates the M8 demo receipt under `/tmp`, asserts the required packet files, and runs the targeted M8-GTM test.
- [x] Document the fresh-clone path and the exact commands to run.

### Task 3: Public CI Safety Net

**Files:**
- Create: `.github/workflows/ci.yml`

- [x] Add a backend CI job on push and pull request.
- [x] Use Python 3.11 and `uv`.
- [x] Run full pytest, offline smoke, and Path C smoke without vendor submodules.

### Task 4: Public/Private Artifact Guardrails

**Files:**
- Modify: `.gitignore`
- Modify: `.env.example`
- Modify: `docs/milestones/M8_GTM_QC_CLEANUP_2026-05-18.md`

- [x] Remove the fake-looking Anthropic key placeholder.
- [x] Ignore local explorations, source packs, drafts, exports, scratch output, and generated local artifacts.
- [x] Record the exec-level decisions surfaced by the QC audit.

### Task 5: Verification

**Files:**
- No new source files expected beyond cleanup artifacts.

- [ ] Run `scripts/path_c_smoke.sh`.
- [ ] Run `uv run pytest -q`.
- [ ] Run `uv run profusion smoke --offline`.
- [ ] Run `git diff --check`.
- [ ] Review `git diff --stat` and summarize assumptions/decisions.
