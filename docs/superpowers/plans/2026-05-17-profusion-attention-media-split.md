# Profusion And Attention Media Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the education/content engine into `/home/kyle/attention-media-lab`, preserve MoneyPrinterTurbo and MoneyPrinterV2 there, and clean Profusion back to a B2B workflow-trust project with a sanitized demo workflow and generic workflow outcome observations.

**Architecture:** Extract first, then simplify. Profusion remains the B2B workflow trust and receipt system: cockpit, evidence boundaries, human review gates, receipt lifecycle, sanitized demo workflow, and generic outcome observations. Attention Media Lab becomes the owned education/media project: MoneyPrinterTurbo, MoneyPrinterV2, Substack package work, source packs, voice guide, drafts, and education-content planning.

**Tech Stack:** Python 3.11, Typer, FastAPI, SQLite, Vite/React operator cockpit, git submodules or vendored upstream copies, Markdown documentation, local file artifacts under `data/`.

---

## Non-Negotiable Constraints

- Do not delete existing documentation.
- Outdated Profusion or MPT/MoneyPrinter-related documentation must be moved under a `docs/archive/` folder, not removed.
- Preserve MoneyPrinterTurbo and MoneyPrinterV2 together in `/home/kyle/attention-media-lab`; keep them logically connected to the original MPT tool lineage.
- Profusion may borrow high-level review, receipt, limitation, and evidence-boundary ideas from the education/content project, but the two projects must not share a day-to-day workflow.
- Profusion B2B work has short-term priority.
- Substack publishing, education source packs, owned-media drafts, and education-channel measurement belong to Attention Media Lab.
- Profusion keeps generic M8 measurement as workflow outcome observations, not content-channel analytics.
- Keep the Profusion public website untouched unless a broken claim must be corrected.
- Avoid destructive git commands. Do not use `git reset --hard` or `git checkout --` for cleanup.

## Target File Map

### New Project: `/home/kyle/attention-media-lab`

- Create: `README.md` - active project purpose, boundary from Profusion, and MPT/V2 relationship.
- Create: `AGENTS.md` - local operating charter for the education/media project.
- Create: `docs/PROJECT_ORIGIN_2026-05-17.md` - explains the split from Profusion.
- Create: `docs/archive/profusion-import/README.md` - index of imported historical docs/artifacts.
- Create: `docs/archive/profusion-import/profusion_m8_pipeline_test_artifact.md` - copied from Profusion before Profusion archives it.
- Create: `docs/archive/profusion-import/M8_SUBSTACK_SPIKE_2026-05-08.md` - moved from Profusion dirty tree.
- Create: `docs/runbooks/substack_publishing.md` - moved from Profusion dirty tree.
- Create: `data/source_packs/profusion_substack_voice/` - moved from Profusion dirty tree.
- Create: `data/style/profusion_substack_voice_2026-05-08.md` - moved from Profusion dirty tree.
- Create: `data/drafts/profusion_substack_voice/human_in_the_loop_is_not_enough.md` - moved from Profusion dirty tree.
- Create: `vendor/MoneyPrinterTurbo/` - copied from `/home/kyle/profusion/vendor/MoneyPrinterTurbo`.
- Create: `vendor/MoneyPrinterV2/` - copied from `/home/kyle/profusion/vendor/MoneyPrinterV2`.
- Create: `src/attention_media_lab/substack_publish.py` - moved from Profusion dirty tree if kept as active code.
- Create: `src/attention_media_lab/adapters/substack.py` - moved from Profusion dirty tree if kept as active code.
- Create: `tests/test_substack_publish.py` - moved from Profusion dirty tree if kept as active code.

### Profusion Files To Create Or Update

