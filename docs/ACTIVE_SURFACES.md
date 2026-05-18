# Active Surfaces

Date: 2026-05-18
Status: Active repo map after M8-GTM QC audit.

## Controlling Rule

```text
receipt-real first -> HyperFrames-rendered second -> cockpit-visible later
```

Profusion is a B2B workflow-trust and evidence-receipt system. It is not the
education/content engine, a publishing system, generic AI observability,
compliance automation, or a turnkey SaaS platform.

## Active For P0 / P0.1

These surfaces are the current implementation lane:

- `src/orchestrator/m8_gtm/` - fixture-backed M8-GTM receipt harness.
- `examples/m8/support-triage-human-review/` - Customer Trust Triage Receipt
  source fixture.
- `tests/test_m8_gtm_receipt_harness.py` - P0 receipt harness contract tests.
- `docs/runbooks/m8_gtm_n8n_receipt_harness.md` - current P0 runbook.
- `docs/runbooks/path_c_turnkey_reproduction.md` - fresh-clone reproduction
  path.
- `scripts/bootstrap_uv.sh` and `scripts/path_c_smoke.sh` - local/CI bootstrap
  and smoke checks.
- `.github/workflows/ci.yml` - first public repo CI safety net.

P0/P0.1 must keep using bounded evidence language: local fixture artifacts,
human review boundary, generated workflow receipt, supported claims,
unsupported claims, limitations, and next review.

## Specified But Not Started

P1 is the receipt-derived HyperFrames demo video path. It should generate a
storyboard and video manifest from P0 receipt outputs before rendering any MP4.

Required P1 artifacts when implementation starts:

- `demo_storyboard.md`
- `hyperframes_video_manifest.json`
- `customer_trust_triage_receipt.mp4`

Every on-screen claim must trace to one of:

- `workflow_receipt.json`
- `workflow_receipt.md`
- `m8_observation.json`
- a storyboard generated from those files

## Deferred / Read-Only Only

P2 cockpit visibility is optional. If it starts, it must be read-only and must
not expose approval buttons, scheduling, publishing, retry, or other mutation
controls for buyer-facing demos.

Allowed only after explicit P2 kickoff:

- `apps/operator-cockpit/`
- receipt summary and artifact-list views
- supported/unsupported claim views
- read-only receipt/measurement API routes

## Frozen For P1

These surfaces remain in the repo for historical compatibility and tests, but
they are not part of the P0/P0.1/P1 path:

- `vendor/MoneyPrinterTurbo`
- `vendor/MoneyPrinterV2`
- `src/orchestrator/adapters/turbo.py`
- `src/orchestrator/adapters/v2.py`
- render, publish, schedule, and publish-due CLI paths
- legacy content-generation pipeline docs

Do not extend these surfaces for Profusion P1. Real MoneyPrinterTurbo/V2
continuity now belongs in `/home/kyle/attention-media-lab`.

Physical removal of the vendor submodules and legacy command code is a
separate exec-level decision. It should happen only after the remaining
historical tests, milestone docs, and compatibility promises are intentionally
retired or moved.

## Public Website Boundary

`dashboard/` is the public Profusion website. Do not change it during the
M8-GTM cleanup/P0.1 lane unless a breakage fix is explicitly approved.

## Private And Local Artifacts

Generated receipts, logs, exports, source packs, drafts, local explorations,
and scratch outputs belong in ignored paths:

- `data/receipts/`
- `data/measurements/`
- `data/private/`
- `data/exports/`
- `data/explorations/`
- `data/source_packs/`
- `data/drafts/`
- `tmp/`
- `scratch/`
- `explorations/`
- `outputs/`

High-level plans and bounded milestone notes may remain public. Raw local
artifacts, prospect data, private operating notes, and exploratory outputs
should stay ignored.
