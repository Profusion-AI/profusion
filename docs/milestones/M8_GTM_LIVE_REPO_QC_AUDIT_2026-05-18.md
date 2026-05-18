# M8-GTM Live Repo QC Audit

Date: 2026-05-18
Status: Documentation-only QC audit for follow-up implementation.
Verdict: YELLOW-GREEN, with a specific turnkey edge.

## Executive Verdict

Profusion's P0 receipt harness is real enough to respect. The repo now has a
concrete, reproducible, fixture-backed proof loop:

```text
local workflow artifacts -> bounded M8 observation -> workflow receipt
```

The receipt language is appropriately careful about what it does and does not
prove. That is the right trust posture.

Profusion is not P1-ready in the strict sense yet. P1 is not "the repo works."
P1 is the receipt-derived HyperFrames demo video path, with claim drift
controls and render metadata.

Current hierarchy:

```text
P0 = CLI + durable artifacts + generated receipt
P1 = HyperFrames-rendered demo video from receipt outputs
P2 = optional read-only cockpit visibility
```

The controlling rule remains:

```text
receipt-real first, HyperFrames-rendered second, cockpit-visible later
```

P0 is done. P1 is specified. P1 is not yet implemented.

The strongest conclusion is that the core mechanism is finally pointed at the
right business. The weakest conclusion is that the repo still carries too much
historical product surface area for a buyer-facing P1 demo sprint.

## Evidence Reviewed

This audit incorporates:

- the live local clone of `Profusion-AI/profusion`
- the Path C reproduction note in
  `docs/milestones/M8_GTM_PATH_C_TURNKEY_REPRODUCTION_2026-05-18.md`
- the current P0/P1 milestone docs and runbooks
- local checks of CI presence, API routes, state-machine surfaces, environment
  checks, third-party license docs, and M8 receipt harness behavior

This branch intentionally makes no implementation changes.

## What Is Genuinely Strong

The P0 scope is disciplined. The spec locks P0 to a fixture-backed receipt
harness and says P1/P2 must not delay it. It also keeps the public website,
education/content engine, and broader cockpit work out of scope.

The P0 runbook is unusually honest. It says what is real, what is mocked, and
what is not proven. The no-claims list is important: no live n8n proof, no
Gmail/Slack/Sheets/HubSpot proof, no live customer messages, no compliance
certification, no legal assurance, no proof that the billing complaint is
factually true, and no claim that support automation is the product.

The M8 CLI surface is simple and legible:

```bash
uv run profusion m8 demo <workflow_slug> --output-dir <output_dir>
```

It delegates to `generate_demo_packet`, catches domain errors, emits clear
progress lines, and prints the HTML receipt path.

The M8 receipt renderer escapes HTML-derived text. The HTML renderer uses
`html.escape` on title, IDs, evidence boundary, list items, artifacts, key/value
output, and next recommended review.

The third-party licensing posture is visible. The repo documents
MoneyPrinterTurbo as MIT and MoneyPrinterV2 as AGPL-3.0, with an explicit note
that legal review is required before any public SaaS deployment involving V2
components.

## Top Defects And Recommended Fixes

### 1. P1 Is Specified But Not Shipped

P0 is implemented and verified; P1 remains deferred. The docs say P1 requires:

```text
demo_storyboard.md
hyperframes_video_manifest.json
customer_trust_triage_receipt.mp4
```

They also say every text claim shown in the video must be sourced from
`workflow_receipt.json`, `workflow_receipt.md`, `m8_observation.json`, or a
storyboard generated from those files.

The next implementation should not be "make a cool video." It should be a
claim-controlled P1 artifact compiler.

Recommended implementation files:

```text
src/orchestrator/m8_gtm/p1_storyboard.py
src/orchestrator/m8_gtm/p1_manifest.py
tests/test_m8_gtm_p1_storyboard.py
tests/test_m8_gtm_p1_manifest.py
```

Recommended CLI shape:

```bash
uv run profusion m8 video support-triage-human-review \
  --receipt-dir <p0-packet> \
  --output-dir <p1-output> \
  --render-mode auto
```

Storyboard scenes should include explicit source references:

```json
{
  "scene_id": "sensitive_review_boundary",
  "onscreen_text": "Sensitive billing complaint triggered human review.",
  "source_refs": [
    "workflow_receipt.where_human_review_entered[0]",
    "m8_observation.human_review_events[0]"
  ]
}
```

Add a banned-claims list for P1:

```text
certified
fully verified
compliance approved
live n8n
live Gmail
customer sent
production ready
legal assurance
```

### 2. The Turnkey Path Still Fails Before `uv` Exists

The Path C command initially failed because `uv` was not installed, then
succeeded after:

```bash
python3 -m pip install --user uv
```

That is not a code failure, but it is a turnkey failure.

Recommended patch:

```text
scripts/bootstrap_uv.sh
scripts/path_c_smoke.sh
docs/runbooks/path_c_turnkey_reproduction.md
README.md quickstart block
```

Recommended first-run shape:

