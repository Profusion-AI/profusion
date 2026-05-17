# OpenClaw Approval Levels for Profusion

Status: active
Owner: Kyle
Last updated: 2026-05-17

## Current Authority

Current outbound authority is L0/L1 only. No external prospect email, follow-up, LinkedIn message, public post, or campaign send is approved.

## L0: Observe and Summarize

No external effect. OpenClaw may do this without additional approval.

Examples:

- inspect local docs and repos
- search public sources
- summarize inbox/replies if mailbox access is available
- produce daily owner briefs
- list candidate companies from approved public sources
- create internal briefs and receipts

## L1: Draft and Prepare

No external effect. Kyle review is required before anything is used externally.

Examples:

- score prospects
- draft cold email copy
- draft follow-ups
- prepare campaign concepts
- create approval records
- prepare call briefs
- update internal/private ledgers

## L2: Bounded External Send

External effect inside a pre-approved campaign or workflow. Not currently enabled.

Required before any L2 send:

- Kyle approves sender inbox
- Kyle approves campaign
- Kyle approves recipient list
- Kyle approves copy family
- Kyle approves daily cap
- suppression and unsubscribe process exists
- send ledger format exists
- accurate From and Reply-To are verified
- postal address and opt-out method are present where required
- every send writes a ledger row

## L3: Sensitive External Action

Requires Kyle approval for each instance.

Examples:

- legal, compliance, security, pricing, integration, partnership, contract, or procurement replies
- any claim about Profusion capabilities not already approved
- any prospect-specific commitment
- any use of a prospect name, logo, or content outside private operations

## Approval Record Format

Record each approval with:

- approval_id
- approver
- timestamp
- approval_level
- action_type
- campaign_id if applicable
- allowed recipients or lead segment
- approved copy family/version
- daily cap
- follow-up count
- expiry date
- risk notes
- next safe action

