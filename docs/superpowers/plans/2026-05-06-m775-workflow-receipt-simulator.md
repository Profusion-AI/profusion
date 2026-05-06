# M7.75 Workflow Receipt Simulator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a content-first, claim-bounded Workflow Receipt Simulator plus buyer-readable pilot collateral without starting M8.

**Architecture:** Add a static, deterministic simulator to the active public `dashboard/` app while keeping the operator cockpit internal. The simulator uses local fixtures and pure TypeScript transformation logic, never live APIs or receipt lifecycle mutation. Buyer collateral lives under `docs/` and explains the offer without requiring repo or cockpit knowledge.

**Tech Stack:** React 19, Vite, TypeScript, Node built-in test runner for pure simulator logic, Markdown collateral.

---

## Scope Decisions

- AI-assisted content/media governance owns the next two-week wedge.
- Homepage narrative may continue signaling the agentic engineering frontier.
- Implemented proof remains `content_video_receipt` in `media_trust`.
- Coding-agent output review and contractor readiness are simulated examples only.
- Current demo receipt remains `draft`.
- M8 measurement loops remain deferred.

## Files

- Create: `dashboard/src/domain/workflowReceiptSimulator.ts`
- Create: `dashboard/src/data/workflowReceiptTemplates.ts`
- Create: `dashboard/src/pages/WorkflowReceiptSimulator.tsx`
- Create: `dashboard/scripts/workflowReceiptSimulator.test.ts`
- Create: `dashboard/tsconfig.test.json`
- Modify: `dashboard/package.json`
- Modify: `dashboard/src/App.tsx`
- Modify: `dashboard/src/index.css`
- Modify: `netlify.toml`
- Create: `docs/offers/governed-ai-workflow-receipt-pilot.md`
- Create: `docs/offers/workflow-reliability-session.md`
- Create: `docs/checklists/evidence-boundary-worksheet.md`
- Create: `docs/checklists/receipt-review-checklist.md`
- Create: `docs/samples/sample-ai-assisted-content-workflow-receipt.md`
- Create: `docs/simulator/workflow-receipt-simulator-fixtures.md`
- Create: `docs/profusion-m775-implementation-alignment-addendum-2026-05-06.md`

## Tasks

### Task 1: Simulator Domain Red Test

- [ ] Add a Node test that imports `buildWorkflowReceiptSimulation` and fixture templates.
- [ ] Assert the content template is labeled `Current sample`.
- [ ] Assert the coding-agent template is labeled `Simulated example`.
- [ ] Assert generated receipts include supported claims, unsupported claims, evidence boundaries, and limitations.
- [ ] Run `cd dashboard && corepack pnpm test:simulator`; expected first result is failure because the domain files do not exist yet.

### Task 2: Simulator Domain Implementation

- [ ] Add typed simulator models and deterministic fixture templates.
- [ ] Add `buildWorkflowReceiptSimulation(input, template)` that returns a workflow map, business value brief, evidence boundary, artifact trail, receipt preview, limitations, and CTA metadata.
- [ ] Run `cd dashboard && corepack pnpm test:simulator`; expected result is pass.

### Task 3: Static Public-Site Route

- [ ] Add `WorkflowReceiptSimulator.tsx` using the domain model and fixtures.
- [ ] Route `/workflow-receipt-simulator` and `/simulator` inside the active `App.tsx` entrypoint without reviving stale operator-dashboard routes.
- [ ] Keep the route unlinked from the main nav by default, but add a bounded hero CTA or secondary link only if it is clearly preview/sample language.
- [ ] Label templates as `Current sample`, `Simulated example`, or `Future integration concept`.
- [ ] Avoid claims of production coding-agent instrumentation, live MCP capture, compliance certification, correctness validation, autonomous governance, or hiring automation.

### Task 4: Buyer-Readable Collateral

- [ ] Create the pilot offer one-pager.
- [ ] Create the Workflow Reliability Session one-pager.
- [ ] Create an evidence boundary worksheet.
- [ ] Create a receipt review checklist.
- [ ] Create the sample AI-assisted content workflow receipt.
- [ ] Create the simulator fixtures note.
- [ ] Create an implementation-alignment addendum distinguishing strategic narrative from shipped proof.

### Task 5: Verification

- [ ] Run `cd dashboard && corepack pnpm test:simulator`.
- [ ] Run `cd dashboard && corepack pnpm lint`.
- [ ] Run `cd dashboard && corepack pnpm build`.
- [ ] Run `uv run pytest`.
- [ ] Run `uv run profusion smoke --offline`.
- [ ] Run operator-cockpit regression checks if time permits: `corepack pnpm test`, `corepack pnpm lint`, `corepack pnpm build:netlify`, and `corepack pnpm smoke:static`.

## Acceptance Criteria

- The simulator default is AI-assisted content approval.
- Secondary templates are clearly simulated.
- Simulator output includes workflow map, business value, evidence boundary, artifact trail, receipt preview, limitations, and Workflow Reliability Session CTA.
- No live backend writes, login, customer portal, receipt transition, MCP integration, Work Trust runner, AI observability, or M8 measurement loop is introduced.
- Buyer collateral can be read without understanding cockpit, SQLite, FastAPI, CLI lifecycle, or M7.5.
- Current receipt remains `draft`.
