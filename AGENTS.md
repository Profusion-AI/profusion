# Repository Guidelines

## Current Project Truth

As of 2026-05-17, Profusion is a B2B workflow-trust and evidence-receipt
system. Its near-term commercial lane is narrow: help a team turn one risky
AI-assisted workflow into reviewable evidence with captured artifacts, human
review gates, approvals, limitations, and a plain-English workflow receipt.

Current milestone state:

- M0-M6: complete.
- M7 Internal Operator Cockpit: locked and shipped as the internal operator
  surface.
- M7.5 Reviewer Evidence Packets: first file-first evidence packet slice is
  complete.
- M8 Measurement and Learning Loops: active as generic workflow outcome
  observations, not content-channel analytics.

The education/content creation system, Substack-specific publishing work,
MoneyPrinterTurbo continuity work, and MoneyPrinterV2 continuity work now live
in the separate `/home/kyle/attention-media-lab` project. Profusion may borrow
high-level learning-loop ideas from that work, but these are separate projects.
Do not reintroduce day-to-day workflow coupling between Profusion and Attention
Media Lab.

`render`, `publish`, and `publish-due` remain in Profusion only as legacy
sanitized demo compatibility paths connected to the original MPT/V2 heritage.
They are not the current B2B product promise. Prefer receipts, cockpit
read-models, workflow outcome observations, and private OpenClaw operating
artifacts for current work.

When a Profusion or MPT-era document is outdated or no longer matches this
renewed implementation vision, move it under the relevant `docs/archive/`
folder with context. Do not delete existing documentation.

## Project Structure & Module Organization

Profusion is a Python 3.11 orchestrator with a separate internal cockpit and
public website:

- `src/orchestrator/` contains the CLI, FastAPI backend, state machine,
  SQLite access, read models, measurements, receipts, and legacy vendor demo
  adapters.
- `tests/` contains pytest coverage for pipeline stages, API contracts,
  retries, scheduling, publishing compatibility, receipts, measurements, and
  status behavior.
- `apps/operator-cockpit/` contains the internal M7 operator cockpit.
- `dashboard/` contains the public Profusion AI Netlify website. Do not treat
  it as the operator cockpit.
- `docs/` holds active architecture notes, runbooks, milestone summaries, and
  business direction.
- `docs/archive/` holds outdated or superseded docs that must be preserved but
  should not steer current implementation.
- `ops/openclaw/` holds internal operating guardrails for draft-only business
  development and workflow-trust outreach preparation.
- `data/measurements/` contains ignored, file-first M8 workflow outcome
  observations.
- `data/private/` contains ignored private operating artifacts.
- `data/receipts/` contains ignored file-first M7.5 receipt/evidence packets.
- `configs/` and `data/topics/` contain example runtime inputs.
- `vendor/` contains legacy MoneyPrinterTurbo and MoneyPrinterV2 integrations.
  Keep V2 intact and logically connected to the original MPT tool, but treat
  active MPT/V2 evolution as Attention Media Lab work.

## Build, Test, and Development Commands

- `uv sync` installs the Python environment from `pyproject.toml` and
  `uv.lock`.
- `uv run pytest` runs the orchestrator test suite.
- `uv run profusion status` checks the local queue state.
- `uv run profusion check-env` validates tools and configured services.
- `uv run profusion smoke --offline` runs fixture-backed operator verification
  without live vendors.
- `uv run profusion serve --dev` starts the local API/operator backend.
- `uv run profusion measure --help` shows the M8 workflow outcome observation
  command group.
- `uv run profusion measure record --help` shows the observation recording
  contract before writing measurement artifacts.
- `uv run profusion receipt --help` shows the reviewer receipt command group.
- `uv run profusion render --help`, `uv run profusion publish --help`, and
  `uv run profusion publish-due --help` are legacy sanitized demo
  compatibility paths only.

## Operator Cockpit Commands

- `cd apps/operator-cockpit && corepack pnpm install` installs cockpit
  dependencies.
