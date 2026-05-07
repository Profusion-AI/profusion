# Profusion Business Update

Date: 2026-05-03

## Executive Summary

Profusion is past the foundation phase and is now in the transition from an
internal MVP to a paid-pilot-ready workflow.

M0-M6 established the operating core: a local pipeline that can ingest ideas,
generate structured creative work, render media, apply QA and approval gates,
publish or schedule approved output, and recover from failures with inspectable
state. This is the internal machinery that makes Profusion operable.

M7 is the current clarification point. It should be treated as the internal
Profusion operator dashboard, not as a B2B customer portal. Its purpose is to
help Profusion run the system reliably, inspect state, recover from failures,
and produce pilot evidence. The B2B customer-facing experience should come
later as a narrower reviewer-facing output first, then eventually as a customer
admin portal if buyer demand proves it is worth building.

## What M0-M6 Established

M0-M6 should be understood as the internal MVP foundation.

They do not yet constitute a polished customer-facing SaaS product. They do
prove that Profusion has a real operating substrate instead of a one-off demo
script.

### M0: Foundation

M0 created the base project structure, local state machine, SQLite storage,
CLI skeleton, vendor boundaries, configuration, and licensing posture.

Business meaning: Profusion became a real local system with defined states and
dependencies, not just a loose experiment.

### M1: Editorial Pipeline

M1 moved content from raw topic to structured brief to script variants, with
validation around generated outputs.

Business meaning: the system can turn an initial idea into production-ready
creative planning assets in a repeatable workflow.

### M2: Rendering

M2 connected selected script variants to local video rendering through the
MoneyPrinterTurbo integration and stored local render artifacts.

Business meaning: Profusion can move from planning into generated media output.

### M3: QA and Approval Gates

M3 added post-render QA and human approval before any publishing step.

Business meaning: the system protects reputation and operator judgment. It does
not blindly publish generated content.

### M4: Publishing

M4 added approval-gated publishing through MoneyPrinterV2/PostBridge.

Business meaning: approved work can leave the local system and move toward
distribution through a controlled publishing adapter.

### M5: Scheduling and Cross-Posting

M5 added scheduled publishing and multiple target coordination.

Business meaning: Profusion can coordinate planned distribution instead of only
immediate one-off posting.

### M6: Agent Hardening and Operational Durability

M6 made the system inspectable, retryable, handoff-safe, and durable under
operator or agent use. It added status, inspect, jobs, renders, approvals, logs,
handoff, retry, and offline smoke surfaces.

Business meaning: Profusion became operator-grade. Failures are part of the
workflow, not hidden emergencies. A human or agent can inspect what happened,
understand whether recovery is safe, and continue without manually editing the
database.

## Current M7 Reality

M7 was intended to be the local operator dashboard. The dashboard/API work
landed in the repo, but the visible `dashboard/` Vite entrypoint was later
repurposed for the public Profusion AI website deployed to Netlify.

The important business interpretation is:

- M7 is not "not started."
- M7 is not the public website.
- M7 is not the eventual B2B customer portal.
- M7 is an internal operator cockpit that now needs a clean surface boundary.

M7 now has a clean standalone source-of-truth trail:

- `docs/milestones/M7_OPERATOR_COCKPIT_PRD_TTD.md`
- `docs/milestones/M7_OPERATOR_COCKPIT_SMOKE_2026-05-03.md`
- `docs/milestones/M7_OPERATOR_COCKPIT_CLOSEOUT_2026-05-03.md`
- `docs/milestones/M7_OPERATOR_COCKPIT_FINAL_CLOSEOUT_2026-05-06.md`

The old issue was that intent was spread across the M6 readiness note,
directional spec, decisions log, API tests, and status reconciliation. That is
now resolved for M7.

## What M7 Should Provide

M7 should provide an internal Profusion operator dashboard.

Primary user: the operator of Profusion AI.

Near-term operators:

- Kyle
- Codex or other coding agents
- Future Profusion team members or contractors

Primary job: help Profusion run the workflow reliably enough to support demos,
paid pilots, and evidence generation.

