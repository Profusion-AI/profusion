# Cron and TaskFlow Notes

Status: interface found; no jobs scheduled
Owner: OpenClaw drafts, Kyle approves schedules
Last updated: 2026-05-17

## Current Runtime Findings

OpenClaw CLI is available at /home/kyle/.npm-global/bin/openclaw.

Cron interface:

- openclaw cron add
- openclaw cron disable
- openclaw cron edit
- openclaw cron enable
- openclaw cron get
- openclaw cron list
- openclaw cron rm
- openclaw cron run
- openclaw cron runs
- openclaw cron show
- openclaw cron status

Current cron state checked on 2026-05-17: no cron jobs.

Task and TaskFlow inspection:

- openclaw tasks list
- openclaw tasks audit
- openclaw tasks maintenance
- openclaw tasks show
- openclaw tasks cancel
- openclaw tasks flow list
- openclaw tasks flow show
- openclaw tasks flow cancel

Current task state checked on 2026-05-17: no background tasks, no TaskFlows, no audit findings.

Canonical TaskFlow runtime API from local skill docs:

- api.runtime.tasks.flow is canonical
- api.runtime.taskFlow is an alias
- use fromToolContext(ctx) when trusted tool context has sessionKey
- use bindSession({ sessionKey, requesterOrigin }) when the binding layer resolved owner/delivery context

Managed lifecycle:

1. createManaged
2. runTask
3. setWaiting
4. resume
5. finish or fail
6. requestCancel or cancel

## Approved Starting Cron Ideas

Do not schedule yet. Draft internal-only cron candidates first:

- daily owner brief
- stale task review
- unread reply triage
- repo health/status digest
- lead research draft queue

Draft-only outbound cron candidates:

- find leads
- enrich context
- score fit
- draft candidate outreach
- create approval record

No send cron until sender identity, suppression, opt-out, approval IDs, daily cap, send ledger, reply/bounce monitoring, and Kyle campaign approval all exist.

