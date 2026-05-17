# Gmail Alias Setup Checklist for agents@profusion.ai

Status: pending Kyle setup
Owner: Kyle
Last updated: 2026-05-17

## Goal

Configure agents@profusion.ai as the OpenClaw outbound operating lane inside Kyle's primary kyle@profusion.ai Google Workspace account.

## Precondition

agents@profusion.ai is an alternate email alias on the primary Workspace account, not a standalone Google account.

## Gmail Setup

1. Confirm Google Workspace alias exists for agents@profusion.ai on kyle@profusion.ai.
2. In Gmail, open Settings -> Accounts and Import -> Send mail as.
3. Add agents@profusion.ai as a send-as identity if it is not already present.
4. Set the displayed sender name Kyle wants for this lane.
5. Confirm Reply-To behavior. Recommended early posture: replies route back to the same monitored Gmail lane.
6. Send a test message from an external account to agents@profusion.ai.
7. Confirm the message arrives in Kyle's primary Gmail mailbox.
8. Send a test message from Gmail using From: agents@profusion.ai to an internal/test recipient.
9. Confirm the recipient sees accurate From and Reply-To.

## Labels

Create labels:

- OpenClaw / Inbox
- OpenClaw / Drafted
- OpenClaw / Approved to Send
- OpenClaw / Sent
- OpenClaw / Replies
- OpenClaw / Opt-Out
- OpenClaw / Bounces
- OpenClaw / Human Review

## Filters

Create Gmail filters:

- To: agents@profusion.ai -> apply OpenClaw / Inbox
- From: mailer-daemon or delivery status notifications -> apply OpenClaw / Bounces
- Contains unsubscribe/opt out/do not contact -> apply OpenClaw / Opt-Out and OpenClaw / Human Review
- Replies to outbound campaign threads -> apply OpenClaw / Replies

## DNS / Deliverability

Before live sending, verify:

- SPF includes the approved Google Workspace sender path
- DKIM is enabled for profusion.ai in Google Workspace
- DMARC exists for profusion.ai, at least monitor mode
- no unapproved sending service is spoofing profusion.ai
- commercial footer has a valid physical postal address
- opt-out method is present and operational

Useful commands or checks:

- dig TXT profusion.ai
- dig TXT google._domainkey.profusion.ai
- dig TXT _dmarc.profusion.ai
- send a manual test to a mailbox Kyle controls and inspect headers

## Current Blocker

Until this checklist is confirmed, OpenClaw must not draft messages that assume agents@profusion.ai is live.