M7 should provide:

- Queue visibility: what work exists and what stage each item is in.
- Item detail: lifecycle state, artifacts, jobs, approvals, blockage, recent
  logs, and next safe command.
- Recovery support: clear failure explanation and whether retry is safe.
- Guarded actions: safe retry paths only, not broad dangerous controls.
- Handoff context: enough state for another operator or agent to resume work.

M7 proves that Profusion can be operated. It does not prove market demand,
commercial compliance, identity verification, detection accuracy, or customer
self-service readiness.

## Internal MVP vs B2B-Facing Product

This distinction should remain explicit.

### Internal MVP

The internal MVP is the system Profusion uses to deliver the work.

It includes:

- CLI and orchestration layer
- Local state machine and database
- Render, QA, approval, publish, schedule, retry, and diagnostic paths
- Operator dashboard
- Trust-session tooling and evidence production

Audience: Profusion operators.

Goal: make the workflow reliable, inspectable, repeatable, and demoable.

### B2B-Facing Output

The first B2B-facing surface should not be a full portal. It should be a
reviewer-readable evidence package.

It should include:

- Session summary
- Declared mode
- Policy decision
- Watermark or disclosure state
- Outcome
- Receipt or audit artifact
- Plain-English explanation of what the system did and did not prove

Audience: pilot buyer, reviewer, evaluator, compliance stakeholder, hiring or
security lead.

Goal: help the buyer understand and evaluate the governed video-session
workflow without needing to operate Profusion.

### Future B2B Customer Portal

A customer portal should be deferred.

It may eventually include:

- Organization settings
- Customer policy configuration
- User and reviewer management
- Session history
- Review queues
- Audit exports
- Billing or plan management

Audience: paying customer admins and reviewers.

Goal: let customers self-administer Profusion after the paid-pilot workflow is
validated.

This is not the current MVP priority.

## M7 and Beyond

### M7: Internal Operator Cockpit

Recommended definition:

> M7 is the internal Profusion operator cockpit for reliably producing
> pilot-grade workflow outputs and evidence.

Closeout work:

- Decide where the operator dashboard lives now that `dashboard/` is the public
  Netlify website.
- Restore or separate the local operator dashboard entrypoint.
- Browser-smoke the local operator dashboard against `profusion serve`.
- Capture a clean M7 PRD/TTD that defines user journeys, non-goals, UX states,
  technical contracts, and acceptance criteria.

### M7.5 / PP1: Reviewer-Readable Pilot Evidence

Recommended definition:

> M7.5 / PP1 turns internal workflow output into buyer-readable pilot evidence.

Deliverables:

- A clean trust-session receipt format.
- A plain-English receipt summary.
- A demo/pilot evidence packet.
- Clear language around boundaries: declaration, policy, watermark, receipt,
  and review, not detector-grade claims.

This is the first meaningful B2B-facing surface.

### M8: Measurement and Learning Loops

M8 should remain deferred until the pilot path is clearer.

Potential later scope:

- Performance and outcome metrics
- Review-loop analytics
- Published-output measurement
- Feedback loops for improving future sessions or content workflows

M8 should not distract from M7 closeout or paid-pilot readiness.

### Later: Customer Admin Portal

A customer admin portal should only begin after there is enough buyer signal to
justify it.

It should not be conflated with M7. M7 is for Profusion operators. The customer
portal is a later SaaS/productization surface.

## Business Direction

The near-term business objective is not to build a broad platform. It is to
produce a credible, narrow paid-pilot workflow.

The strongest current path is:

1. Keep the internal operator dashboard focused on Profusion's ability to run
   and recover the system.
2. Build reviewer-readable evidence for B2B buyers.
3. Use that evidence to support a paid-pilot conversation.
4. Defer customer self-service until the pilot proves what customers actually
   need to configure, review, and export.

The practical question for the next sprint is:

> Can Profusion show a buyer a governed video-session workflow, produce a
> readable receipt, and explain exactly what the system did and did not prove?

That is the business bridge from internal MVP to B2B-facing product.
