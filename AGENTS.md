# Repository Guidelines

## Project Structure & Module Organization

Profusion is a Python 3.11 orchestrator with a Vite/React dashboard:

- `src/orchestrator/` contains the CLI, FastAPI backend, state machine, SQLite access, read models, and vendor adapters.
- `tests/` contains pytest coverage for pipeline stages, API contracts, retries, scheduling, publishing, and status behavior.
- `dashboard/` is the public Vite/React app deployed by Netlify.
- `docs/` holds architecture notes, runbooks, deployment wrap-ups, and directional specs.
- `configs/` and `data/topics/` contain example runtime inputs.
- `vendor/` contains MoneyPrinterTurbo and MoneyPrinterV2 integrations. Prefer adapter changes in `src/orchestrator/adapters/` before touching vendored code.

## Build, Test, and Development Commands

- `uv sync` installs the Python environment from `pyproject.toml` and `uv.lock`.
- `uv run pytest` runs the orchestrator test suite.
- `uv run profusion status` checks the local queue state.
- `uv run profusion check-env` validates tools and configured services.
- `uv run profusion smoke --offline` runs fixture-backed operator verification without live vendors.
- `uv run profusion serve` starts the local API/operator backend.
- `cd dashboard && pnpm install` installs frontend dependencies.
- `cd dashboard && pnpm dev --host 127.0.0.1` starts the Vite dev server.
- `cd dashboard && pnpm lint && pnpm build` verifies the dashboard and Netlify build output.

## Coding Style & Naming Conventions

Use typed, explicit Python in `src/orchestrator/`; keep external-service behavior behind adapters and stable read contracts in `read_models.py`. Follow 4-space Python indentation, snake_case functions, PascalCase Pydantic models, and clear Typer command names. Frontend code uses PascalCase components, `useX` hooks, and API helpers under `dashboard/src/api/`.

## Testing Guidelines

Add or update pytest files as `tests/test_<area>.py` for backend behavior. Prefer contract tests for JSON/API changes and state transition tests for pipeline logic. For frontend changes, run `pnpm lint` and `pnpm build`. Release-facing changes should pass the offline smoke path.

## Commit & Pull Request Guidelines

Recent commits use concise milestone or scope prefixes, for example `M7 QC fixes: ...` and `Add Profusion AI Netlify website deployment`. Keep commits focused and imperative. Pull requests should describe behavior changes, list verification commands, call out live-service assumptions, and include screenshots for visible dashboard or website changes.

## Security & Configuration Tips

Do not commit `.env`, API keys, generated databases, or render artifacts. Start from `.env.example`, keep vendor credentials local, and document any new required setting in README or the relevant runbook.
