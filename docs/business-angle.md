# Profusion AI Business Angle

Date: 2026-05-03

## One-Line Thesis

Profusion AI is building a trust wrapper around AI-mediated work.

AI makes outputs cheap. Profusion makes the process inspectable.

## What This Means

The product is not the content pipeline by itself. The product is not the
operator cockpit by itself. The product is not a receipt because receipts sound
enterprise-friendly.

The product is the governed process around important AI-assisted work:

```text
capture workflow -> preserve artifacts -> apply QA -> require human review -> track approval -> state limitations -> generate receipt
```

When AI is involved, the final artifact is no longer enough. A polished video,
essay, resume, transcript, coding answer, report, or presentation no longer
proves much about how it was produced, who reviewed it, what was automated, what
was human, what evidence exists, or what can honestly be claimed.

Profusion's answer is:

> Do not just inspect the output. Inspect the governed process that produced it.

## Current Build Reality

Profusion currently has a working local-first governed content workflow.

Implemented substrate:

- explicit content lifecycle state machine
- local SQLite source of truth
- idea, brief, script, render, QA, approval, publish, schedule, retry, and
  handoff surfaces
- internal operator cockpit at `apps/operator-cockpit/`
- public website in `dashboard/`
- file-first `content_video_receipt` packets
- receipt read API and static cockpit snapshot compatibility
- receipt lifecycle states:

```text
draft -> reviewed -> approved_for_packet -> delivered
```

The current receipt documents workflow evidence only:

- declared workflow
- generated artifacts
- QA checks
- review state
- approval state
- evidence trail
- limitations

It does not claim:

- universal synthetic-media detection
- identity verification
- liveness verification
- proof that manipulation did not occur outside the captured workflow
- candidate ranking
- automated hiring
- hire/no-hire recommendation
- customer portal readiness
- Work Trust production readiness

That restraint is part of the product posture. Profusion should win trust by
being precise about what it governed, what it observed, and what it cannot
claim.

## The Production/Draft Boundary

`https://profusion.ai` is the public website. It is not currently the live
operator cockpit and it does not expose the latest internal receipt-lifecycle
work.

The operator cockpit is internal. A Netlify draft can be deployed as a static,
read-only preview of the cockpit using generated JSON snapshot files. That
preview can show queue state, evidence state, receipt packets, lifecycle badges,
and next terminal commands, but it does not run the local FastAPI/SQLite
backend and it does not perform mutations.

The operational step before showing the cockpit externally is:

```text
run the demo receipt to the intended lifecycle state
rebuild the static cockpit snapshot
deploy a fresh Netlify draft
smoke the draft
share the draft privately
```

This is not about having clients. It is about making sure the private demo
matches the current repo truth before a reviewer, advisor, or prospect sees it.

## What Profusion Can Market Now

Profusion can market a narrow founder-led B2B pilot, not a mature SaaS product.

The honest offer is:

> Profusion helps teams turn high-risk AI-assisted workflows into reviewable
> evidence packets.

A stronger paid-pilot framing:

> Governed AI Workflow Receipt Pilot

Pilot deliverable:

- one defined AI-assisted workflow
- one declared policy boundary
- one evidence capture path
- one human review gate
- one receipt packet
- one limitations statement
- one reviewer-readable demo packet

The buyer is not paying for a self-service platform yet. The buyer is paying to
learn whether a messy AI-mediated workflow can be wrapped in enough evidence,
review, and limitations to become defensible.

## First B2B Buyer Angles

### 1. AI Media Governance

Target buyer:

- media teams
- executive communications teams
- marketing operations
- agencies using AI-generated or AI-assisted video
- compliance-aware content teams

Problem:

AI-assisted content is easy to produce but hard to defend. Buyers need to show
that content had a governed process behind it: QA, approval, artifact trail,
human review, and clear disclosure boundaries.

What Profusion can show now:

- governed content workflow
- content video receipt
- artifact and approval trail
- cockpit evidence view
- lifecycle states for receipt readiness

Honest claim:

> Profusion creates workflow evidence for AI-assisted media production.

Do not claim:

> Profusion detects all synthetic media or proves a video is authentic.

### 2. AI-Assisted Work Trust

Target buyer:

- security-sensitive employers
- remote technical hiring teams
- contractor onboarding teams
- privileged-access workforce teams
- AI governance leaders

Problem:

AI makes polished work samples cheap. A company no longer knows whether a
candidate, contractor, or employee demonstrated real judgment or merely passed
through an AI tool chain.

Planned workflow:

```text
participant -> scenario -> aided work session -> trace -> rubric -> human review -> receipt
```

What Profusion can market now:

- a design-partner or paid-pilot concept
- the trust-wrapper thesis
- the existing receipt/cockpit substrate as proof that the governance machine is
  real
