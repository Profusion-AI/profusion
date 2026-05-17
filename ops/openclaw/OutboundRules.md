# Profusion Outbound Rules

Status: draft-only operations active; live sending blocked
Owner: Kyle
Last updated: 2026-05-17

## Operating Posture

OpenClaw may research, score, draft, classify, brief, and log. OpenClaw may not send external prospect email yet.

No prospect email may be sent until Kyle explicitly approves:

- sender inbox
- campaign
- recipient list
- copy family
- daily cap
- suppression/unsubscribe process
- send ledger format

## Sender Lane

Planned identity: agents@profusion.ai.

This is an alias inside Kyle's primary Google Workspace/Gmail account, not a standalone Google account. Until receive/send tests and labels are confirmed, drafts must not assume the lane is live.

Required Gmail labels:

- OpenClaw / Inbox
- OpenClaw / Drafted
- OpenClaw / Approved to Send
- OpenClaw / Sent
- OpenClaw / Replies
- OpenClaw / Opt-Out
- OpenClaw / Bounces
- OpenClaw / Human Review

## Compliance and Deliverability Gates

Before live sending, verify:

- agents@profusion.ai can receive mail
- Gmail can send from agents@profusion.ai
- SPF, DKIM, and DMARC are configured for profusion.ai
- From and Reply-To are accurate
- commercial outreach includes a valid physical postal address
- every campaign has a clear opt-out method
- opt-outs are recorded before any future sends
- suppression is checked before every send
- bounce and reply monitoring exists
- daily volume starts very low

## Initial Volume Policy

- Days 1-3: zero external sends; drafts only
- First approved send test: 1-3 emails manually reviewed by Kyle
- Initial live cap after approval: no more than 5-10/day
- No automated follow-up sequence until bounce/reply/opt-out handling works

## Suppression Rules

Suppression must be checked before every send. Any unsubscribe, opt-out, negative privacy request, bounce requiring no further contact, or Kyle do-not-contact decision must be recorded before any future send attempts.

Suppression beats approval. If a recipient is suppressed, do not send even if the campaign is approved.

## Receipt Discipline

Every meaningful outbound action must produce:

- artifact pointer
- approval state
- risk note
- next safe action
- owner
- timestamp

## Hard Stops

Pause outbound preparation and notify Kyle if:

- a prospect asks to opt out
- bounce or complaint risk appears
- sender identity is unclear
- a claim feels unsupported
- a prospect asks about hiring decisions, certification, compliance guarantees, legal terms, security review, or production integrations
- the campaign starts to feel generic, pushy, or reputationally risky
