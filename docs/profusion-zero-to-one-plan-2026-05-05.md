# Profusion Zero-To-One Plan

Date: 2026-05-05

Purpose: coordinate Profusion's technical and business next steps for the first
week of May 2026 through the first paid client.

## Executive Decision

Profusion should not try to sell "AI governance" or a broad trust platform
right now. The next step is a founder-led paid pilot around one painful buyer
moment:

> Ship AI-mediated work that can survive scrutiny.

The near-term offer should be:

> Profusion Evidence Receipt Pilot: in one week, Profusion maps one
> AI-assisted workflow, defines the evidence boundary, captures or organizes the
> relevant artifacts, documents human review, and produces a reviewer-readable
> receipt that explains what happened and what it does not prove.

This keeps the ambition intact while making the first sale concrete. The first
client is not buying a mature SaaS platform. They are buying a bounded evidence
packet for an AI-assisted workflow they may need to defend to a client, legal
reviewer, executive, platform, or internal risk owner.

## Read Of The Three Planning Docs

### `docs/business-update.md`

This doc establishes the operational boundary. M0-M6 created the local
operating substrate. M7 is the internal operator cockpit, not the website and
not a customer portal. M7.5 is the first B2B-facing bridge: a
reviewer-readable evidence package.

Business implication: Profusion has enough machinery to support paid-pilot
conversations, but the buyer-facing surface should be the receipt packet, not
a self-service app.

### `docs/business-angle.md`

This doc establishes the category boundary. The product is not the content
pipeline, the cockpit, or a vague receipt. The product is a governed process
around important AI-assisted work:

```text
capture workflow -> preserve artifacts -> apply QA -> require human review -> track approval -> state limitations -> generate receipt
```

Business implication: the content workflow is the first governed workflow. The
company-level primitive is the receipt. Profusion should sell bounded process
evidence, not detector-grade truth, automated hiring, identity/liveness
verification, or compliance guarantees.

### `docs/consulting-thesis-wip.md`

This doc adds the missing demand layer. People may need governance, but they
want permission to move faster without looking reckless. "AI governance" is too
cold. "Ship AI work that can survive scrutiny" is closer to the buyer's actual
desire.

Business implication: lead generation should not start with abstract category
education. It should start with vivid buyer moments:

- A client asks how AI was used in a deliverable.
- Legal asks who reviewed a synthetic or AI-assisted asset.
- A content team needs to show the human approval boundary.
- An agency has answers scattered across Slack, Drive, Loom, Descript, and
  memory.
- A leader wants to use AI without creating a reputational problem later.

## Current Product Truth

### What Profusion Currently Does

Profusion is a local-first governed workflow system for AI-assisted content
operations. It currently includes:

- Python 3.11 orchestrator.
- SQLite source of truth.
- Explicit lifecycle state machine.
- Content intake, brief generation, script generation, rendering, QA, human
  approval, publishing, scheduling, retries, diagnostics, and handoff surfaces.
- Internal React/Vite operator cockpit at `apps/operator-cockpit/`.
- Public website in `dashboard/`, deployed separately at `https://profusion.ai`.
- File-first reviewer evidence packets under `data/receipts/`.
- A `content_video_receipt` receipt type for the current media-trust workflow.
- CLI receipt lifecycle:

```text
draft -> reviewed -> approved_for_packet -> delivered
```

The demo receipt currently exists as a draft packet for
`m75-demo-content-video-receipt`:

```text
data/receipts/content-video-m75-demo-con-20260503T155812Z-ceb13ddd/
```

### What It Does Not Do Yet

Profusion does not yet provide:

- Customer portal.
- Multi-tenant organization management.
- Billing.
- External reviewer queues.
- ATS, DAM, Slack, Drive, GRC, or procurement integrations.
- Work Trust scenario runner.
- Candidate ranking.
- Automated hiring or selection decisions.
- Identity verification.
- Liveness verification.
- Universal synthetic-media detection.
- Legal compliance certification.

These gaps are acceptable for the first sale if the offer is scoped as a
founder-led evidence pilot. They become dangerous only if the sales story
pretends Profusion is already a mature SaaS or assurance platform.

## Zero-To-One Strategy

The Thiel-style move is not to claim a giant market. It is to own a tiny,
urgent market where Profusion can be one of one.

The initial tiny market should be:

> Small and mid-sized AI-using media, content, and executive-communications
> teams that need to defend how AI was used in client-visible work.

The wedge is narrow because:

- It is closest to the current code and `content_video_receipt`.
- The artifacts are understandable: script, media asset, QA, approval, receipt.
- The buyer pain is human and near-term: client trust, legal review, platform
  disclosure, brand risk, synthetic media anxiety.
- The sales cycle is likely shorter than enterprise GRC or regulated hiring.

