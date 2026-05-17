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
│  ├── measurements.py — file-first M8 observations/comparisons│
│  ├── substack_publish.py — M8 Substack package/readback loop │
│  ├── config.py       — .env loader                          │
│  └── adapters/                                               │
│      ├── claude.py   — Anthropic SDK (LLM, all gen work)    │
│      ├── turbo.py    — MoneyPrinterTurbo adapter (M2)       │
│      ├── v2.py       — MoneyPrinterV2 adapter (M4)         │
│      ├── substack.py — manual Substack package/RSS adapter  │
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
│  ├── measurements/   — file-first M8 measurement observations│
│  ├── substack/       — file-first Substack package/readback  │
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

8. M6 operator hardening
   → inspect / jobs / renders / approvals / handoff / retry
   → stable JSON contracts for the internal operator cockpit

9. M8 Substack spike
   → local source/voice artifacts can guide a long-form Substack draft
   → substack import-article requires explicit human content approval
   → substack package writes copy/paste publication artifacts
   → human publishes in Substack web editor
   → substack publish records the URL after explicit confirmation
   → substack verify checks the recorded URL through public RSS readback
   → receipt draft can include the Substack publish evidence

10. M8 measure
   → manual/file-first observation captured with comparison dimensions
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
- M6 read-model contracts and retry lineage
- M8 Substack publishing/evidence spike boundary
