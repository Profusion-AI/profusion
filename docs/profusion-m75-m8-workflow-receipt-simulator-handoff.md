# Profusion M7.75 Handoff — Workflow Receipt Simulator Bridge

**Date:** 2026-05-06  
**Intended recipients:** Codex, Claude Code, and Kyle  
**Purpose:** Bridge the gap between the verified M7/M7.5 implementation reality and the proposed customer-facing Workflow Receipt Simulator, without prematurely starting M8 or over-claiming engineering/coding-agent reliability capabilities.

---

## 1. Executive verdict

Profusion should not start M8 yet.

The next execution milestone should be treated as **M7.75: Workflow Receipt Simulator + Pilot Operating Kit**.

The reason is simple: M7 and M7.5 prove that Profusion can operate a governed internal content workflow and generate a file-first receipt packet, but the business still needs a sales-ready demonstration that a prospect can understand without learning the cockpit, FastAPI, SQLite, milestone history, or terminal lifecycle commands.

The bridge milestone should turn the existing M7.5 evidence slice into a controlled customer-facing demonstration:

> A prospect chooses one simulated AI-assisted workflow, Profusion maps the workflow into actors, AI touchpoints, artifacts, review gates, risk points, business value, and receipt boundaries, then generates a sample receipt showing what happened, what evidence exists, what humans reviewed, and what the receipt does not prove.

This is not M8. This is the commercial bridge between “we built an internal cockpit and a draft receipt” and “a buyer understands why this matters enough to discuss a pilot.”

---

## 2. Source-grounded reality check

### What is verified now

The latest status review says Profusion is between M7.5 closeout and M8 start. M7 is complete as an internal operator cockpit baseline, M7.5 has a first evidence slice for the current content workflow, and M8 should not start until the receipt packet is reviewed, advanced through lifecycle, and used as a selling or reviewer artifact. Source anchor: `profusion-m7-m8-status-review-2026-05-06.md`, lines 31–37.

Fresh verification also passed: Python tests, smoke test, dashboard lint/build, cockpit test/lint/build, cockpit static smoke, production homepage HTTP 200, Netlify draft queue HTTP 200, and the demo receipt API returning one draft `content_video_receipt`. Source anchor: `profusion-m7-m8-status-review-2026-05-06.md`, lines 41–64.

M7 is verified as an internal cockpit with queue, item detail, jobs/failures, artifacts, approvals, logs, handoff, evidence views, next safe command presentation, and read-only static preview export. It is explicitly not buyer-facing. Source anchor: `profusion-m7-m8-status-review-2026-05-06.md`, lines 66–84.

M7.5 has the `content_video_receipt` generator, packet files, CLI lifecycle commands, receipt API route, cockpit evidence visibility, and static receipt JSON export. The current demo receipt is still `draft`, with `receipt_type: content_video_receipt`, `trust_domain: media_trust`, and `subject_id: m75-demo-content-video-receipt`. Source anchor: `profusion-m7-m8-status-review-2026-05-06.md`, lines 86–117.

M8 has not started. The planned M8 scope remains content measurement and learning loops, and it should stay deferred unless a buyer conversation proves measurement is the blocker, the current media receipt packet has been reviewed and used externally, or a signed/near-signed pilot requires measurement. Source anchor: `profusion-m7-m8-status-review-2026-05-06.md`, lines 119–137.

### What the strategic docs already say

The business-plan guidance says Profusion is platform-shaped but should not yet be sold as a platform. The public B2B product should be a founder-led **Governed AI Workflow Receipt Pilot**: pick one high-risk AI-assisted workflow, define the evidence boundary, capture artifacts, apply review gates, and produce a reviewer-readable receipt that says what happened, who reviewed it, and what it does not prove. Source anchor: `Profusion AI Business Plan.txt`, lines 1–9.

The same business-plan guidance separates the terms cleanly: company category is workflow trust infrastructure, current public B2B offer is the Governed AI Workflow Receipt Pilot, current internal/private demo surface is operator cockpit plus receipt lifecycle, and first proven receipt mode is AI media/content workflow evidence. Source anchor: `Profusion AI Business Plan.txt`, lines 17–29.

