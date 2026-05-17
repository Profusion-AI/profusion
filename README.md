# Profusion

B2B workflow-trust and evidence-receipt system. Profusion helps operators define evidence boundaries, preserve workflow artifacts, apply human review gates, state limitations, and produce reviewer-readable receipts for AI-assisted work.

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

See `STATUS.md` for milestone progress and `docs/runbooks/` for operations,
handoff, recovery, and release checklists.

## Architecture

See `docs/architecture.md` for the layer diagram and `DECISIONS.md` for key design decisions.
