# Current Splash Page Copy

Date: 2026-05-05

Source: `dashboard/src/App.tsx`

Status: superseded by the 2026-05-06/2026-05-07 reliability-gap homepage.
This file preserves the earlier workflow-trust homepage copy for reference. Do
not treat it as the current live `dashboard/src/App.tsx` copy.

Current homepage source of truth:

```text
dashboard/src/App.tsx
docs/profusion-homepage-reliability-gap-update-2026-05-05.md
docs/profusion-m775-implementation-alignment-addendum-2026-05-06.md
```

Purpose: preserve the current public homepage/splash-page copy as reference
material for positioning, outbound, landing-page variants, and future copy
edits.

## Navigation

- Profusion AI
- Workflow
- Use Cases
- Services
- Principles
- Contact

## Hero

Eyebrow:

> AI WORKFLOW TRUST PRACTICE

Headline:

> Turn AI-assisted workflows into reviewable evidence.

Rendered headline line breaks:

```text
Turn AI-assisted
workflows into
reviewable evidence.
```

Primary subhead:

> AI is entering high-risk workflows faster than most organizations can govern
> them. Profusion helps teams map one workflow, capture the right artifacts,
> add human review gates, and produce a plain-English receipt showing what
> happened.

Secondary subhead:

> We focus on AI-assisted content, synthetic media risk, recruiting and
> staffing workflows, client-facing automation, and internal AI governance. No
> black-box scoring. No automated decisions. No fake certainty.

Primary CTA:

> Start with One Workflow

Secondary CTA:

> See the Receipt Method

## Hero Receipt Card

Receipt label:

> WORKFLOW RECEIPT

Status chip:

> HUMAN REVIEWED

Visible receipt fields:

```text
workflow_id
wf_ai_workflow_review_7F9A

evidence_boundary
client_visible_output

artifacts_captured
brief · draft · qa · approval

review_gate
human_reviewed

claims_supported
process_evidence_only

receipt_status
ready_for_review_packet
```

Receipt status pills:

- EVIDENCE CAPTURED
- HUMAN REVIEW

## The Problem

Eyebrow:

> The Problem

Headline:

> AI is entering workflows faster than [rotating audience] can govern it.

Rotating audience words:

- organizations
- agentic teams
- content ops
- recruiters
- AI teams
- automation teams
- risk teams
- executives

Problem cards:

### Outputs are easy. Evidence is hard.

> AI-assisted work often leaves scattered prompts, drafts, files, messages, and
> approvals instead of one reviewable trail.

Status:

> REVIEW REQUIRED

### Agents produce work faster than teams produce evidence.

> Coding agents, AI assistants, and automation workflows can generate outputs,
> edits, summaries, drafts, and decisions across scattered tools. Human
> approval may happen, but the trail is often incomplete.

Status:

> AGENTIC REVIEW GAP

### Review gates are informal.

> Teams may know humans reviewed the work, but cannot easily show what was
> reviewed, when, by whom, or under what boundary.

Status:

> HUMAN REVIEW

### Claims get overstated.

> A credible trust system needs to show what happened and what the evidence
> does not prove.

Status:

> LIMITED CLAIMS

## Workflow Trust Layer

Eyebrow:

> Workflow Trust Layer

Headline:

> A control layer for high-risk AI-assisted work.

Subhead:

> The goal is not trust language alone. The goal is to make AI-assisted and
> agentic workflows inspectable: what the system did, what artifacts exist,
> what humans reviewed, what changed, and what the receipt does and does not
> prove.

Step labels:

- Map
- Capture
- Review
- Bound
- Receipt

### Step 1: Map

Title:

> Define the workflow boundary

Description:

> Start with one high-risk AI-assisted workflow and make clear what is inside
> the receipt and what remains outside it.

Recorded details:

- workflow_scope
- risk_context
- evidence_boundary

### Step 2: Capture

Title:

> Preserve the artifacts

Description:

> Capture the briefs, drafts, generated assets, QA outputs, logs, approvals,
> and other evidence needed to reconstruct the process.

Recorded details:

- source_artifacts
- generated_outputs
- qa_checkpoint

### Step 3: Review

Title:

> Add human review gates

Description:

> Make human judgment explicit: what was reviewed, what changed, what passed,
> what failed, and what needed escalation.

Recorded details:

- review_gate
- human_decision
- escalation_path

### Step 4: Bound

Title:

> State what the evidence supports

Description:

> The receipt describes supported claims and known limitations so teams do not
> sell fake certainty or imply assurance they do not have.

Recorded details:

- supported_claims
- known_limits
- non_claims

### Step 5: Receipt

Title:

> Produce reviewable evidence

Description:

> Generate a plain-English workflow receipt that a client, executive, reviewer,
> or risk owner can inspect without reconstructing the process from scratch.

Recorded details:

- receipt_packet
- review_status
- delivery_record

## Where We Start

Eyebrow:

> Where We Start

Headline:

> Start with the AI workflows someone may ask you to defend.

Subhead:

> When AI touches agentic work, client-facing content, synthetic media, hiring
> workflows, or customer automation, the final output is not enough. Teams need
> a clear record of what happened, who reviewed it, and what evidence supports
> the claim.

Status line:

> Pilot engagements begin with one workflow and one reviewable receipt.

Tab labels:

- Overview
- Architecture
- Status

### Overview Cards

#### AI CONTENT APPROVAL

Title:

> Show how client-facing AI work was reviewed.

Description:

> Capture the brief, generated assets, QA checks, revisions, and human approval
> trail before public or client delivery.

#### SYNTHETIC MEDIA RISK

Title:

> Make synthetic media reviewable before it reaches clients or the public.

Description:

> Prototype disclosure, artifact trails, policy decisions, and receipt language
> for altered or AI-generated media.

#### RECRUITING & STAFFING

Title:

> Keep AI-mediated work reviewable.

Description:

> Prototype evidence receipts for work samples, contractor readiness, and
> recruiter workflows without automated ranking or hiring decisions.

#### CLIENT-FACING AUTOMATION

Title:

> Give buyers an evidence layer.

Description:

> Help AI automation agencies and consultants show where workflow evidence,
> human judgment, and limitations enter the system.

### Architecture Tab

Label:

> SYSTEM ARCHITECTURE

Layers:

```text
AI-Assisted or Agentic Workflow
Profusion Evidence Layer
Artifact + Review + Receipt Engine
Client / Legal / Risk Review
```

Integration note:

> Agentic workflow support: Profusion adds a receipt layer between agentic work
> and human approval. Planned integration path: Profusion MCP tools for
> capturing workflow events, artifacts, review checkpoints, and receipt metadata
> from agentic environments.

### Status Tab

```text
Practice status: Founder-led workflow trust practice
Commercial posture: Founder-led paid pilots, not self-serve SaaS
Trust mechanism: Artifact capture, QA, human review, workflow receipt
Current boundary: Process evidence, not compliance certification
```

## Consulting Services

Eyebrow:

> Consulting Services

Headline:

> Build the evidence layer before the workflow becomes a risk.

### 01 - AI Workflow Trust Strategy

Tagline:

> Workflow maps, evidence boundaries, review gates.

Description:

> Map the AI-assisted workflows where final outputs are not enough, then define
> the evidence and human review controls that make those workflows governable.

Tags:

- Workflow Mapping
- Evidence Design
- Review Gates

### 02 - Workflow Receipt Prototyping

Tagline:

> Plain-English packets for high-risk AI work.

Description:

> Design and prototype workflow receipts that capture artifacts, review state,
> supported claims, limitations, and delivery-ready evidence.

Tags:

- Receipts
- Artifacts
- Limitations

### 03 - AI-Assisted & Agentic Work Review Systems

Tagline:

> Human accountability for AI-mediated work.

Description:

> Prototype review paths for AI-assisted content, coding-agent outputs,
> synthetic media, recruiting workflows, and client-facing automation without
> black-box scoring or automated decisions.

Tags:

- Oversight
- QA
- Human Judgment

### 04 - AI Trust Pilot Advisory

Tagline:

> Product wedge, architecture, launch narrative.

Description:

> Help teams shape AI workflow pilots around clear evidence boundaries, review
> gates, receipt logic, and a launch narrative that does not overclaim.

Tags:

- Strategy
- Architecture
- Narrative

## Ideal Clients

Eyebrow:

> Ideal Clients

Headline:

> For teams whose AI work needs to survive review.

Subhead:

> We work best with teams who already feel the gap between moving faster with
> AI and explaining what happened when a client, reviewer, executive, or risk
> owner asks.

Client list:

1. AI content and synthetic media teams that need review gates, artifact trails, and approval receipts.
2. Engineering, product, and AI operations teams using coding agents or MCP-connected tools who need reviewable evidence around agent outputs, human approvals, and production-facing changes.
3. Recruiting and staffing firms exploring AI-assisted workflows without automated ranking or black-box hiring decisions.
4. AI automation agencies and consultants whose clients need evidence that a workflow is governed.
5. Governance, risk, and operations leaders who need workflow-level proof that policy became practice.

## Operating Principles

Eyebrow:

> Operating Principles

Headline:

> Trust is not a vibe.

Subhead:

> It is workflow scope, artifact capture, human review, limitations, and
> receipts.

### Map the workflow.

> The trust layer starts with one concrete AI-assisted workflow, not a generic
> responsible-AI claim.

### Capture the evidence.

> Artifacts, QA checks, review notes, approvals, and limitations should survive
> outside scattered tools and memory.

### Preserve human judgment.

> The point is not to automate responsibility away. The point is to show where
> human review entered the process.

### Limit the claim.

> A credible receipt says what the evidence supports and what remains outside
> the captured boundary.

### Never overclaim certainty.

> A trust system loses credibility the moment marketing outruns the evidence.
> We keep those two aligned.

## Contact

Eyebrow:

> Contact

Headline:

> Start with one high-risk workflow.

Subhead:

> We work with a small number of teams at a time. If one AI-assisted workflow
> needs a trust layer, start there.

Contact notes:

- First session: map one workflow and its evidence boundary.
- Work product: workflow receipts, review gates, and limitation language.
- No long-term lock-in. Engagements are scoped around a defined workflow.

Form label:

> WORKFLOW TRUST SESSION REQUEST

Form fields:

- Name
- Organization
- Email
- Workflow context

Workflow context placeholder:

> Briefly describe the AI-assisted or agentic workflow, output, or review
> problem...

Submit button:

> Request a Session

Submitting state:

> Sending...

Error state:

> The request could not be sent. Please try again.

Confirmation:

```text
REQUEST RECORDED
We'll be in touch.
Thank you, {name}. We review all requests personally and will respond within two business days.
```

## Footer

Brand:

> Profusion AI

Footer line:

> Reviewable evidence for AI-assisted work. © 2026

Footer links:

- Workflow Trust
- Use Cases
- Services
- Contact
