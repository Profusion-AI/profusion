# M8-GTM Path C Turnkey Reproduction

Date: 2026-05-18
Status: Local reproduction completed; included in documentation-only QC branch.

## Purpose

This note records what happened when Codex cloned the live
`Profusion-AI/profusion` repository and attempted Path C: regenerate the M8-GTM
Customer Trust Triage Receipt before the HyperFrames assessment.

The goal was to distinguish two questions:

1. Does the copied alpha artifact bundle in `Downloads/` behave like a turnkey
   executable project?
2. Does the actual live Profusion repository behave like a turnkey executable
   project when cloned locally?

## Repository Context

Repository cloned:

```text
https://github.com/Profusion-AI/profusion
```

Local checkout:

```text
/home/kyle-home/profusion
```

Branch used for this note:

```text
codex/path-c-turnkey-repro-20260518
```

Clone state:

```text
main at a09ca00 chore: merge GitHub license root
```

The live repository includes the executable project metadata missing from the
copied alpha artifact bundle:

```text
pyproject.toml
uv.lock
.python-version
src/orchestrator/cli.py
src/orchestrator/m8_gtm/
examples/m8/support-triage-human-review/
tests/test_m8_gtm_receipt_harness.py
```

## GitHub CLI Readiness

`gh` is installed and authenticated in this terminal.

Observed status:

```text
gh version 2.92.0
Logged in to github.com account Profusion-AI
Git operations protocol: https
Token scopes include repo and workflow
viewerPermission for Profusion-AI/profusion: ADMIN
```

This branch is prepared for a documentation-only commit and push.

Git committer identity was initially not configured in this fresh clone. For
this documentation branch, the repo-local identity was set from the
authenticated GitHub account:

```text
git config user.name -> Profusion-AI
git config user.email -> kyle.greenwell@gmail.com
```

## Exact Path C Attempt

Command attempted from the live repo root:

```bash
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-path-c-turnkey-exact
```

Initial result:

```text
bash: uv: command not found
```

Interpretation:

The live repo is structurally executable, but this terminal image did not have
`uv` installed at the start of the test. That is an environment bootstrap edge,
not a missing-repo-files edge.

## Tool Bootstrap

User-space bootstrap command:

```bash
python3 -m pip install --user uv
```

Observed result:

```text
Successfully installed uv-0.11.15
/home/kyle-home/.local/bin/uv
uv 0.11.15 (x86_64-unknown-linux-gnu)
```

System Python was:

```text
Python 3.14.4
```

The project requires:

```text
>=3.11,<3.12
```

On the rerun, `uv` downloaded and used:

```text
CPython 3.11.15
```

This is expected `uv` behavior and confirms that the repo can recover from an
incompatible system Python if `uv` itself is available.

## Successful Regeneration

Rerun command:

```bash
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-path-c-turnkey-exact-after-uv
```

Observed result:

```text
Loaded workflow fixture: support-triage-human-review
Loaded run artifacts: routine_invoice, sensitive_billing_complaint
Validated artifact manifest
Generated M8 observation
Generated workflow receipt JSON
Generated workflow receipt Markdown
Generated workflow receipt HTML
Receipt: /tmp/profusion-path-c-turnkey-exact-after-uv/support-triage-human-review/receipt-20260518T221728Z-f875b1d8/workflow_receipt.html
```

Generated packet files:

```text
artifact_manifest.json
m8_observation.json
workflow_receipt.json
workflow_receipt.md
workflow_receipt.html
artifacts/workflow.json
artifacts/run_001_routine_invoice/*
artifacts/run_002_sensitive_billing_complaint/*
```

## Negative Path Check

Command:

```bash
uv run profusion m8 demo not-a-real-workflow --output-dir /tmp/profusion-path-c-turnkey-unknown-workflow
```

Observed result:

```text
Unknown M8 demo workflow 'not-a-real-workflow'. Supported:
support-triage-human-review
```

Exit code:

```text
1
```

This matches the documented runbook behavior.