Work Trust remains the stronger long-term strategic wedge, but it should not be
marketed as shipped until there is a real Work Trust demo receipt. For now it
belongs in founder narrative and design-partner conversations, not as the first
promise.

## First Buyer Profile

Primary economic buyer:

- Founder of a 5-50 person AI-enabled video, creative, or content agency.
- Head of client services at an agency using AI assets in client work.
- Executive communications or content-ops lead producing sensitive AI-assisted
  media.

Acute trigger:

- A client, legal reviewer, executive, or platform asks how AI was used,
  reviewed, approved, and limited.

Current workaround:

- Slack messages, Drive folders, Looms, Descript exports, approval emails,
  checklists, memory, and manual screenshots.

Profusion's promise:

- One reviewer-readable packet that reconstructs the governed workflow without
  asking the buyer to assemble evidence manually after the fact.

Buyer-facing language:

> When someone asks how AI was used in this work, you should not have to
> reconstruct the answer from Slack, Drive, Loom, and memory.

## Paid Pilot Offer

Name:

> Profusion Evidence Receipt Pilot

Positioning:

> For teams using AI in client-facing or sensitive work, Profusion maps one
> workflow and produces a reviewer-readable evidence receipt showing what AI
> touched, what humans reviewed, what artifacts were used, what was approved,
> and what the receipt does not prove.

Scope:

- One AI-assisted workflow.
- One evidence-boundary session.
- One artifact map.
- One human review gate.
- One receipt packet.
- One limitations statement.
- One debrief call.

Suggested price hypothesis:

- Ask: $5,000 to $15,000 for the first serious paid pilot.
- Design-partner exception: $2,500 to $5,000 only if the buyer has an urgent
  workflow, will give fast feedback, and may become a repeat case study or
  referral source.

Do not sell:

- Compliance guarantee.
- Legal advice.
- Customer portal.
- AI detector.
- Authenticity certification.
- Automated decision system.

## Buyer Conversation Plan

Goal by Friday, 2026-05-15:

- Identify 30 real people.
- Send 20 warm or semi-warm notes.
- Book 5 serious conversations.
- Ask at least 2 prospects directly whether they would pay for one workflow
  receipt pilot.
- Close or advance 1 pilot candidate to written scope.

Discovery questions:

- When a client or reviewer asks how AI was used, what do you show them?
- What part of your AI workflow would be hardest to defend later?
- Have you ever avoided using AI because you were unsure how to explain it?
- What would need to be in a one-page receipt for this to be useful?
- Would you pay for someone to create that evidence packet for one real
  workflow?

Outbound message shape:

```text
I am building Profusion around a specific problem: AI makes client-facing work
faster, but it also makes the review trail harder to explain.

For teams producing AI-assisted media, I am testing a one-week evidence receipt
pilot: one workflow, one artifact map, one human review gate, one packet that
states what happened and what it does not prove.

When a client asks how AI was used in a deliverable, what do you currently show
them?
```

The public posture should be statement-led, not question-led. Lead with a
point of view, then end with a sharp question.

Example:

```text
The final artifact is no longer enough. If AI touched the workflow, the review
trail matters: what changed, who approved it, what artifacts exist, and what
the claim refuses to prove.

When a client asks how AI was used, what do teams actually show them today?
```

## Technical Plan From Now To First Client

### 1. Prepare The Demo Packet

Owner: Codex/local technical lane.

Actions:

- Keep the public website stable.
- Use the existing demo item and receipt packet.
- Transition the demo receipt through the intended lifecycle only when the
  packet has actually been reviewed:

```bash
uv run profusion receipt transition --receipt-id content-video-m75-demo-con-20260503T155812Z-ceb13ddd --to reviewed
uv run profusion receipt transition --receipt-id content-video-m75-demo-con-20260503T155812Z-ceb13ddd --to approved_for_packet
```

- Rebuild the static cockpit snapshot.
- Deploy a private Netlify draft, not production.
- Smoke the private draft.
- Keep the draft explicitly framed as read-only evidence preview, not hosted
  SaaS.

Acceptance criteria:

- A prospect can see a queue item, evidence state, receipt status, and packet
  files without needing local tooling.
- The packet can be explained in 60 seconds.
- The limitations are visible and plain-English.

### 2. Create A Sales-Ready Sample Receipt

Owner: Codex/local technical lane, reviewed by Kyle.

Actions:

- Create one sanitized sample receipt artifact under `docs/` or
  `docs/examples/`.
- Include:
  - workflow summary
  - artifacts captured
  - review/approval state
  - limitations
  - what the receipt does not prove
  - appendix pointer to machine-readable evidence

Acceptance criteria:

- Kyle can send it before a call.
- It does not require a buyer to understand M7, M7.5, SQLite, FastAPI, or the
  cockpit.