The strongest near-term pilot is the **AI-Assisted Content Workflow Receipt**, because the existing Profusion content workflow can already demonstrate lifecycle state, artifacts, QA, approval, publishing readiness, retry, and receipt generation. Source anchor: `Profusion AI Business Plan.txt`, lines 270–288.

The lead-gen guidance says Profusion’s category should remain workflow evidence and receipting for high-risk AI-assisted work. Agentic workflows are a use case, MCP is an integration mechanism, output mediation is the product behavior, and receipts are the buyer-readable artifact. Source anchor: `Lead Gen Strategy for Profusion.txt`, lines 221–243.

The content-pipeline PRD says the first release should optimize for reliability, auditability, and operator control, not raw throughput, and should expose a clean state machine so a human can intervene without losing context. Source anchor: `profusion-content-pipeline-prd.md`, lines 11–27.

---

## 3. The core gap to reconcile

There are two realities that must be held together without hand-waving.

**Implementation reality:** Profusion currently proves media/content workflow evidence through a `content_video_receipt`. It does not yet prove coding-agent diffs, tests, PR review, CI results, verification tax, review burden, or production-change reliability.

**Positioning reality:** The homepage now foregrounds the broader productivity-reliability gap, including coding-agent and agentic engineering review.

The answer is not to panic-build M8, not to over-build agent observability, and not to pretend the current repo proves engineering reliability. The answer is to create a **bounded simulator** that demonstrates the general receipt kernel while being honest about what has shipped.

The repeatable kernel is:

```text
workflow boundary
→ evidence map
→ captured artifacts
→ human review gates
→ review decision
→ limitations
→ receipt packet
```

The simulator should make that kernel obvious.

---

## 4. Decision: which wedge owns the next two weeks?

**Recommended decision:** AI-assisted media/content governance owns the next two-week execution wedge.

Why: it is closest to implemented product evidence. The existing receipt mode, cockpit evidence view, and file-first packet all support a media/content receipt today. Coding-agent reliability remains a valid positioning hypothesis and future sample path, but it should not own execution unless Kyle explicitly chooses to build a sanitized engineering reliability sample receipt before outreach.

**Practical translation:**

1. Use media/content governance as the first real sample receipt and customer-facing demo path.
2. Include coding-agent reliability as a simulated template only if clearly labeled as a future/synthetic example.
3. Do not claim live coding-agent integrations, PR review capture, CI capture, MCP integration, or engineering receipt generation until a purpose-built fixture or generator exists.
4. Keep the homepage category broad, but ensure any prospect conversation starts with one concrete workflow and one receipt packet.

---

## 5. Workflow Reliability Session vs Simulator vs Pilot vs Cockpit

These are not the same thing. Codex should preserve the separation.

| Term | Owner | User-facing? | Purpose | Status |
|---|---|---:|---|---|
| **Workflow Reliability Session** | Kyle / sales motion | Yes | Discovery call or diagnostic review. Prospect brings one workflow; Profusion identifies evidence boundary, risks, review gates, and pilot fit. | Lead-capture offer. |
| **Workflow Receipt Simulator** | Public site | Yes | Controlled, simulated environment where a prospect can see the receipt mechanism using fake/sanitized data. | New M7.75 deliverable. |
| **Governed AI Workflow Receipt Pilot** | Founder-led delivery | Yes, but not self-serve | Paid or design-partner engagement using one real workflow, real evidence boundary, real artifacts, and a reviewer-readable receipt packet. | Current public B2B offer. |
| **Operator Cockpit** | Profusion internal ops | No, except narrated preview/screenshots | Internal mission-control surface for queue, artifacts, approvals, logs, handoff, evidence, and receipt lifecycle. | M7 complete baseline. |
| **M8 Measurement Loops** | Product roadmap | No | Content measurement imports/read models and learning loops after receipt value is proven. | Deferred. |

The lead-capture section at the bottom of the site should route to the **Workflow Reliability Session**, not directly to a pilot and not directly to the internal cockpit. The simulator should support that CTA by giving the buyer something concrete to understand before the call.

---

## 6. Workflow Receipt Simulator — rough PRD reconciled to repo reality

### Product name

**Workflow Receipt Simulator**

### Public positioning

```text
Try a simulated workflow receipt.
Choose one AI-assisted workflow and see how Profusion turns it into reviewable evidence: actors, artifacts, review gates, risks, business value, and a bounded receipt.
```

