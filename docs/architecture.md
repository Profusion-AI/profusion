# Profusion Architecture

## 2026-05-17 Project Boundary

Profusion's active architecture is workflow trust and evidence receipts. MoneyPrinterTurbo and MoneyPrinterV2 have moved to `/home/kyle/attention-media-lab` as education/content tooling. Existing Profusion render/publish code is legacy/demo infrastructure until a later cleanup removes or replaces it with fixture-backed demo receipts.

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Operator / Human                          │
│              profusion <command> [options]                   │
└───────────────────────────┬─────────────────────────────────┘
                            │ CLI (typer)
┌───────────────────────────▼─────────────────────────────────┐
│                   Orchestration Layer                         │
│  src/orchestrator/                                           │
│  ├── cli.py          — operator commands                     │
│  ├── state.py        — content state machine + guards        │
│  ├── db.py           — SQLite persistence (content.db)       │
│  ├── models.py       — Pydantic typed entities               │
│  ├── read_models.py  — inspection/JSON dashboard contracts   │
│  ├── retry.py        — conservative retry orchestration      │
│  ├── diagnostics.py  — redacted failure logs + metadata      │
│  ├── measurements.py — file-first workflow observations      │
│  ├── config.py       — .env loader                          │
│  └── adapters/                                               │
│      ├── claude.py   — Anthropic SDK (LLM, all gen work)    │
│      └── firecrawl.py— Firecrawl ingest adapter (M1)       │
└──────────┬──────────────────────────────────────────────────┘
           │ workflow state, evidence, receipts, observations
┌──────────▼──────────────────────────────────────────────────┐
│                     Evidence Storage Layer                    │
│  data/                                                       │
│  ├── content.db      — SQLite: all pipeline state           │
│  ├── evidence/       — reviewer-facing evidence artifacts   │
│  ├── receipts/       — file-first receipt packets           │
│  ├── approvals/      — approval records                     │
│  ├── measurements/   — file-first M8 measurement observations│
│  └── logs/           — agent action + failure logs          │
└────────────────────────────────────────────────────────────┘
           │ read models / API contracts
┌──────────▼──────────────────────────────────────────────────┐
│                 Internal Operator Cockpit                    │
│  apps/operator-cockpit/                                      │
│  • queue, item detail, jobs, artifacts, receipts, handoff    │
│  • safe retry only; approval/publish remain command-gated    │
└────────────────────────────────────────────────────────────┘
```

Historical render/publish adapters and generated media artifacts remain legacy
demo infrastructure only. MoneyPrinterTurbo and MoneyPrinterV2 have moved to
`/home/kyle/attention-media-lab` as education/content tooling.

## Data Flow (happy path)

```
1. operator defines a workflow and evidence boundary
   → source context, scope, limitations, and expected review gates recorded

2. Profusion preserves workflow artifacts
   → artifacts, logs, approvals, and handoff context stay inspectable

3. human review gates are applied
   → reviewer decision and limitation language are attached to the workflow

4. receipt draft is generated
   → reviewer-readable evidence packet explains what happened and what was not proven

5. receipt lifecycle is reviewed separately from work approval
   → draft → reviewed → approved_for_packet → delivered

6. API/read models expose operator state
   → cockpit reads queue, item detail, artifacts, receipts, logs, and handoff

7. M6/M7 operator hardening
   → inspect / jobs / artifacts / approvals / handoff / retry
   → stable JSON contracts for the internal operator cockpit

8. M8 workflow outcome observations
   → manual/file-first observation captured with generic comparison dimensions
   → status: measured → archived
```

Media/content flows may remain only as sanitized demo workflows for explaining
receipt mechanics. Real education/content operations now belong to
`/home/kyle/attention-media-lab`.

## Adapter Boundaries

Adapters are the only place orchestrator code touches external services.
All adapters expose a minimal typed interface. Legacy render/publish adapters
are demo infrastructure after the split; active product architecture should
center workflow state, evidence boundaries, receipts, read models, and the
operator cockpit.

## Key Design Decisions

See DECISIONS.md for full rationale on:
- Python 3.11 for orchestrator / split vendor envs
- Git submodule strategy
- LLM routing through Claude (not Turbo's internal LLM)
- State machine canonical source (PRD §13)
- Edge-TTS as default TTS engine
- M6 read-model contracts and retry lineage
- 2026-05-17 split boundary for historical Substack demo infrastructure