## Verification Commands

Targeted M8 harness tests:

```bash
uv run pytest tests/test_m8_gtm_receipt_harness.py -q
```

Result:

```text
8 passed in 0.08s
```

Nearby receipt and measurement tests:

```bash
uv run pytest tests/test_receipts.py tests/test_measurements.py tests/test_m8_gtm_receipt_harness.py -q
```

Result:

```text
26 passed in 0.87s
```

Full backend suite:

```bash
uv run pytest -q
```

Result:

```text
201 passed in 2.46s
```

## Drift Compared With Alpha Packet

Compared against the alpha packet:

```text
/home/kyle-home/Downloads/profusion-m8-gtm-p0-artifacts-2026-05-18/data/receipts/m8-gtm/support-triage-human-review/receipt-20260518T214605Z-aef389af/
```

`workflow_receipt.json` matched after removing volatile generated fields:

```text
receipt_id
generated_at
source_manifest_id
source_observation_id
```

`m8_observation.json` matched after removing volatile generated fields:

```text
observation_id
observed_at
source_manifest_id
```

`artifact_manifest.json` matched after removing volatile generated fields and
artifact source paths, except for the expected local absolute fixture path:

```diff
- "source_fixture_path": "/home/kyle/profusion/examples/m8/support-triage-human-review"
+ "source_fixture_path": "/home/kyle-home/profusion/examples/m8/support-triage-human-review"
```

Interpretation:

The regenerated receipt claim content matches the alpha packet. The remaining
differences are expected IDs, timestamps, output paths, and local absolute
source paths.

## Edge Case Discrepancies

### 1. Copied alpha bundle is not turnkey executable

The copied bundle in `Downloads/` contains source and fixtures, but lacks repo
metadata such as `pyproject.toml`, `uv.lock`, and the repo-level CLI/config
surface. It can regenerate only through a lower-level `PYTHONPATH` harness call
with explicit `fixture_root` and `output_root`.

### 2. Live repo is turnkey after `uv` exists

The cloned GitHub repo can regenerate the receipt through the documented CLI
path after `uv` is installed. `uv` correctly provisions Python 3.11 even though
the host system Python is 3.14.

### 3. Absolute paths reduce byte-for-byte portability

The generated `artifact_manifest.json` records local absolute paths such as
`source_fixture_path` and per-artifact `source_path`. This is useful for local
traceability but means packet manifests are not byte-identical across machines
or checkout locations.

For HyperFrames and demo-claim traceability, this is acceptable. For future
cross-machine deterministic receipts, consider adding repo-relative source path
fields or making absolute source paths explicitly non-canonical.

### 4. Default output path writes ignored local artifacts

The runbook default writes under:

```text
data/receipts/m8-gtm/support-triage-human-review/<receipt_id>/
```

That path is intentionally ignored by git. For assessment and CI-style
reproduction, `--output-dir /tmp/...` is cleaner because it avoids local
workspace clutter.

### 5. Full pytest creates ignored local logs

The full test suite produced ignored runtime files under `data/logs/`, plus
standard ignored caches and `.venv/`. This does not affect git-tracked state,
but it is worth knowing when running the baseline in a fresh checkout.

## Readiness Verdict

The live GitHub repository is ready for Path C-style local reproduction once
`uv` is available. The receipt regeneration path, negative workflow handling,
targeted tests, nearby tests, and full backend suite all passed in this local
clone.

The main discrepancy from the copied alpha bundle is not code behavior; it is
project packaging context. The copied bundle is an evidence snapshot plus
partial source. The live repo is the correct place to assess turnkey execution.

## Recommendation For HyperFrames Assessment

Proceed with the HyperFrames assessment using the receipt packet as the video
claim source, and document this Path C result as pipeline evidence:

```text
actual repo clone -> uv bootstrap -> profusion m8 demo -> regenerated receipt -> tests pass
```

For any future GitHub push, review this note first, then commit it with the
assessment artifacts or fold the findings into a broader P1 HyperFrames
capabilities report.