### Primary user

A prospect evaluating whether Profusion’s receipt model makes sense for one of their workflows. This user may be a founder, operator, content lead, AI governance lead, recruiting operations lead, automation consultant, or technical buyer.

### Primary promise

The simulator should answer:

```text
What does Profusion actually do to a workflow?
What business value does the receipt provide?
What evidence is captured?
What does the receipt prove, and what does it not prove?
How is this different from a dashboard or generic AI policy document?
```

### Available workflow templates for M7.75

Use controlled templates, not a blank canvas.

**Template 1 — AI-Assisted Content Approval**  
This should be the default and should map to the current `content_video_receipt` implementation. It demonstrates: topic/brief, script, render, QA, human approval, schedule/publish status, artifact pointers, evidence sources, and limitations.

**Template 2 — Coding-Agent Output Review, simulated**  
This is allowed only as a clearly labeled simulated/future template. It should not claim production integration. It can show what an engineering receipt would eventually include: task brief, agent output, changed files, tests requested, review notes, approval context, limitations, and unsupported claims. Do not include real Codex/Claude/Gemini integration claims.

**Template 3 — AI-Mediated Contractor Readiness, simulated**  
This is optional. It should avoid hiring decision language. It can show observed work behavior, artifacts reviewed, human notes, strengths, risks, and limitations. It must not rank candidates, recommend hire/no-hire, or imply automated employment decisioning.

### Required simulator flow

1. **Choose a workflow template.**
2. **Enter lightweight context.** Examples: business goal, audience/client, AI tools involved, output type, risk if wrong, human reviewer role.
3. **Show workflow breakdown.** Include workflow goal, actors, AI touchpoints, artifacts, review gates, risk points, business value, supported claims, unsupported claims.
4. **Show simulated evidence capture.** Display fake/sanitized artifacts such as prompt log, AI output, QA checklist, human review note, approval decision, limitation note, and final deliverable pointer.
5. **Generate sample receipt preview.** Present a reviewer-readable receipt with evidence boundary, artifacts captured, AI tools involved, review gates applied, human reviewer role, QA outcome, decision, supported claims, limitations, and recommended next controls.
6. **Call to action.** Route to “Book a Workflow Reliability Session” with the selected template and generated context prefilled if technically simple.

### Required output panels

The simulator should produce these panels:

1. **Workflow Map** — actors, AI touchpoints, artifacts, review gates.
2. **Business Value Brief** — trust value, operational value, risk value, differentiation value.
3. **Evidence Boundary** — what is inside the receipt and what is outside it.
4. **Simulated Artifact Trail** — fake/sanitized artifacts with labels.
5. **Receipt Preview** — plain-English sample receipt.
6. **Limitations** — what the receipt does not prove.
7. **Next Step** — Workflow Reliability Session CTA.

### Required receipt language

Use careful language:

```text
Sample Workflow Receipt
Evidence available
Human review recorded
QA checkpoint applied
Limitations included
Supported claim
Unsupported claim
Outside receipt boundary
```

Avoid overclaiming:

```text
Certified
Verified truth
Compliant
Approved by Profusion
Risk-free
Hiring recommendation
Candidate ranking
Autonomous compliance
Production integration
```

### Customer-facing vs internal boundaries

The public simulator may show simulated receipt logic, sample artifacts, and a receipt preview.

It must not expose:

- internal cockpit routes as a customer portal,
- live queue data,
- mutable receipt lifecycle commands,
- raw production logs,
- client data stores,
- real customer artifacts,
- private prompts,
- live publishing commands,
- real coding-agent/MCP integration claims.

---

## 7. Recommended implementation architecture

### Keep it static-first

The simulator should be implemented as a static/read-only public-site feature first, most likely in the public `dashboard/` app rather than the internal `apps/operator-cockpit/` app.

Recommended route names:

```text
/workflow-receipt-simulator
/sample-receipt
/workflow-reliability-session
```

Do not build login, portal, hosted mutable backend, billing, external reviewer queue, live receipt lifecycle, MCP integration, Work Trust runner, or measurement loops for this milestone.

### Suggested file structure

