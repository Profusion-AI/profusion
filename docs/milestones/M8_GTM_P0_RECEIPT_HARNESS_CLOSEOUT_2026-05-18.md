# M8-GTM P0 Receipt Harness Closeout

Date: 2026-05-18
Status: P0 implemented and verified

## What Was Implemented

- Added the fixture-backed Customer Trust Triage Receipt source packet under
  `examples/m8/support-triage-human-review/`.
- Added `orchestrator.m8_gtm` with fixture loading, validation, atomic packet
  generation, artifact hashing, M8 observation construction, workflow receipt
  JSON construction, Markdown rendering, and escaped HTML rendering.
- Added `profusion m8 demo support-triage-human-review`.
- Added P0 tests in `tests/test_m8_gtm_receipt_harness.py`.
- Added the runbook at `docs/runbooks/m8_gtm_n8n_receipt_harness.md`.
- Updated the approved spec with Kyle approval, scope lock, evidence mode, and
  no-claims policy.

## Verification

Red test check:

```text
uv run pytest tests/test_m8_gtm_receipt_harness.py -q
-> failed before implementation with:
ModuleNotFoundError: No module named 'orchestrator.m8_gtm'
```

P0 demo command:

```text
uv run profusion m8 demo support-triage-human-review
-> exit 0
```

Final generated receipt:

```text
data/receipts/m8-gtm/support-triage-human-review/receipt-20260518T214605Z-aef389af/workflow_receipt.html
```

Targeted P0 tests:

```text
uv run pytest tests/test_m8_gtm_receipt_harness.py
-> 8 passed in 0.09s
```

Nearby regression tests:

```text
uv run pytest tests/test_receipts.py tests/test_measurements.py tests/test_m8_gtm_receipt_harness.py
-> 26 passed in 0.66s
```

Full backend baseline:

```text
uv run pytest
-> 201 passed in 3.01s
```

Offline smoke:

```text
uv run profusion smoke --offline
-> [ok] offline smoke passed
```

Whitespace check:

```text
git diff --check
-> exit 0
```

## Output Packet

Latest verified packet:

```text
data/receipts/m8-gtm/support-triage-human-review/receipt-20260518T214605Z-aef389af/
```

Required files present:

```text
artifact_manifest.json
m8_observation.json
workflow_receipt.json
workflow_receipt.md
workflow_receipt.html
artifacts/
```

The generated receipt includes:

- `evidence_mode`: `fixture_backed_local_demo`
- non-empty supported claims
- non-empty claims not supported
- non-empty limitations
- sensitive billing complaint human review event
- local fixture no-live-integration and no-live-send limitations

The output packet is ignored by git under `data/receipts/*`.

## Known Limitations

- This is a fixture-backed local demo, not live n8n execution.
- It does not prove Gmail, Slack, Google Sheets, HubSpot, or n8n API
  integration.
- It does not send customer messages.
- It does not prove the billing complaint is factually true.
- It does not certify compliance or provide legal assurance.
- It does not make support automation a product.

## Safe Next Step

Kyle should review:

- `workflow_receipt.html`
- `workflow_receipt.md`
- `workflow_receipt.json`
- `m8_observation.json`
- `artifact_manifest.json`
- `docs/runbooks/m8_gtm_n8n_receipt_harness.md`

If the packet is credible enough, P1 can start as a receipt-derived
HyperFrames explainer video. The video must not introduce claims that are not
present in the receipt, observation, manifest, or storyboard generated from
those files.

## Deferred To P1/P2

P1:

- `demo_storyboard.md`
- `hyperframes_video_manifest.json`
- `customer_trust_triage_receipt.mp4`

P2:

- optional read-only cockpit visibility for receipt summary, artifact list,
  observation status, supported claims, and unsupported claims

Still out of scope:

- approval buttons
- mutation logic
- scheduling or publishing controls
- public website changes
- live integration claims
