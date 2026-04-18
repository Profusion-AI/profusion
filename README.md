# Profusion

Semi-autonomous short-form educational media pipeline. Ingests topics, generates editorial briefs and scripts via Claude, renders video via MoneyPrinterTurbo, and publishes via MoneyPrinterV2.

## Quick start

```bash
git clone --recurse-submodules <repo-url> ~/profusion
cd ~/profusion
uv sync
cp .env.example .env   # add ANTHROPIC_API_KEY
uv run profusion check-env
uv run profusion status
```

## Current milestone

See `STATUS.md` for milestone progress and `docs/runbooks.md` for troubleshooting.

## Architecture

See `docs/architecture.md` for the layer diagram and `DECISIONS.md` for key design decisions.