```text
dashboard/src/pages/WorkflowReceiptSimulator.tsx
dashboard/src/pages/SampleReceipt.tsx
dashboard/src/data/workflowReceiptTemplates.ts
dashboard/src/domain/workflowReceiptSimulator.ts
dashboard/src/components/receipt/WorkflowMap.tsx
dashboard/src/components/receipt/BusinessValueBrief.tsx
dashboard/src/components/receipt/EvidenceBoundary.tsx
dashboard/src/components/receipt/ArtifactTrail.tsx
dashboard/src/components/receipt/ReceiptPreview.tsx
dashboard/src/components/receipt/LimitationsPanel.tsx
docs/offers/workflow-reliability-session.md
docs/offers/governed-ai-workflow-receipt-pilot.md
docs/simulator/workflow-receipt-simulator-prd.md
docs/samples/sample-content-video-workflow-receipt.md
docs/checklists/receipt-review-checklist.md
docs/checklists/pilot-intake-checklist.md
```

### Suggested TypeScript domain model

```ts
export type WorkflowTemplateId =
  | "content_approval"
  | "coding_agent_review_simulated"
  | "contractor_readiness_simulated";

export interface WorkflowSimulatorInput {
  templateId: WorkflowTemplateId;
  businessGoal: string;
  outputType: string;
  audienceOrReviewer: string;
  aiTouchpoints: string[];
  riskIfWrong: string;
  humanReviewerRole: string;
}

export interface WorkflowBreakdown {
  workflowGoal: string;
  actors: string[];
  aiTouchpoints: string[];
  artifacts: ReceiptArtifact[];
  reviewGates: ReviewGate[];
  riskPoints: string[];
  businessValue: BusinessValueBrief;
  supportedClaims: string[];
  unsupportedClaims: string[];
  evidenceBoundary: EvidenceBoundary;
}

export interface ReceiptArtifact {
  id: string;
  label: string;
  artifactType: string;
  simulated: boolean;
  description: string;
}

export interface ReviewGate {
  id: string;
  label: string;
  reviewerRole: string;
  decision: "not_started" | "passed" | "failed" | "needs_review" | "simulated_passed";
  notes: string;
}

export interface BusinessValueBrief {
  trustValue: string;
  operationalValue: string;
  riskValue: string;
  differentiationValue: string;
}

export interface EvidenceBoundary {
  insideReceipt: string[];
  outsideReceipt: string[];
  limitations: string[];
}
```

### Use fixtures, not live APIs

For M7.75, the simulator should use deterministic fixtures. It may display one generated sample receipt based on user selections, but it should not mutate real receipt state or call internal receipt APIs.

If the current `content_video_receipt` sample is used, sanitize and copy it into a static sample fixture. Do not fetch live internal data from the cockpit preview.

---

## 8. Demo receipt lifecycle guidance

The current demo receipt should not be moved from `draft` to `reviewed` or `approved_for_packet` just because the command works.

Advance it only if Kyle reviews the packet language and confirms:

1. The receipt is understandable without explaining the cockpit.
2. The limitations are clear and not buried.
3. The receipt does not imply certification, compliance, truth verification, or production-grade audit.
4. Artifact pointers are readable enough for a prospect or reviewer.
5. The receipt identifies what is inside and outside the evidence boundary.
6. The receipt makes the business value legible.
7. The receipt supports the intended first wedge: AI-assisted media/content governance.

Recommended lifecycle commands, after review:

```bash
uv run profusion receipt list --item-id m75-demo-content-video-receipt --json
uv run profusion receipt transition --receipt-id <receipt_id> --to reviewed --json
uv run profusion receipt transition --receipt-id <receipt_id> --to approved_for_packet --json
```

If the packet is not sales-ready, leave it as `draft`, create a separate `sample-content-video-workflow-receipt.md`, and do not mark the real receipt as reviewed.

---

## 9. First prospect packet

The first prospect should not receive the cockpit as the primary artifact.

Recommended pre-call packet:

1. **One-page sample workflow receipt** — public/readable, no cockpit explanation required.
2. **Pilot scope one-pager** — what the Governed AI Workflow Receipt Pilot includes, excludes, and produces.
3. **Workflow Reliability Session worksheet** — one page asking the prospect to bring a workflow, owner, AI touchpoints, risk, existing artifacts, and reviewer role.
4. **Optional cockpit preview screenshot or short narrated clip** — use only as credibility evidence, not as the product.
5. **Optional simulator link** — static, controlled, fake/sanitized data.