- `cd apps/operator-cockpit && corepack pnpm dev --host 127.0.0.1` starts the
  internal cockpit.
- `cd apps/operator-cockpit && corepack pnpm test` runs cockpit tests.
- `cd apps/operator-cockpit && corepack pnpm lint` verifies cockpit lint.
- `cd apps/operator-cockpit && corepack pnpm build:netlify` builds the static
  cockpit preview.
- `cd apps/operator-cockpit && corepack pnpm smoke:static` verifies the static
  cockpit snapshot.

## Public Website Commands

- `cd dashboard && corepack pnpm install` installs public website
  dependencies.
- `cd dashboard && corepack pnpm dev --host 127.0.0.1` starts the public
  website dev server.
- `cd dashboard && corepack pnpm lint` verifies the public website.
- `cd dashboard && corepack pnpm build` builds the public website.

## Coding Style & Naming Conventions

Use typed, explicit Python in `src/orchestrator/`; keep external-service
behavior behind adapters and stable read contracts in `read_models.py`. Follow
4-space Python indentation, snake_case functions, PascalCase Pydantic models,
and clear Typer command names. Frontend code uses PascalCase components, `useX`
hooks, and API helpers under the app-specific `src/api/` folder.

## Testing Guidelines

Add or update pytest files as `tests/test_<area>.py` for backend behavior.
Prefer contract tests for JSON/API changes and state transition tests for
pipeline logic. For operator cockpit changes, run the cockpit test/lint/build
commands above. For public website changes, run the dashboard lint/build
commands above. Release-facing changes should pass the offline smoke path.

## Current M8 Guardrails

Allowed:

- improve manual workflow outcome observation recording
- improve observation summaries and read models
- improve `/measurements` cockpit clarity
- seed realistic demo observations
- document the M8 operator runbook
- write M8 closeout notes
- rerun the full verification baseline
- keep old content-format measurement keys only as compatibility aliases

Not allowed unless explicitly reopened:

- Substack-specific commands, services, package helpers, RSS verification, or
  publication artifacts inside Profusion
- direct hidden Substack write endpoints
- authenticated Substack dashboard scraping
- ungated browser publish automation
- committing Substack cookies, sessions, passwords, or API keys
- platform API metric imports
- automated optimization
- model feedback loops
- buyer-facing measurement dashboard
- public website changes
- Work Trust scenario execution
- hiring/candidate ranking language
- AI observability platform claims

## OpenClaw and Business Development Guardrails

OpenClaw may research, score, draft, classify, brief, and log inside private or
internal repo paths. It may not send external email, follow-ups, LinkedIn
messages, public posts, or campaigns without Kyle approval of the sender lane,
campaign, recipient list, copy family, daily cap, suppression/unsubscribe
process, and send ledger format.

Use the current commercial frame unless newer verified docs supersede it:

- Category: AI workflow trust / AI workflow reliability.
- First offer: founder-led Profusion Evidence Receipt Pilot or Workflow
  Reliability Session.
- Mechanism: one workflow, one evidence boundary, captured artifacts, human
  review gates, approvals, stated limitations, and reviewer-readable workflow
  receipt.

Do not pitch Profusion as generic responsible AI, AI observability, compliance
automation, recruiting automation, deepfake detection, certification, or a
turnkey platform. Do not imply existing clients, revenue, certifications, legal
assurance, or production-scale capability unless verified in current docs.

## Commit & Pull Request Guidelines

Recent commits use concise milestone or scope prefixes, for example
`M7 QC fixes: ...` and `Add Profusion AI Netlify website deployment`. Keep
commits focused and imperative. Pull requests should describe behavior changes,
list verification commands, call out live-service assumptions, and include
screenshots for visible dashboard or website changes.

## Security & Configuration Tips

Do not commit `.env`, API keys, generated databases, private operating data, or
render artifacts. Start from `.env.example`, keep vendor credentials local, and
document any new required setting in README or the relevant runbook.
