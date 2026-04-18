# Profusion Architecture

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
│  ├── config.py       — .env loader                          │
│  └── adapters/                                               │
│      ├── claude.py   — Anthropic SDK (LLM, all gen work)    │
│      ├── turbo.py    — MoneyPrinterTurbo adapter (M2)       │
│      ├── v2.py       — MoneyPrinterV2 adapter (M4)         │
│      └── firecrawl.py— Firecrawl ingest adapter (M1)       │
└──────────┬───────────────────────────┬───────────────────────┘
           │ render(script, profile)   │ publish(video, metadata)
┌──────────▼──────────┐  ┌────────────▼──────────────────────┐
│  MoneyPrinterTurbo  │  │         MoneyPrinterV2             │
│  vendor/...Turbo/   │  │       vendor/...V2/                │
│                     │  │                                    │
│  • script → video   │  │  • YouTube Shorts upload           │
│  • Edge-TTS voice   │  │  • scheduler/cron                  │
│  • subtitles        │  │  • optional Post Bridge            │
│  • background music │  │    (TikTok, Instagram)             │
│  • NVENC encoding   │  │                                    │
└──────────┬──────────┘  └────────────┬──────────────────────┘
           │                          │
┌──────────▼──────────────────────────▼──────────────────────┐
│                     Storage Layer                            │
│  data/                                                       │
│  ├── content.db      — SQLite: all pipeline state           │
│  ├── renders/        — MP4 artifacts + manifests            │
│  ├── scripts/        — script text files                    │
│  ├── topics/         — raw topic intake files               │
│  ├── approvals/      — approval records                     │
│  ├── publish_logs/   — per-publish-job logs                 │
│  └── logs/           — agent action + failure logs          │
└────────────────────────────────────────────────────────────┘
```

## Data Flow (happy path)

```
1. operator: profusion ingest --topic "..."
   → content_items row created (status: idea)

2. profusion plan
   → claude.generate() → content brief
   → content_briefs row created (status: planned)

3. profusion render
   → claude.generate() → scripts
   → script_variants rows created (status: scripted)
   → turbo.render(script) → MP4 artifact
   → render_jobs row (status: rendered)

4. profusion qa
   → technical + editorial checks
   → status: qa_passed or qa_failed

5. profusion approve
   → approval_records row
   → status: approved

6. profusion schedule
   → publish_jobs row scheduled
   → status: scheduled

7. profusion publish
   → v2.publish(video, metadata)
   → status: published, URL stored

8. (future M6) measure
   → performance captured
   → status: measured → archived
```

## Adapter Boundaries

Adapters are the only place orchestrator code touches vendor repos.
All adapters expose a minimal typed interface. Neither Turbo nor V2
internals are imported directly outside their adapter module.

This means either vendor can be replaced by editing one file.

## Key Design Decisions

See DECISIONS.md for full rationale on:
- Python 3.11 for orchestrator / split vendor envs
- Git submodule strategy
- LLM routing through Claude (not Turbo's internal LLM)
- State machine canonical source (PRD §13)
- Edge-TTS as default TTS engine