The cockpit preview is useful to show internal discipline, but the sale is the receipt and the governed pilot, not a dashboard.

---

## 10. Homepage/product positioning guardrail

The homepage can continue using productivity-reliability language only if the repo makes the capability boundary explicit.

Recommended public framing:

```text
Profusion turns AI-assisted workflows into reviewable evidence.

We start with one workflow: define the boundary, capture artifacts, apply review gates, and generate a plain-English receipt showing what happened, what was reviewed, and what the receipt does — and does not — prove.
```

Recommended caveat for coding-agent reliability language:

```text
For coding-agent and agentic workflows, Profusion is developing receipt patterns for agent outputs, review checkpoints, and approval context. Current public samples are simulated unless marked otherwise.
```

Do not claim:

```text
Profusion has production coding-agent reliability instrumentation.
Profusion integrates with Codex, Claude Code, Gemini, or MCP.
Profusion performs agent observability.
Profusion validates code correctness.
Profusion certifies AI work.
```

The category should stay **workflow evidence and receipts**, not AI observability.

---

## 11. M8 interpretation

Do not reinterpret M8 silently.

Current M8 remains:

```text
content measurement loops
manual/file-first measurement imports
item-level and aggregate measurement read models
CLI commands for observations
published → measured transition
cockpit visibility after read-model behavior is tested
```

If buyer conversations prove that “measurement” now means reliability measurement across AI workflows rather than content metrics, create a new roadmap decision before building. Suggested naming:

```text
M8A — Content Measurement Loops
M8R — Workflow Reliability Measurement
```

Until then, the next milestone is M7.75, not M8.

---

## 12. Open-source recommendation

Yes, Profusion can open-source part of this business to reinforce trust, but only the trust primitive.

Recommended open-source candidates:

```text
schemas/workflow-receipt.schema.json
examples/content-approval-receipt.example.json
examples/coding-agent-receipt.simulated.example.json
examples/contractor-readiness-receipt.simulated.example.json
docs/receipt-vocabulary.md
docs/receipt-limitations-guide.md
static-demo/workflow-receipt-simulator/
```

Do not open-source yet:

```text
internal operator cockpit
production receipt lifecycle code
client-specific receipt generation logic
private prompts
customer artifacts
production data stores
security-sensitive adapters
MoneyPrinterV2-coupled code without legal review
```

The open-source story should be:

> We make the receipt structure and limitation language transparent. Our paid work is applying it to real workflows, capturing the right evidence, and helping teams create reviewer-readable packets.

This gives credibility without giving away the commercial operating system.

---

## 13. Codex execution order

### Step 0 — Preserve the current verified state

Before new work, inspect `git status`. The M7/M7.5 worktree is broad and dirty according to the status review. Do not start simulator work until the current boundary is documented or committed.

Minimum action:

```bash
git status --short
```

Then recommend a commit split or handoff boundary. Do not accidentally conflate cockpit, receipt lifecycle, homepage copy, and simulator work.

### Step 1 — Review the draft demo receipt

Inspect the current packet:

```text
data/receipts/content-video-m75-demo-con-20260503T155812Z-ceb13ddd/
```

Review:

```text
receipt.md
summary.md
limitations.md
reviewer_notes.md
evidence.json
```

Apply the checklist in Section 8. Either keep as `draft` or transition only after Kyle-level review.

### Step 2 — Create sales-ready sample receipt

Create a standalone sample that can be read without cockpit context:

```text
docs/samples/sample-content-video-workflow-receipt.md
```

It should include:

```text
Workflow name
Business context
Evidence boundary
Artifacts captured
Review gates
Human review role
QA result
Approval status
Supported claims
Unsupported claims
Limitations
Recommended next controls
```

### Step 3 — Create the pilot operating kit

Create:

```text
docs/offers/workflow-reliability-session.md
docs/offers/governed-ai-workflow-receipt-pilot.md
docs/checklists/pilot-intake-checklist.md
docs/checklists/evidence-boundary-worksheet.md
docs/checklists/receipt-review-checklist.md
```

### Step 4 — Build static simulator route