- Create: `docs/PROJECT_SPLIT_DECISION_2026-05-17.md` - canonical split decision.
- Create: `docs/archive/2026-05-17-project-split/README.md` - archive index.
- Move to archive: `docs/directional-spec.md` -> `docs/archive/2026-05-17-project-split/directional-spec.md`.
- Move to archive: `docs/directional-spec-revised.md` -> `docs/archive/2026-05-17-project-split/directional-spec-revised.md`.
- Move to archive: `docs/profusion_m8_pipeline_test_artifact.md` -> `docs/archive/2026-05-17-project-split/profusion_m8_pipeline_test_artifact.md`.
- Modify: `README.md` - describe Profusion as B2B workflow trust, not an education media pipeline.
- Modify: `pyproject.toml` - update project description away from educational media.
- Modify: `STATUS.md` - add split status and current M7-M8 priority interpretation.
- Modify: `docs/ROADMAP.md` - make B2B workflow trust canonical and M8 generic outcome observations.
- Modify: `docs/architecture.md` - state that MPT/V2 are no longer Profusion core dependencies after extraction.
- Modify: `docs/business-update.md` - remove ambiguity between education-content engine and B2B pitch.
- Modify: `docs/milestones/M8_MEASUREMENT_LOOPS_FIRST_SLICE_2026-05-08.md` - reframe from content metrics to workflow outcome observations.
- Modify: `docs/profusion-m7-m8-status-review-2026-05-06.md` - add supersession note pointing to split decision.
- Modify: `docs/profusion-m75-m8-workflow-receipt-simulator-handoff.md` - add split note and archive any stale M8 stop-sign language if it conflicts with current direction.
- Modify: `DECISIONS.md` - add split decision and MPT/V2 relocation decision.
- Modify: `src/orchestrator/cli.py` - keep `measure`; remove or do not commit `substack` commands in Profusion.
- Modify: `src/orchestrator/api.py` - keep measurement endpoints if they are generic outcome observations.
- Modify: `src/orchestrator/measurements.py` - keep or rename language to workflow outcome observations.
- Modify: `apps/operator-cockpit/src/pages/MeasurementsPage.tsx` - label UI as outcome observations, not content analytics.
- Modify: `apps/operator-cockpit/src/domain/measurementViewModel.ts` and tests - keep generic dimensions or rename content-specific dimensions.
- Do not commit: `src/orchestrator/adapters/substack.py`, `src/orchestrator/substack_publish.py`, `tests/test_substack_publish.py` in Profusion after they are moved to Attention Media Lab.

## Task 1: Preflight Snapshot And Current-State Inventory

**Files:**
- Inspect: `/home/kyle/profusion`
- Create: `/home/kyle/profusion/docs/PROJECT_SPLIT_DECISION_2026-05-17.md`

- [ ] **Step 1: Capture the Profusion dirty tree before moving anything**

Run:

```bash
cd /home/kyle/profusion
git status --short > /tmp/profusion-split-status-before.txt
git diff --stat -- . ':(exclude)vendor' > /tmp/profusion-split-diffstat-before.txt
git ls-files --others --exclude-standard > /tmp/profusion-split-untracked-before.txt
```

Expected: files are written under `/tmp/` and reflect the current dirty tree.

- [ ] **Step 2: Verify the current baseline still passes**

Run:

```bash
cd /home/kyle/profusion
uv run pytest -q
uv run profusion smoke --offline
cd /home/kyle/profusion/apps/operator-cockpit
corepack pnpm test
corepack pnpm lint
```

Expected:

```text
pytest passes
[ok] offline smoke passed
operator cockpit tests pass
operator cockpit lint passes
```

- [ ] **Step 3: Write the canonical split decision doc**

Create `docs/PROJECT_SPLIT_DECISION_2026-05-17.md` with this content:

```markdown
# Profusion / Attention Media Lab Split Decision

Date: 2026-05-17

## Decision

Profusion and the education/content engine are now separate projects.

Profusion remains the B2B workflow-trust project. It focuses on evidence boundaries, human review gates, limitation language, receipt lifecycle, internal operator visibility, sanitized demo workflows, and founder-led workflow receipt pilots.

Attention Media Lab is the education/content project. It owns the real education media strategy, MoneyPrinterTurbo and MoneyPrinterV2 lineage, Substack package work, source packs, voice guides, owned-media drafts, and content-channel measurement.

The projects may borrow high-level concepts from each other, especially evidence boundaries, review gates, receipts, and limitation language. They should not share a working day-to-day workflow.

## Profusion Canonical Direction

Category: AI workflow trust.

First offer: founder-led Profusion Evidence Receipt Pilot.

Mechanism: one workflow, one evidence boundary, captured artifacts, human review gates, approval state, stated limitations, and a reviewer-readable workflow receipt.

Profusion should not be pitched as education-media automation, generic content automation, AI observability, compliance certification, deepfake detection, recruiting automation, or a turnkey SaaS platform unless future work proves those claims.

## Sanitized Demo Rule

Profusion may keep one sanitized AI-assisted media/content workflow as a demo receipt source. This demo exists to explain the receipt mechanism, not to operate Kyle's education media channel.

## M7 Through M8 Interpretation

M7 remains the internal operator cockpit.

M7.5 remains reviewer-readable evidence receipts.

M8 remains valid only as generic workflow outcome observations. It should not be framed as content-channel analytics inside Profusion.

## Archive Rule

Do not delete historical documentation. Outdated Profusion or MoneyPrinter-derived planning docs should move under `docs/archive/` with an index note explaining why they were archived.

## New Project

The education/content project lives at:

`/home/kyle/attention-media-lab`
```