- It avoids compliance and authenticity overclaims.

### 3. Create The Pilot Operating Kit

Owner: Codex/local technical lane.

Artifacts:

- `pilot-intake.md`: questions for the buyer's workflow.
- `evidence-boundary-worksheet.md`: what is inside and outside the receipt.
- `receipt-review-checklist.md`: reviewer checks before a packet is marked
  `approved_for_packet`.
- `pilot-scope-template.md`: one-page scope for the paid pilot.

Acceptance criteria:

- Kyle can run a discovery call and produce a scope without improvising from
  scratch.
- Each artifact reinforces the repeatable kernel:

```text
workflow boundary -> evidence map -> captured events -> review decision -> limitations -> receipt packet
```

### 4. Avoid Premature Product Work

Do not build these before the first client:

- Customer portal.
- Login.
- Billing.
- Multi-tenant orgs.
- External reviewer queue.
- ATS integration.
- DAM integration.
- GRC integration.
- Work Trust runner.
- Website rewrite.

Only build a new feature before first client if it directly helps Kyle show,
generate, review, or deliver one receipt packet.

### 5. After The First Paid Workflow

Technical learning goals:

- Which evidence fields mattered to the buyer?
- Which fields confused them?
- Which artifacts were missing from the current receipt model?
- Did the buyer need a one-page summary, appendix, machine-readable JSON, or
  all three?
- Did they ask for repeat receipts, a template, an integration, or a portal?

Productization rule:

> Build only what the second sale requires.

## Business Plan From Now To First Client

### Week 1: 2026-05-05 To 2026-05-10

Business:

- Pick the wedge: AI-assisted media governance.
- Build a list of 30 named prospects.
- Prioritize warm paths: agency owners, content leads, video producers,
  executive communications people, AI media operators, client-services leads.
- Publish 3 statement-led posts around the same thesis:
  - final artifacts no longer self-authenticate
  - AI work needs a review trail
  - receipts are useful only when they state limitations
- Send the first 10 direct notes.

Technical:

- Review and approve the current demo receipt.
- Prepare the private draft/demo path.
- Create the sample receipt and pilot operating kit.

### Week 2: 2026-05-11 To 2026-05-17

Business:

- Hold 5 discovery calls.
- Ask the payment question directly in at least 2 calls.
- Convert the strongest pain into a one-page pilot scope.
- Keep notes by buyer trigger, not by industry label.

Technical:

- Adjust only the receipt/sample packet language if calls reveal confusion.
- Do not add platform features unless they unblock a signed pilot.

### Week 3: 2026-05-18 To 2026-05-24

Business:

- Close 1 design-partner paid pilot or make an explicit no-go decision.
- If no one will pay, diagnose whether the problem is:
  - wrong buyer
  - wrong trigger
  - wrong offer
  - unclear artifact
  - pain not urgent enough

Technical:

- If a pilot closes, run the workflow manually/founder-led.
- Produce the receipt packet with the existing Profusion machinery wherever
  possible.
- Track every manual step as product discovery.

## Operating Split

Kyle:

- Owns buyer conversations, founder narrative, warm intros, pricing ask, and
  the decision to pursue or drop a wedge.
- Should avoid hiding in docs after the demo packet is ready.
- Should judge Profusion by the energy and specificity that comes from buyer
  calls, not by strategy quality alone.

Codex/local repo lane:

- Owns current-state verification, receipt packet preparation, private demo
  rebuilds, sample artifacts, pilot templates, and minimal code/docs changes
  needed for the first pilot.
- Should not expand the product surface without buyer evidence.

Browser-side ChatGPT/creative lane:

- Can help turn the thesis into outbound copy, X/LinkedIn posts, call scripts,
  and follow-up emails.
- Should keep the message concrete and buyer-moment driven.

## Decision Gates

By 2026-05-15:

- If 5 real conversations produce at least 2 "this is a real problem" signals,
  continue the media-governance wedge.
- If prospects like the thesis but cannot name a workflow, sharpen the trigger
  and try another 10 prospects.
- If prospects can name the workflow but will not pay for a manual packet,
  reduce scope once, then reassess.
- If conversations consistently drift to hiring/contractor trust, start a
  Work Trust demo receipt as a separate design-partner lane.

By 2026-05-24:

- If one pilot is paid or close to paid, execute the founder-led pilot and
  design the second sale into the debrief.
- If no pilot is close after 10 serious conversations, do not build more
  platform. Revisit wedge, buyer, and desire.

## North Star

Profusion's first client should prove this:

> One real buyer had one AI-assisted workflow where the final output was not
> enough, and Profusion made that workflow legible enough to survive review.

That is the zero-to-one milestone. Everything else is supporting machinery.