```bash
command -v uv >/dev/null || python3 -m pip install --user uv
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-m8-demo
```

The smoke script should check/install `uv`, run the M8 demo to `/tmp`, assert
the five required packet files exist, and run the targeted M8 test file.

### 3. Absolute Paths Make Receipts Non-Canonical Across Machines

The Path C reproduction found that regenerated content matched after removing
volatile IDs and timestamps, but absolute local paths caused drift in
`artifact_manifest.json`.

That is acceptable for local traceability. It is weak for cross-machine
evidence comparison.

Recommended canonical fields:

```json
{
  "source_fixture_ref": "examples/m8/support-triage-human-review",
  "source_path_relative": "runs/run_002_sensitive_billing_complaint/human_review_event.json",
  "packet_path_relative": "artifacts/run_002_sensitive_billing_complaint/human_review_event.json",
  "source_path_absolute": "/home/kyle-home/profusion/...",
  "canonical": true
}
```

Recommended commands:

```bash
uv run profusion m8 canonicalize <packet-dir>
uv run profusion m8 compare --canonical <packet-a> <packet-b>
```

For P1, the video manifest should point to canonical receipt data, not
host-local path data.

### 4. There Appears To Be No CI Safety Net

Local evidence is strong, but this checkout has no obvious `.github/workflows`
CI file. Local tests passing is not enough once the repo is live.

Recommended GitHub Actions workflow:

```yaml
name: ci

on:
  push:
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          submodules: false
      - name: Install uv
        run: python3 -m pip install --user uv
      - name: Run backend tests
        run: uv run pytest -q
      - name: Offline smoke
        run: uv run profusion smoke --offline
      - name: M8 P0 demo
        run: |
          uv run profusion m8 demo support-triage-human-review --output-dir "$RUNNER_TEMP/profusion-m8"
          test -n "$(find "$RUNNER_TEMP/profusion-m8" -name workflow_receipt.html -print -quit)"
```

Add a P1 job only when P1 exists. Do not make submodules mandatory for P0/P1
unless the workflow actually needs them.

### 5. The State Machine Is Documented, But Parts Of The Code Bypass Or Compress It

The canonical lifecycle includes a visible `awaiting_approval` state:

```text
qa_passed -> awaiting_approval -> approved
```

The DB helper `record_approval_decision()` transitions from current status to
`awaiting_approval`, then to the final status in the same transaction, making
`awaiting_approval` non-observable. The same file exposes
`update_item_status()` as a direct status setter without transition validation.

For a company selling evidence around review boundaries, the review boundary
should be structurally visible, not a transient DB hop.

Recommended patch:

```python
transition_item_status(db_path, item_id, new_status)  # validates transition
_set_item_status_unchecked(...)                       # private/test/migration only
```

Recommended approval flow:

```text
qa_passed -> awaiting_approval
awaiting_approval + approved decision -> approved
awaiting_approval + revision_requested -> scripted
awaiting_approval + rejected -> archived
```

If `awaiting_approval` is not meant to be externally observable, remove it from
the canonical state machine. Do not keep it as theater.

### 6. P2 Is Supposed To Be Read-Only, But The API Already Exposes Mutation Endpoints

P1/P2 docs say P2 cockpit visibility is optional and must stay read-only: no
approval buttons, mutation logic, scheduling, or publishing controls.

The FastAPI layer currently exposes POST routes for QA retry, render retry, and
publish retry. That is fine for the internal operator cockpit, but risky if
reused for P2 receipt visibility.

Recommended patch:

```python
PROFUSION_API_MODE=read_only
```

When read-only mode is active, do not register POST routes, or return `403`
with a clear message. For P1/P2 demos, default to read-only. Make mutation
opt-in.

The API static path also points to `dashboard/dist`, while repo truth says M7
is in `apps/operator-cockpit/` and the public website in `dashboard/` is out of
scope. The operator API should either serve `apps/operator-cockpit/dist` or
serve no static bundle until P2 is intentionally wired.

### 7. The Repo Is Carrying Too Many Product Eras At Once

The live repo contains the active M8 receipt harness, M7/M7.5 receipt surfaces,
an operator cockpit, a public dashboard, MoneyPrinterTurbo and MoneyPrinterV2
submodules, content/publish/schedule flows, measurement flows, and GTM docs.

Individually, most of this is understandable. Together, it makes the repo
harder to assess as a clean P1 artifact.

P1 does not need MoneyPrinterTurbo. P1 does not need MoneyPrinterV2. P1 does
not need public website work. P1 does not need live publishing, scheduling, or
content generation. P1 needs a receipt-derived video generated under claim
control.

Recommended doc:

```text
docs/ACTIVE_SURFACES.md
```

Recommended map:

```text
Active for P1:
- src/orchestrator/m8_gtm/
- examples/m8/support-triage-human-review/
- docs/runbooks/m8_gtm_n8n_receipt_harness.md
- docs/milestones/M8_*.md

Frozen / do not touch for P1:
- dashboard/
- vendor/
- publication/scheduling flows
- content-generation pipeline

Allowed only if P2 explicitly starts:
- apps/operator-cockpit/
- src/orchestrator/api.py read-only receipt routes
```