- [ ] **Step 4: Commit the split decision only**

Run:

```bash
cd /home/kyle/profusion
git add docs/PROJECT_SPLIT_DECISION_2026-05-17.md
git commit -m "docs: record Profusion and Attention Media split"
```

Expected: one commit containing only the split decision doc.

## Task 2: Create Attention Media Lab And Import Education/Content Assets

**Files:**
- Create: `/home/kyle/attention-media-lab/README.md`
- Create: `/home/kyle/attention-media-lab/AGENTS.md`
- Create: `/home/kyle/attention-media-lab/docs/PROJECT_ORIGIN_2026-05-17.md`
- Create: `/home/kyle/attention-media-lab/docs/archive/profusion-import/README.md`
- Move/copy: Profusion education/Substack assets listed in the target file map.

- [ ] **Step 1: Create the new project skeleton**

Run:

```bash
mkdir -p /home/kyle/attention-media-lab/{docs/archive/profusion-import,docs/runbooks,data/source_packs,data/style,data/drafts,src/attention_media_lab/adapters,tests,vendor}
```

Expected: directory exists and is outside `/home/kyle/profusion`.

- [ ] **Step 2: Write the Attention Media Lab README**

Create `/home/kyle/attention-media-lab/README.md`:

```markdown
# Attention Media Lab

Attention Media Lab is Kyle's education and owned-media project for AI-era learning, Attention Intelligence, post-labor education, source-aware media, and thoughtful content production.

This project was split out of Profusion on 2026-05-17.

## Relationship To Profusion

Profusion is the B2B workflow-trust project.

Attention Media Lab is the education/content project.

The two projects can borrow high-level ideas from each other: evidence boundaries, review gates, limitation language, receipts, source discipline, and measured learning loops. They should not share a day-to-day operating workflow.

## MoneyPrinter Lineage

MoneyPrinterTurbo and MoneyPrinterV2 belong here as content-production tooling. Keep them logically connected to the original MPT-style toolchain and document any local changes clearly.

## Short-Term Priority

Profusion's B2B lane takes priority in the short term. Attention Media Lab should preserve and continue the education/content system without pulling Profusion back into owned-media operations.
```

- [ ] **Step 3: Write Attention Media Lab operating charter**

Create `/home/kyle/attention-media-lab/AGENTS.md`:

```markdown
# AGENTS.md - Attention Media Lab

Attention Media Lab is Kyle's education and owned-media project.

## Purpose

Build and operate a thoughtful education/content engine around AI-era learning, Attention Intelligence, post-labor education, source-aware media, and public thought leadership.

## Boundary From Profusion

Profusion is B2B workflow trust. Attention Media Lab is education/content.

Borrow ideas across projects only at the concept level. Do not create a dependency where Profusion must run Attention Media Lab or Attention Media Lab must run Profusion.

## Tooling Direction

MoneyPrinterTurbo and MoneyPrinterV2 live here as content-production tools.

Substack packaging, voice guides, source packs, education drafts, and content-channel measurements live here.

## Safety

Do not publish externally, send emails, post to Substack, or make public claims without Kyle approval.

Do not delete imported docs. Archive outdated docs under `docs/archive/`.
```

- [ ] **Step 4: Copy MoneyPrinterTurbo and MoneyPrinterV2 into the new project**

Run:

```bash
rsync -a --delete --exclude '.git' /home/kyle/profusion/vendor/MoneyPrinterTurbo/ /home/kyle/attention-media-lab/vendor/MoneyPrinterTurbo/
rsync -a --delete --exclude '.git' /home/kyle/profusion/vendor/MoneyPrinterV2/ /home/kyle/attention-media-lab/vendor/MoneyPrinterV2/
```

