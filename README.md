# Profusion

B2B workflow-trust and evidence-receipt system. Profusion helps operators define evidence boundaries, preserve workflow artifacts, apply human review gates, state limitations, and produce reviewer-readable receipts for AI-assisted work.

## Quick start

For the active P0 receipt path, vendor submodules are not required:

```bash
git clone https://github.com/Profusion-AI/profusion.git ~/profusion
cd ~/profusion
scripts/bootstrap_uv.sh
scripts/path_c_smoke.sh
```

Use `git clone --recurse-submodules` only when intentionally inspecting the
legacy MoneyPrinter render/publish compatibility surface.

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
scripts/path_c_smoke.sh
uv run profusion m8 demo support-triage-human-review
uv run pytest tests/test_m8_gtm_receipt_harness.py
uv run pytest
uv run profusion smoke --offline
```

## Current milestone

P0 is implemented as a fixture-backed receipt harness. P1 is the
receipt-derived HyperFrames demo path and has not started. P2 cockpit
visibility is deferred and must remain read-only.

See `STATUS.md` for milestone progress, `docs/ACTIVE_SURFACES.md` for the
current repo boundary, and `docs/runbooks/` for operations, handoff, recovery,
and release checklists.

## Architecture

See `docs/architecture.md` for the layer diagram and `DECISIONS.md` for key design decisions.