Implement a deterministic, fixture-backed simulator in the public site. Default to content approval. Mark non-content templates as simulated.

### Step 5 — Add CTA linkage

The simulator should end with:

```text
Book a Workflow Reliability Session
Bring one workflow. We’ll identify the evidence boundary, review gates, artifacts, and receipt opportunity.
```

This is the lead capture. It is not the pilot itself.

### Step 6 — Optional: add simulated engineering sample

Only if the homepage continues to foreground coding-agent reliability, add a static sample receipt fixture:

```text
docs/samples/sample-coding-agent-workflow-receipt.simulated.md
```

Label clearly:

```text
Simulated example. Not generated from a live coding-agent integration.
```

### Step 7 — Run verification

Expected checks after implementation:

```bash
uv run pytest
uv run profusion smoke --offline
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm build:netlify
cd apps/operator-cockpit && corepack pnpm smoke:static
```

If only the public site changed, cockpit checks can still be run as regression protection.

---

## 14. Acceptance criteria for M7.75

M7.75 is complete when all of the following are true:

1. Current M7/M7.5 worktree boundary is documented or committed.
2. Current demo receipt has been reviewed and either kept as draft or deliberately advanced.
3. A sales-ready sample content/video workflow receipt exists and is understandable without cockpit context.
4. A pilot operating kit exists: intake, evidence boundary worksheet, receipt-review checklist, and pilot scope.
5. A static Workflow Receipt Simulator exists on the public site or as a draft Netlify route.
6. Simulator includes default AI-assisted content approval template.
7. Any coding-agent or contractor-readiness template is clearly labeled simulated.
8. Simulator produces a workflow map, business value brief, evidence boundary, artifact trail, receipt preview, limitations, and CTA.
9. CTA routes to Workflow Reliability Session, not directly to pilot or cockpit.
10. Internal cockpit remains internal and is not reframed as a customer portal.
11. Homepage/product copy does not imply shipped coding-agent receipt generation or MCP integration.
12. M8 remains deferred unless a buyer conversation makes measurement the blocker.
13. Tests/build/smoke pass or failures are documented with exact blockers.

---

## 15. Codex handoff prompt

Use this prompt in Codex:

```text
You are reviewing and bridging Profusion between M7.5 closeout and M8 start.

Read the latest status review and this M7.75 handoff before making changes.

Your job is not to start M8. Your job is to create the commercial bridge between the existing M7.5 content_video_receipt evidence slice and a customer-facing Workflow Receipt Simulator / pilot operating kit.

Ground truth:
- M7 is complete as an internal operator cockpit.
- M7.5 has a file-first content_video_receipt generator, CLI lifecycle, receipt API, cockpit evidence visibility, and static preview.
- The current demo receipt is still draft.
- M8 measurement loops have not started and should remain deferred unless buyer signal proves measurement is the blocker.
- The public site has moved toward productivity-reliability/coding-agent language, but the implementation still proves media/content workflow evidence.

Your tasks:
1. Inspect git status and document the current worktree boundary.
2. Review the draft demo receipt packet and recommend whether it stays draft or advances to reviewed / approved_for_packet.
3. Create a sales-ready sample content/video workflow receipt that can be read without cockpit context.
4. Create the pilot operating kit: Workflow Reliability Session, Governed AI Workflow Receipt Pilot, intake checklist, evidence-boundary worksheet, receipt-review checklist.
5. Implement or specify a static Workflow Receipt Simulator using deterministic fake/sanitized fixtures.
6. Keep content/media governance as the default live wedge.
7. If adding coding-agent reliability, make it a simulated sample only and clearly label it as not generated from live integration.
8. Do not build login, customer portal, hosted mutable backend, MCP integration, Work Trust runner, measurement loops, or AI observability.
9. Preserve internal cockpit boundaries.
10. Run the relevant tests/build/smoke checks and summarize results.

Acceptance target:
One credible sample receipt packet plus one controlled simulator path that can support a serious buyer conversation.
```

---

## 16. Final strategic instruction

Do not let the next sprint become vague platform work.

The target is not “M8 shipped.”

The target is:

```text
One credible receipt packet.
One controlled workflow simulator.
One pilot operating kit.
One serious buyer conversation.
```

That is the bridge from build reality to market reality.