Expected: both vendor trees exist under `/home/kyle/attention-media-lab/vendor/`.

- [ ] **Step 5: Move Substack and education assets out of Profusion**

Run:

```bash
cd /home/kyle/profusion
mv data/source_packs/profusion_substack_voice /home/kyle/attention-media-lab/data/source_packs/
mv data/style/profusion_substack_voice_2026-05-08.md /home/kyle/attention-media-lab/data/style/
mv data/drafts/profusion_substack_voice /home/kyle/attention-media-lab/data/drafts/
mv docs/runbooks/substack_publishing.md /home/kyle/attention-media-lab/docs/runbooks/
mv docs/milestones/M8_SUBSTACK_SPIKE_2026-05-08.md /home/kyle/attention-media-lab/docs/archive/profusion-import/
mv "docs/Kyle Greenwell - AI Speed Is Not Enough. Work Has to Become Reviewable.pdf" /home/kyle/attention-media-lab/docs/archive/profusion-import/
```

Expected: these paths no longer appear as untracked Profusion files and exist under Attention Media Lab.

- [ ] **Step 6: Copy education test artifact before archiving the Profusion original**

Run:

```bash
cp /home/kyle/profusion/docs/profusion_m8_pipeline_test_artifact.md /home/kyle/attention-media-lab/docs/archive/profusion-import/profusion_m8_pipeline_test_artifact.md
```

Expected: Attention Media Lab has a preserved copy.

- [ ] **Step 7: Move Substack code to Attention Media Lab if it exists**

Run:

```bash
cd /home/kyle/profusion
test -f src/orchestrator/adapters/substack.py && mv src/orchestrator/adapters/substack.py /home/kyle/attention-media-lab/src/attention_media_lab/adapters/substack.py || true
test -f src/orchestrator/substack_publish.py && mv src/orchestrator/substack_publish.py /home/kyle/attention-media-lab/src/attention_media_lab/substack_publish.py || true
test -f tests/test_substack_publish.py && mv tests/test_substack_publish.py /home/kyle/attention-media-lab/tests/test_substack_publish.py || true
```

Expected: Substack code is not present in Profusion; it is preserved in Attention Media Lab.

- [ ] **Step 8: Write origin note and import archive index**

Create `/home/kyle/attention-media-lab/docs/PROJECT_ORIGIN_2026-05-17.md`:

```markdown
# Project Origin

Date: 2026-05-17

Attention Media Lab was split out of Profusion to separate Kyle's education/content work from Profusion's B2B workflow-trust lane.

Imported material includes MoneyPrinterTurbo, MoneyPrinterV2, Substack packaging work, voice/source artifacts, education-focused planning artifacts, and owned-media drafts.

Profusion remains the place for B2B evidence boundaries, workflow receipts, review gates, limitation language, sanitized demo workflows, and workflow outcome observations.
```

Create `/home/kyle/attention-media-lab/docs/archive/profusion-import/README.md`:

```markdown
# Profusion Import Archive

This folder preserves education/content and Substack materials imported from `/home/kyle/profusion` during the 2026-05-17 project split.

These files are historical source material for Attention Media Lab. They are not Profusion's current B2B roadmap.
```

- [ ] **Step 9: Initialize Attention Media Lab git repo**

Run:

```bash
cd /home/kyle/attention-media-lab
git init
git add .
git commit -m "Initial Attention Media Lab split import"
```

Expected: new repo has an initial commit containing the imported content and vendor trees.

## Task 3: Archive Outdated Profusion Docs Instead Of Deleting Them

**Files:**
- Create: `docs/archive/2026-05-17-project-split/README.md`
- Move: `docs/directional-spec.md`
- Move: `docs/directional-spec-revised.md`
- Move: `docs/profusion_m8_pipeline_test_artifact.md`

- [ ] **Step 1: Create Profusion archive folder**

Run:

```bash
cd /home/kyle/profusion
mkdir -p docs/archive/2026-05-17-project-split
```

Expected: archive folder exists.

- [ ] **Step 2: Write archive index**

Create `docs/archive/2026-05-17-project-split/README.md`:

```markdown
# 2026-05-17 Project Split Archive

This archive preserves Profusion documents that were accurate during the education/content-pipeline phase but no longer describe the active Profusion implementation vision.

Current direction:

- Profusion: B2B workflow trust, evidence boundaries, receipts, review gates, sanitized demo workflow, and workflow outcome observations.
- Attention Media Lab: education/content engine, MoneyPrinterTurbo, MoneyPrinterV2, Substack, source packs, voice guides, owned-media drafts, and content-channel measurement.

Archived documents are historical. Do not use them as current implementation guidance without checking `docs/PROJECT_SPLIT_DECISION_2026-05-17.md`, `STATUS.md`, and `docs/ROADMAP.md`.
```

- [ ] **Step 3: Move education-era docs into the archive**

Run:

```bash
cd /home/kyle/profusion
git mv docs/directional-spec.md docs/archive/2026-05-17-project-split/directional-spec.md
git mv docs/directional-spec-revised.md docs/archive/2026-05-17-project-split/directional-spec-revised.md
git mv docs/profusion_m8_pipeline_test_artifact.md docs/archive/2026-05-17-project-split/profusion_m8_pipeline_test_artifact.md
```

Expected: docs are moved, not deleted.

- [ ] **Step 4: Commit archive move**

Run:

```bash
cd /home/kyle/profusion
git add docs/archive/2026-05-17-project-split
git commit -m "docs: archive education-era Profusion planning"
```

Expected: commit contains only archive/index moves.

## Task 4: Reframe Profusion Docs Around B2B Workflow Trust

**Files:**
- Modify: `README.md`
- Modify: `pyproject.toml`
- Modify: `STATUS.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/architecture.md`
- Modify: `docs/business-update.md`
- Modify: `DECISIONS.md`

- [ ] **Step 1: Update README project description**

Change `README.md` line 3 to:

```markdown
B2B workflow-trust and evidence-receipt system. Profusion helps operators define evidence boundaries, preserve workflow artifacts, apply human review gates, state limitations, and produce reviewer-readable receipts for AI-assisted work.
```

- [ ] **Step 2: Update package description**

Change `pyproject.toml` project description to:

```toml
description = "B2B workflow-trust and evidence-receipt system"
```

- [ ] **Step 3: Update STATUS current-state heading**

In `STATUS.md`, replace the current project-state heading with:

```markdown
## Current Project State: Profusion split from education/content engine; M7 locked; M7.5 receipt slice complete; M8 outcome observations in progress
```

Add this paragraph immediately under it:

```markdown
As of 2026-05-17, Profusion is the B2B workflow-trust project. The real education/content engine, MoneyPrinterTurbo/MoneyPrinterV2 lineage, Substack package work, source packs, voice guides, and owned-media drafts now belong to `/home/kyle/attention-media-lab`. Profusion may keep a sanitized AI-assisted media/content demo only to explain receipt mechanics.
```

- [ ] **Step 4: Update ROADMAP current definition**

In `docs/ROADMAP.md`, replace the opening current definition with:

```markdown
Profusion AI is a governed AI-mediated workflow evidence system. Its near-term B2B lane is the Profusion Evidence Receipt Pilot: one workflow, one evidence boundary, captured artifacts, human review gates, stated limitations, and a reviewer-readable receipt.

The education/content engine has moved to `/home/kyle/attention-media-lab`. Profusion may retain one sanitized content/media demo as a receipt example, but it is not the owner of Kyle's education media channel.
```

- [ ] **Step 5: Add architecture split note**

In `docs/architecture.md`, add a top-level section near the top:

```markdown
## 2026-05-17 Project Boundary

Profusion's active architecture is workflow trust and evidence receipts. MoneyPrinterTurbo and MoneyPrinterV2 have moved to `/home/kyle/attention-media-lab` as education/content tooling. Existing Profusion render/publish code is legacy/demo infrastructure until a later cleanup removes or replaces it with fixture-backed demo receipts.
```

- [ ] **Step 6: Add DECISIONS entry**

Append to `DECISIONS.md`:

```markdown
## 2026-05-17 — Profusion / Attention Media Lab split

**Decision:** Profusion and the education/content engine are separate projects.

**Rationale:**
- Profusion's near-term commercial lane is B2B workflow trust and evidence receipts.
- The education/content engine is a real project, but it should not define Profusion's product promise.
- MoneyPrinterTurbo, MoneyPrinterV2, Substack packaging, source packs, voice guides, and owned-media drafts belong in `/home/kyle/attention-media-lab`.
- Profusion keeps a sanitized demo workflow only to demonstrate receipt mechanics.
- M8 remains in Profusion only as generic workflow outcome observations.
```

- [ ] **Step 7: Run doc drift search**

Run:

```bash
cd /home/kyle/profusion
rg -n "educational media|education content|Substack|MoneyPrinterTurbo|MoneyPrinterV2|content measurement|content-channel|Attention Intelligence" README.md STATUS.md docs DECISIONS.md pyproject.toml
```

Expected: any remaining hits are either in `docs/archive/`, explicitly framed as historical, or intentionally kept as sanitized demo context.

- [ ] **Step 8: Commit doc reframing**

Run:

```bash
cd /home/kyle/profusion
git add README.md pyproject.toml STATUS.md docs/ROADMAP.md docs/architecture.md docs/business-update.md DECISIONS.md
git commit -m "docs: reframe Profusion around workflow trust"
```

Expected: commit contains current docs only, not archive moves.

## Task 5: Keep M8 In Profusion As Generic Outcome Observations

**Files:**
- Modify: `src/orchestrator/measurements.py`
- Modify: `src/orchestrator/cli.py`
- Modify: `src/orchestrator/api.py`
- Modify: `src/orchestrator/read_models.py`
- Modify: `tests/test_measurements.py`
- Modify: `apps/operator-cockpit/src/domain/measurementViewModel.ts`
- Modify: `apps/operator-cockpit/src/domain/measurementViewModel.test.ts`
- Modify: `apps/operator-cockpit/src/pages/MeasurementsPage.tsx`
- Modify: `apps/operator-cockpit/src/pages/ItemPage.tsx`
- Modify: `docs/milestones/M8_MEASUREMENT_LOOPS_FIRST_SLICE_2026-05-08.md`

- [ ] **Step 1: Decide naming without a schema migration**

Use the existing command group name `measure` for compatibility, but change user-facing copy to "workflow outcome observations." Keep existing fields if already implemented, but interpret optional dimensions generically:

```text
hook_variant -> scenario_variant
content_format -> workflow_type
editorial_pillar -> trust_domain
```

If renaming stored keys would require migration, do not rename keys in this pass. Instead, add display aliases and documentation.

- [ ] **Step 2: Update CLI help text**

In `src/orchestrator/cli.py`, keep:

```python
measure_app = typer.Typer(help="Record and inspect manual workflow outcome observations.")
```

For `record`, use:

```python
@measure_app.command("record")
def measure_record(...):
    """Record a manual workflow outcome observation for a reviewed, demoed, or published workflow."""
```

- [ ] **Step 3: Remove Profusion substack command registration**

In `src/orchestrator/cli.py`, remove the `substack_app` registration and all `substack_*` commands from Profusion after confirming the code was moved to Attention Media Lab.

Run:

```bash
cd /home/kyle/profusion
uv run profusion --help | rg "substack" && false || true
```

Expected: no `substack` command appears in Profusion help.

- [ ] **Step 4: Update measurement tests**

In `tests/test_measurements.py`, add a test that records an internal demo outcome observation and asserts generic language fields survive:

```python
def test_measurement_summary_supports_workflow_outcome_observations(tmp_path):
    db_path = tmp_path / "content.db"
    measurements_dir = tmp_path / "measurements"
    # Use existing fixture/helper setup from this test file.
    # Record one observation with platform="internal_demo",
    # observation_type="reviewer_feedback", and qualitative_signal.
    # Assert summary contains observation_count == 1 and the qualitative signal
    # is reachable through latest_observation.
```

Use the existing helper style in `tests/test_measurements.py`; do not invent a second DB fixture layer.

- [ ] **Step 5: Update cockpit labels**

Change user-visible cockpit strings from content analytics language to outcome observation language:

```text
Measurements -> Outcome Observations
Content format -> Workflow type
Editorial pillar -> Trust domain
Hook variant -> Scenario variant
```

- [ ] **Step 6: Update M8 milestone doc**

At the top of `docs/milestones/M8_MEASUREMENT_LOOPS_FIRST_SLICE_2026-05-08.md`, add:

```markdown
## 2026-05-17 Split Update

After the Profusion / Attention Media Lab split, this M8 slice remains in Profusion only as generic workflow outcome observations. Substack publishing, education-channel analytics, source packs, voice guides, and owned-media measurement now belong to `/home/kyle/attention-media-lab`.
```

- [ ] **Step 7: Run targeted verification**

Run:

```bash
cd /home/kyle/profusion
uv run pytest tests/test_measurements.py -q
uv run profusion --help
uv run profusion measure --help
```

Expected:

```text
measurement tests pass
Profusion help includes measure
Profusion help does not include substack
```

- [ ] **Step 8: Commit M8 reframing**

Run:

```bash
cd /home/kyle/profusion
git add src/orchestrator/measurements.py src/orchestrator/cli.py src/orchestrator/api.py src/orchestrator/read_models.py tests/test_measurements.py apps/operator-cockpit/src/domain/measurementViewModel.ts apps/operator-cockpit/src/domain/measurementViewModel.test.ts apps/operator-cockpit/src/pages/MeasurementsPage.tsx apps/operator-cockpit/src/pages/ItemPage.tsx docs/milestones/M8_MEASUREMENT_LOOPS_FIRST_SLICE_2026-05-08.md
git commit -m "refactor: frame M8 as workflow outcome observations"
```

Expected: commit contains only M8 generic-measurement changes.

## Task 6: Deprecate Profusion Live MPT/V2 Dependency Without Breaking The Sanitized Demo

**Files:**
- Modify: `src/orchestrator/cli.py`
- Modify: `src/orchestrator/adapters/turbo.py`
- Modify: `src/orchestrator/adapters/v2.py`
- Modify: `docs/architecture.md`
- Modify: `STATUS.md`
- Modify: tests covering render/publish if present.

- [ ] **Step 1: Mark live render/publish as legacy/demo-only in CLI help**

Keep commands present in this pass unless tests show safe removal. Update help strings:

```text
render: Legacy/demo render path. Not part of the current B2B product promise.
publish: Legacy/demo publish path. Not part of the current B2B product promise.
```

- [ ] **Step 2: Add runtime warning for render/publish commands**

At the start of `render` and `publish` command handlers, print:

```python
console.print(
    "[yellow]Legacy demo path:[/yellow] live MoneyPrinter render/publish tooling has moved to /home/kyle/attention-media-lab. Profusion keeps this only for sanitized demo compatibility."
)
```

- [ ] **Step 3: Do not remove vendor submodules in this pass**

Leave `/home/kyle/profusion/vendor/MoneyPrinterTurbo` and `/home/kyle/profusion/vendor/MoneyPrinterV2` in place until the warning/deprecation pass is verified. Record in `STATUS.md` that removal is a later cleanup step after fixture-backed demo receipts replace live render/publish.

- [ ] **Step 4: Run render/publish tests**

Run:

```bash
cd /home/kyle/profusion
uv run pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit deprecation**

Run:

```bash
cd /home/kyle/profusion
git add src/orchestrator/cli.py docs/architecture.md STATUS.md
git commit -m "chore: mark render publish paths as legacy demo infrastructure"
```

Expected: commit keeps compatibility and clearly documents non-core status.

## Task 7: Final Documentation Drift Pass And Archive Remaining Outdated Docs

**Files:**
- Inspect: `docs/`
- Move: `docs/profusion-m7-m8-status-review-2026-05-06.md`
- Move: `docs/profusion-m75-m8-workflow-receipt-simulator-handoff.md`
- Move: `docs/profusion-m775-implementation-alignment-addendum-2026-05-06.md`
- Move: `docs/milestones/M7_M7_5_TO_M8_HANDOFF_2026-05-03.md`
- Modify: docs that should stay active with split notes.

- [ ] **Step 1: Search for stale education/content direction**

Run:

```bash
cd /home/kyle/profusion
rg -n "short-form educational|education_reform|Attention Intelligence|Substack|MoneyPrinterTurbo|MoneyPrinterV2|content measurement|owned media|M8 has not started|M8 remains deferred" docs README.md STATUS.md DECISIONS.md pyproject.toml
```

Expected: hits are reviewed one by one.

- [ ] **Step 2: Archive known stale bridge docs**

Run:

```bash
cd /home/kyle/profusion
git mv docs/profusion-m7-m8-status-review-2026-05-06.md docs/archive/2026-05-17-project-split/profusion-m7-m8-status-review-2026-05-06.md
git mv docs/profusion-m75-m8-workflow-receipt-simulator-handoff.md docs/archive/2026-05-17-project-split/profusion-m75-m8-workflow-receipt-simulator-handoff.md
git mv docs/profusion-m775-implementation-alignment-addendum-2026-05-06.md docs/archive/2026-05-17-project-split/profusion-m775-implementation-alignment-addendum-2026-05-06.md
git mv docs/milestones/M7_M7_5_TO_M8_HANDOFF_2026-05-03.md docs/archive/2026-05-17-project-split/M7_M7_5_TO_M8_HANDOFF_2026-05-03.md
```

Expected: older bridge/status handoffs are preserved in the split archive instead of remaining active guidance.

- [ ] **Step 3: Add supersession notes to docs that stay active**

Use this note at the top of active historical docs:

```markdown
> 2026-05-17 split note: Profusion is now the B2B workflow-trust project. Education/content operations, MPT/V2 tooling, Substack publishing, source packs, voice guides, and owned-media drafts belong to `/home/kyle/attention-media-lab`. This document remains for historical or narrow implementation context only.
```

- [ ] **Step 4: Commit drift pass**

Run:

```bash
cd /home/kyle/profusion
git add docs README.md STATUS.md DECISIONS.md pyproject.toml
git commit -m "docs: reconcile split-era roadmap language"
```

Expected: no docs are deleted; outdated docs are archived.

## Task 8: Full Verification And Final Status Report

**Files:**
- Inspect: `/home/kyle/profusion`
- Inspect: `/home/kyle/attention-media-lab`

- [ ] **Step 1: Run Profusion backend and cockpit verification**

Run:

```bash
cd /home/kyle/profusion
uv run pytest -q
uv run profusion smoke --offline
git diff --check
cd /home/kyle/profusion/apps/operator-cockpit
corepack pnpm test
corepack pnpm lint
```

Expected:

```text
all Python tests pass
offline smoke passes
git diff --check passes
cockpit tests pass
cockpit lint passes
```

- [ ] **Step 2: Verify Profusion command boundary**

Run:

```bash
cd /home/kyle/profusion
uv run profusion --help
uv run profusion measure --help
```

Expected:

```text
measure command is present
substack command is absent
render/publish are marked legacy/demo-only if still present
```

- [ ] **Step 3: Verify Attention Media Lab import**

Run:

```bash
cd /home/kyle/attention-media-lab
git status --short
test -d vendor/MoneyPrinterTurbo
test -d vendor/MoneyPrinterV2
test -f README.md
test -f docs/PROJECT_ORIGIN_2026-05-17.md
```

Expected:

```text
git status is clean
MoneyPrinterTurbo exists
MoneyPrinterV2 exists
README exists
origin note exists
```

- [ ] **Step 4: Verify Profusion dirty tree is clean or intentionally documented**

Run:

```bash
cd /home/kyle/profusion
git status --short
```

Expected: either clean, or remaining files are explicitly listed in the final report with owner and reason.

- [ ] **Step 5: Final report to Kyle**

Report in this format:

```text
Done:
- Created /home/kyle/attention-media-lab and imported MPT/V2 plus education/content assets.
- Archived outdated Profusion docs under docs/archive/2026-05-17-project-split.
- Reframed Profusion around B2B workflow trust.
- Kept M8 as generic workflow outcome observations.

Blocked:
- None.

Next:
- Review the split decision and run one focused follow-up pass on legacy render/publish removal after fixture-backed demo receipts are sufficient.

Approval needed:
- None unless a public website, Substack, email, or external publication action is requested.
```

## Self-Review Notes

- Spec coverage: includes project split, new repo creation, MPT/V2 preservation, Profusion B2B reframing, M8 generic measurement, archive-not-delete rule, and verification.
- Placeholder scan: passed; the plan contains no open implementation placeholders.
- Scope check: this plan is large but sequential. It avoids deep removal of legacy render/publish code until after extraction, preserving safety.
- Risk note: the plan intentionally deprecates live MPT/V2 paths in Profusion before removing them. Full removal should be a later plan after fixture-backed demo receipts are enough for Profusion.
