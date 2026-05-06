# Profusion Homepage Launch Handoff

Date: 2026-05-05

Primary reference docs for the next conversation:

- `docs/profusion-zero-to-one-plan-2026-05-05.md`
- `docs/current-copy-splash.md`
- This handoff: `docs/profusion-homepage-launch-handoff-2026-05-05.md`

## Executive Summary

Profusion's public homepage has been repositioned and deployed to production at
`https://profusion.ai`.

The old synthetic-media-first posture has been replaced with a broader but
still concrete category:

> AI workflow trust: reviewable evidence for high-risk AI-assisted and agentic
> work.

The homepage now leads with:

> Turn AI-assisted workflows into reviewable evidence.

The page explains the mechanism as workflow mapping, artifact capture, human
review gates, bounded limitations, and plain-English workflow receipts. This is
now aligned with the zero-to-one plan's first commercial offer:

> Profusion Evidence Receipt Pilot: one workflow, one evidence boundary, one
> human review gate, one limitations statement, one reviewer-readable receipt.

## Deployment

Production URL:

- `https://profusion.ai`

Netlify production deploy:

- Site: `profusionai`
- Site ID: `3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e`
- Deploy ID: `69fa11d971f60e40ef9c7669`
- Deploy URL: `https://69fa11d971f60e40ef9c7669--profusionai.netlify.app`
- Deploy logs: `https://app.netlify.com/projects/profusionai/deploys/69fa11d971f60e40ef9c7669`

Deployment command used:

```bash
npx netlify deploy --prod --no-build --dir=dashboard/dist --site=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e --message "Profusion homepage workflow trust launch copy 2026-05-05" --json
```

Note: the first deploy attempt without `--no-build` failed because Netlify CLI
tried to execute `pnpm build` through the local asdf shim. The verified path is
to build locally with `corepack pnpm build` and upload `dashboard/dist` with
`--no-build`.

## What Changed

Primary code/content files:

- `dashboard/src/App.tsx`
- `dashboard/src/index.css`
- `dashboard/public/__forms.html`
- `docs/current-copy-splash.md`

Primary homepage changes:

- Reframed Profusion as an `AI WORKFLOW TRUST PRACTICE`.
- Kept the hero headline at `Turn AI-assisted workflows into reviewable evidence.`
- Replaced abstract/internal phrasing with buyer-facing mechanism language.
- Updated the hero receipt card to use workflow evidence fields:
  - `workflow_id`
  - `evidence_boundary`
  - `artifacts_captured`
  - `review_gate`
  - `claims_supported`
  - `receipt_status`
- Added `HUMAN REVIEWED` as a clearer receipt-card trust signal.
- Added `Bound` as the workflow step for stating what the evidence supports.
- Added agentic workflow language without making the company an agent
  observability platform.
- Added `AGENTIC REVIEW GAP` as a problem-card status.
- Added a future-facing but bounded MCP integration note:

> Profusion adds a receipt layer between agentic work and human approval.
> Planned integration path: Profusion MCP tools for capturing workflow events,
> artifacts, review checkpoints, and receipt metadata from agentic environments.

- Updated Service 03 to:

> AI-Assisted & Agentic Work Review Systems

- Added engineering, product, and AI operations teams using coding agents or
  MCP-connected tools to the ideal-client list.
- Updated the contact form placeholder to include agentic workflows.
- Aligned the static Netlify form skeleton subject with the visible form:
  `Profusion AI workflow trust session request`.

## Verification

Local verification:

```bash
corepack pnpm lint
corepack pnpm build
```

Build output:

```text
dashboard/dist/index.html
dashboard/dist/assets/index-BnxTSp2L.css
dashboard/dist/assets/index-DxQhm8Uy.js
dashboard/dist/__forms.html
```

Live verification:

- `curl -I https://profusion.ai/` returned HTTP 200.
- `https://profusion.ai/` serves the deployed asset bundle:
  - `/assets/index-DxQhm8Uy.js`
  - `/assets/index-BnxTSp2L.css`
- A headless Chrome DOM check against `https://profusion.ai/?deploy=69fa11d971f60e40ef9c7669` confirmed the production page contains:
  - `AGENTIC REVIEW GAP`
  - `Profusion MCP tools`
  - `AI-Assisted & Agentic Work Review Systems`
  - `Briefly describe the AI-assisted or agentic workflow, output, or review problem...`

## Reconciliation With The Zero-To-One Plan

The homepage now supports, rather than distracts from, the zero-to-one plan.

The plan says Profusion should not sell generic AI governance or a mature SaaS
platform. The homepage now avoids that. It sells a concrete mechanism:

```text
workflow boundary -> artifacts -> human review -> limitations -> receipt
```

The plan says the first buyer should buy a bounded evidence packet for one
workflow. The homepage now points every CTA and proof point back to that:

- `Start with One Workflow`
- `Pilot engagements begin with one workflow and one reviewable receipt.`
- `No long-term lock-in. Engagements are scoped around a defined workflow.`

The plan originally names AI-assisted content and synthetic media as the first
commercial wedge. The homepage still supports that wedge, but it now also
acknowledges agentic/coding-agent workflows as a strong adjacent use case. This
is a strategic expansion of the use-case language, not a change to the first
offer.

The correct hierarchy after launch is:

```text
Category: AI workflow trust
Offer: Profusion Evidence Receipt Pilot
Use cases: AI content, synthetic media, recruiting/staffing, client-facing automation, agentic/coding-agent workflow review
Mechanism: artifact capture, human review gates, limitations, receipts
Future integration path: MCP-based evidence capture
Artifact: reviewer-readable workflow receipt
```

Important guardrail: do not let the next conversation turn this into "AI agent
observability." Agentic workflows are a use case. MCP is an integration
mechanism. Receipts and process evidence remain the buyer-facing product.

## Suggested Next Conversation

Use this handoff and `docs/profusion-zero-to-one-plan-2026-05-05.md` as the
starting context.

The next practical work should be one of these:

1. Create the sales-ready sample receipt that Kyle can send before a call.
2. Create the pilot operating kit:
   - `pilot-intake.md`
   - `evidence-boundary-worksheet.md`
   - `receipt-review-checklist.md`
   - `pilot-scope-template.md`
3. Turn the homepage thesis into outbound copy for the first 20 warm or
   semi-warm leads.
4. Build a narrow prospect list around the first buyer profile in the
   zero-to-one plan.

Recommended next move:

> Start with the pilot operating kit and outbound copy. The website now says
> the right thing; the next task is to create the artifacts Kyle needs to have
> serious first-client conversations without improvising the offer from scratch.

## Current Operating Boundary

Do not build before first client unless it directly supports selling, showing,
reviewing, or delivering one receipt packet:

- Customer portal
- Login
- Billing
- Multi-tenant organizations
- External reviewer queue
- Agent observability platform
- Full MCP implementation
- ATS/DAM/GRC integrations
- Compliance certification
- Automated hiring or ranking

The zero-to-one milestone remains:

> One real buyer had one AI-assisted or agentic workflow where the final output
> was not enough, and Profusion made that workflow legible enough to survive
> review.