### 8. M7.5 Receipt Generation Is Weaker Than The M8 P0 Harness

The M7.5 receipt generator appears to create packet directories directly and
write several files without the same atomic `.partial` discipline or
artifact-hashing posture as the M8 P0 harness.

This is not a P1 blocker because P1 should use the M8 P0 packet. It is a future
consistency issue. If Profusion's product is workflow receipts, receipt modes
should eventually share packet-writing, manifest hashing, and limitation
language primitives.

Recommended follow-up after P1:

```text
src/orchestrator/receipts/packet_writer.py
src/orchestrator/receipts/artifact_manifest.py
```

Then use those for M7.5 and M8.

### 9. Environment Checks Are Too Broad For The P0/P1 Path

`check-env` checks `ffmpeg`, NVENC, Anthropic API key, and Firecrawl. P0 does
not need Anthropic, Firecrawl, Turbo, V2, or publishing credentials.

A stranger running `profusion check-env` before Path C could see failures that
are irrelevant to the receipt harness.

Recommended profiles:

```bash
uv run profusion check-env --profile p0
uv run profusion check-env --profile p1
uv run profusion check-env --profile full
```

P0 should report:

```text
No external credentials required.
No live network integrations required.
Fixture path exists.
M8 demo command available.
```

P1 should check Node, HyperFrames, FFmpeg, and Docker availability, with Docker
listed as recommended for final reproducible render but not required for local
preview.

### 10. `.env.example` Uses A Fake-Looking Anthropic Key Placeholder

`.env.example` currently contains:

```env
ANTHROPIC_API_KEY=sk-ant-...
```

It is probably harmless, but scanners and humans both dislike realistic-looking
secret prefixes. Since P0/P1 do not need Anthropic, make it blank:

```env
ANTHROPIC_API_KEY=
```

Then document which commands actually require it.

## Acceptance Status Against P0/P1

P0 receipt harness: PASS, based on repo closeout and Path C evidence. The
closeout says P0 generated the required packet, included fixture evidence mode,
non-empty supported and unsupported claims, non-empty limitations, and the
sensitive case human review event.

Path C turnkey reproduction: PARTIAL PASS. It works after `uv` exists. It
failed before `uv` existed. That needs a bootstrap/runbook patch.

Cross-machine determinism: PARTIAL PASS. Claim content matches after stripping
volatile IDs and timestamps, but absolute local paths drift. That needs
canonical relative-path fields.

P1 HyperFrames demo: NOT STARTED / NOT ACCEPTED. The docs require storyboard,
video manifest, MP4, claim drift control, and render-mode limitations.

P2 cockpit visibility: DEFERRED. If it starts, it must be read-only. The
current API has mutation routes, so P2 needs a read-only guard before demo
exposure.

CI: FAIL / ABSENT from this checkout. Local tests passing is not enough for a
live repo.

## Priority Patch Queue

1. Path C bootstrap and CI. Add a bootstrap script, Path C runbook, README
   quickstart, and GitHub Actions workflow.
2. Canonical manifest fields. Preserve absolute paths for local debugging, but
   add repo-relative canonical fields and a canonical compare tool/test.
3. P1 storyboard and manifest generator. Implement P1 as receipt-derived
   evidence translation, not hand-authored marketing copy.
4. P1 claim-drift tests. Every on-screen claim must source to
   receipt/observation/storyboard data. Banned overclaim phrases should fail
   tests.
5. State machine hardening. Make `awaiting_approval` real or remove it. Stop
   exposing unvalidated status mutation as a normal helper.
6. Read-only API mode and cockpit/static-path cleanup. P2 should not inherit
   mutation routes by accident.
7. Repo surface map. Make it difficult for future agents to confuse active P1
   work with legacy content, publishing, or dashboard surfaces.

## What Not To Do Right Now

Do not build live n8n integration before P1. Live n8n is more impressive
technically, but it introduces credentials, node setup, webhooks, API shape,
and network failures before the receipt contract is fully proven.

Do not touch MoneyPrinterTurbo or MoneyPrinterV2 for P1. The submodules are
documented and licensed, but they are not the shortest path to P1.

Do not build more cockpit UI yet. The video is the next buyer-readable
artifact. The cockpit can follow as read-only evidence visibility.

Do not update public website copy inside this sprint unless the receipt/video
artifacts already exist. Otherwise the website will outrun the product.

## Bottom Line

Profusion is pointed at a real wedge:

```text
AI-assisted workflow
-> captured artifacts
-> human review boundary
-> M8 observation
-> workflow receipt
-> supported and unsupported claims
```

The P0 code and docs are strong. The main threat now is scope intoxication.

The next move is not to make Profusion bigger. The next move is to make P1
undeniable: one receipt-derived storyboard, one HyperFrames manifest, one MP4,
one claim-drift test suite, and one fresh-clone CI path.