- a narrow prototype path for one scenario

Honest claim:

> Profusion is extending its governed workflow receipt model toward AI-assisted
> work evaluation.

Do not claim:

> Profusion ranks candidates, verifies identity, proves liveness, or automates
> hiring decisions.

### 3. AI Governance Evidence For Regulated Teams

Target buyer:

- AI governance leads
- compliance teams
- risk teams
- legal operations
- enterprise innovation teams

Problem:

Organizations are adopting AI faster than they can prove what happened inside
AI-assisted processes.

What Profusion can offer:

- a receipt template for one workflow
- process evidence vocabulary
- approval and limitation structure
- a working demonstration of reviewable AI-assisted output

Honest claim:

> Profusion helps define and demonstrate evidence boundaries for AI-mediated
> workflows.

Do not claim:

> Profusion is an enterprise compliance platform.

## Unified Product Frame

The content workflow and Work Trust are not separate ideas. They use the same
machine with different nouns.

Current media trust workflow:

```text
idea -> brief -> script -> render -> QA -> approval -> publish/schedule -> receipt
```

Future Work Trust workflow:

```text
participant -> scenario -> aided work session -> trace -> rubric -> human review -> receipt
```

The shared question:

> What happened, under what rules, with what evidence, reviewed by whom, and
> what can we honestly claim?

This is the company-level category:

```text
AI-mediated workflow + high consequence + ambiguity about what happened
= need for process evidence
```

## Category Language

Primary category:

> Workflow trust infrastructure for the AI age.

Plain-English version:

> Profusion turns AI-assisted activity into reviewable evidence.

Offer language:

> Trust receipts for high-risk AI workflows.

More conservative offer language:

> Governed workflow evidence packets for AI-assisted work.

Avoid making "content pipeline" the company category. Content is the first
workflow. Trust receipts are the business.

## Website And Pitch Language

Use:

- trust wrapper around AI-mediated work
- governed AI workflow evidence
- reviewable evidence packets
- workflow receipts
- human review gates
- audit trail
- limitations-first evidence
- process evidence for AI-assisted output

Avoid:

- certified truth
- universal detector
- identity verification
- liveness verification
- candidate ranking
- automated hiring
- compliance solved
- fully autonomous content engine
- customer portal
- production SaaS

## Practical B2B Pitch

Short version:

> AI makes final outputs easy to fake, polish, or overstate. Profusion helps
> teams inspect the process behind the output: what happened, what artifacts
> were created, what QA ran, who reviewed it, what was approved, and what the
> receipt does not claim.

Pilot version:

> We start with one high-risk AI workflow, define its evidence boundary, run it
> through a governed process, and produce a reviewer-readable receipt packet.
> The first goal is not a platform rollout. The first goal is to prove whether
> the workflow can be made inspectable and defensible.

## What To Sell Before Clients Exist

No clients means Profusion should not market customer proof. It can market a
clear problem, a working prototype, and a narrow pilot offer.

Market these now:

- the thesis: final outputs no longer self-authenticate
- the method: govern the process, not just the artifact
- the prototype: internal cockpit plus content video receipt
- the offer: one workflow, one evidence packet, one review cycle
- the boundary: evidence and review, not detector-grade truth

Do not market these yet:

- client logos
- deployment scale
- compliance guarantees
- automated hiring
- Work Trust as already shipped
- broad enterprise platform capability

## Recommended Near-Term Offer

Name:

> Governed AI Workflow Receipt Pilot

First vertical options:

1. AI-assisted media governance
2. privileged remote contractor / AI-mediated work assessment
3. internal AI governance evidence packet

Recommended first external conversation:

> We are looking for one design partner with a high-risk AI-assisted workflow
> where the final output alone is not enough. We will help define the workflow
> boundary, capture artifacts, apply review gates, and produce a receipt that
> states what happened and what it does not prove.

This is B2B-legible without pretending Profusion already has a finished
customer portal.

## Strategic Guardrails

Keep:

- operator control
- review gates
- state machines
- receipts
- artifacts
- limitations
- boring evidence

Defer:

- customer portal
- billing
- org management
- external reviewer queues
- identity/liveness claims
- detector claims
- candidate ranking
- automated decisions
- platform automation

The strategic wedge is not speed. It is defensibility.

## PM Verdict

The vision is aligned if Profusion is described as:

> a system that turns AI-assisted activity into reviewable evidence.

The vision becomes misaligned if Profusion is described primarily as:

- a content automation product
- a synthetic media detector
- a hiring automation platform
- a generic dashboard
- an enterprise compliance platform

Profusion started with media because media gave the project a concrete workflow
to govern. The broader business is trust receipts for high-risk AI-mediated
workflows.

