# Path C Turnkey Reproduction

Date: 2026-05-18
Status: Active P0/P0.1 bootstrap and smoke path.

## Purpose

Path C proves that a fresh Profusion checkout can regenerate the fixture-backed
Customer Trust Triage Receipt without live vendor services, external
credentials, or private data.

The path exercises this mechanism:

```text
local workflow artifacts -> M8 observation -> workflow receipt packet
```

It does not prove live n8n, Gmail, Slack, Google Sheets, HubSpot, customer
message sending, compliance certification, legal assurance, or production
readiness.

## Fresh Checkout

For the P0 receipt path, submodules are not required:

```bash
git clone https://github.com/Profusion-AI/profusion.git ~/profusion
cd ~/profusion
```

If legacy render/publish compatibility is being inspected, clone with
submodules intentionally:

```bash
git clone --recurse-submodules https://github.com/Profusion-AI/profusion.git ~/profusion
```

## Bootstrap `uv`

```bash
scripts/bootstrap_uv.sh
```

The script installs `uv` with `python3 -m pip install --user uv` if `uv` is not
already available.

## Run The Turnkey Smoke

```bash
scripts/path_c_smoke.sh
```

Optional output root:

```bash
scripts/path_c_smoke.sh /tmp/profusion-path-c-smoke
```

The smoke script:

1. checks or installs `uv`
2. runs `uv run profusion m8 demo support-triage-human-review`
3. writes output under `/tmp` by default
4. asserts that the required receipt packet files exist
5. runs `uv run pytest tests/test_m8_gtm_receipt_harness.py -q`

Required generated files:

```text
artifact_manifest.json
m8_observation.json
workflow_receipt.json
workflow_receipt.md
workflow_receipt.html
artifacts/
```

## Full Local Baseline

After Path C passes, run:

```bash
uv run pytest -q
uv run profusion smoke --offline
git diff --check
```

## Artifact Handling

Generated receipt packets, logs, exports, and explorations are local artifacts.
Keep them in ignored paths such as `/tmp`, `data/receipts/`, `data/private/`,
`data/explorations/`, or `outputs/`.

Do not commit raw generated receipt packets, local customer-like data, private
operator notes, prospect lists, or exploratory outputs unless Kyle explicitly
approves a sanitized public artifact.

## Common Failure

If the first run fails with:

```text
uv: command not found
```

run:

```bash
scripts/bootstrap_uv.sh
```

Then rerun the smoke command.
