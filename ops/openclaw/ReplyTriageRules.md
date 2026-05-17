# Reply Triage Rules

Status: draft-only until mailbox lane is confirmed
Owner: Kyle
Last updated: 2026-05-17

## Labels

Inbound messages to agents@profusion.ai should be routed into:

- OpenClaw / Inbox
- OpenClaw / Replies
- OpenClaw / Opt-Out
- OpenClaw / Bounces
- OpenClaw / Human Review

Drafted but unsent messages should use:

- OpenClaw / Drafted
- OpenClaw / Approved to Send

Sent mail should use:

- OpenClaw / Sent

## Classifications

- interested_call
- interested_send_more
- not_now
- wrong_person
- refer_to_colleague
- unsubscribe
- negative
- legal_compliance_question
- pricing_question
- integration_question
- partnership_question
- security_question
- unclear
- bounce

## Handling Rules

All replies may be summarized and drafted internally.

No reply may be sent automatically until Kyle approves exact response templates and authority boundaries.

Immediate Kyle review is required for:

- interested_call
- interested_send_more
- legal_compliance_question
- pricing_question
- integration_question
- partnership_question
- security_question
- unclear
- negative

Suppression update is required before any future sends for:

- unsubscribe
- do-not-contact request
- hard bounce
- privacy objection

## Reply Receipt Fields

Each triaged reply should record:

- reply_id
- received_at
- sender
- company if known
- campaign_id if known
- classification
- summary
- risk_notes
- owner
- next_safe_action
- approval_required
- artifact_pointer
