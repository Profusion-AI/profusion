# M7 Cockpit Visual Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port `docs/M7 Operator Cockpit.html` into the existing `apps/operator-cockpit` React app while preserving Vite routing, read-model hooks, static Netlify `/api/*` snapshots, and conservative command presentation.

**Architecture:** Add a view-model layer that derives operator metrics, filters, row fields, and item-detail sections from the existing API payloads. Replace the rough Tailwind shell/pages with the artifact's dense internal cockpit layout: narrow icon rail, matte workbench palette, metrics strip, queue table, detail panels, approvals/evidence/system/log views, and command copy visibility. Keep mutations out of broad UI actions.

**Tech Stack:** React 19, Vite, TypeScript, Vitest, Tailwind CSS v4, Netlify static deploy.

---

### Task 1: View Models

**Files:**
- Create: `apps/operator-cockpit/src/domain/cockpitViewModel.ts`
- Create: `apps/operator-cockpit/src/domain/cockpitViewModel.test.ts`

- [ ] Write failing Vitest coverage for deriving queue rows, metrics, filters, and command classifications from real API-shaped payloads.
- [ ] Run `cd apps/operator-cockpit && corepack pnpm test -- src/domain/cockpitViewModel.test.ts` and verify the missing module failure.
- [ ] Implement the view-model helpers without changing API contracts.
- [ ] Re-run the targeted test and keep existing domain tests green.

### Task 2: Visual System

**Files:**
- Modify: `apps/operator-cockpit/src/index.css`
- Modify: `apps/operator-cockpit/src/components/queue/StatusBadge.tsx`
- Create: `apps/operator-cockpit/src/components/cockpit/CockpitBadge.tsx`
- Create: `apps/operator-cockpit/src/components/cockpit/MetricStrip.tsx`
- Create: `apps/operator-cockpit/src/components/cockpit/OperatorTable.tsx`
- Create: `apps/operator-cockpit/src/components/cockpit/CommandBlock.tsx`

- [ ] Port the artifact palette and dense operator typography into CSS variables and reusable classes.
- [ ] Replace the old slate badge treatment with artifact-style dot badges.
- [ ] Add reusable metric, table, and command components that consume the Task 1 view models.

### Task 3: Route Shell and Pages

**Files:**
- Modify: `apps/operator-cockpit/src/components/layout/Shell.tsx`
- Modify: `apps/operator-cockpit/src/pages/QueuePage.tsx`
- Modify: `apps/operator-cockpit/src/pages/ItemPage.tsx`
- Modify: `apps/operator-cockpit/src/pages/LogsPage.tsx`
- Create: `apps/operator-cockpit/src/pages/FailuresPage.tsx`
- Create: `apps/operator-cockpit/src/pages/ApprovalsPage.tsx`
- Create: `apps/operator-cockpit/src/pages/EvidencePage.tsx`
- Create: `apps/operator-cockpit/src/pages/SystemPage.tsx`
- Modify: `apps/operator-cockpit/src/router.tsx`

- [ ] Replace the horizontal header with the artifact's narrow side rail and top status bar.
- [ ] Rebuild `/queue` with metrics, filters/search, dense table, and next-safe-command visibility.
- [ ] Rebuild `/items/:id` with artifact-style detail sections for timeline/jobs, artifacts, approvals, logs, handoff, and next safe command.
- [ ] Add secondary routes for failures, approvals, evidence, system, and keep `/logs`.

### Task 4: Verification and Deploy

**Files:**
- Modify as needed: `apps/operator-cockpit/package.json`, `apps/operator-cockpit/pnpm-lock.yaml`
- Modify: `docs/milestones/M7_OPERATOR_COCKPIT_SMOKE_2026-05-03.md`

- [ ] Run `cd apps/operator-cockpit && corepack pnpm test`.
- [ ] Run `cd apps/operator-cockpit && corepack pnpm lint`.
- [ ] Run `cd apps/operator-cockpit && corepack pnpm build:netlify`.
- [ ] Start a local preview and inspect desktop/mobile with browser screenshots.
- [ ] Deploy a new Netlify draft for the cockpit app only, then verify `/queue`, `/api/queue`, and an item detail endpoint.
- [ ] Update the M7 smoke doc with the new deploy URL and the preserved static-preview boundary.
