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

## Alpha receipt demo

The current alpha receipt path is fixture-backed and local:

```bash
uv run profusion m8 demo support-triage-human-review
```

It generates a Customer Trust Triage Receipt packet under the ignored output
root:

```text
data/receipts/m8-gtm/support-triage-human-review/<receipt_id>/
```

Source fixtures live in `examples/m8/support-triage-human-review/`. The demo
shows captured artifacts, an AI-assisted workflow boundary, a human review
event for the sensitive billing complaint case, an M8 observation, and supported
and unsupported receipt claims.

This alpha does not prove live n8n, Gmail, Slack, Google Sheets, HubSpot, or
customer-message execution. It does not certify compliance, provide legal
assurance, or make support automation a product.

Recommended QC commands:

```bash
uv run profusion m8 demo support-triage-human-review
uv run pytest tests/test_m8_gtm_receipt_harness.py
uv run pytest
uv run profusion smoke --offline
```

## Current milestone

See `STATUS.md` for milestone progress and `docs/runbooks/` for operations,
handoff, recovery, and release checklists.

## Architecture

See `docs/architecture.md` for the layer diagram and `DECISIONS.md` for key design decisions.
