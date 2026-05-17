# Profusion Roadmap

Date: 2026-05-08

## Current Definition

Profusion AI is a governed AI-mediated workflow evidence system. Its near-term B2B lane is the Profusion Evidence Receipt Pilot: one workflow, one evidence boundary, captured artifacts, human review gates, stated limitations, and a reviewer-readable receipt.

The education/content engine has moved to `/home/kyle/attention-media-lab`. Profusion may retain one sanitized content/media demo as a receipt example, but it is not the owner of Kyle's education media channel.

## Completed Foundation: M0-M6

M0-M6 established the local operating substrate:

- topic and source intake
- structured brief generation
- script variant generation
- local render job tracking
- rendered artifact manifests
- QA checks
- human approval gates
- approval-gated publishing
- scheduling and cross-post coordination
- retry lineage
- status, inspect, jobs, renders, approvals, logs, and handoff surfaces
- offline smoke verification

Business meaning: Profusion has a real local workflow substrate. It is not yet a
customer-facing SaaS product.

## M7: Internal Operator Cockpit

Source of truth: `docs/milestones/M7_OPERATOR_COCKPIT_PRD_TTD.md`

Status: locked and shipped on 2026-05-06.

Final lock record:
`docs/milestones/M7_OPERATOR_COCKPIT_FINAL_CLOSEOUT_2026-05-06.md`

M7 makes Profusion operable.

M7 is the internal operator cockpit for Kyle, Codex, Claude Code, and future
operators. It is not the public website, not a customer portal, and not the Work
Trust product.

Implementation boundary:

- keep the public `dashboard/` Netlify website untouched
- create `apps/operator-cockpit/` as the internal cockpit Vite app
- run it against `uv run profusion serve`
- consume existing FastAPI/read-model contracts
- expose only guarded safe retry mutations
- show approve, schedule, and publish as next safe commands, not buttons

M7 closeout is complete. It has a browser smoke record against the local API
and cockpit, plus a fresh 2026-05-06 lock verification covering the backend
test suite, offline smoke, cockpit tests, cockpit lint, static Netlify build,
and static cockpit smoke.

## M7.5 / PP1: Reviewer-Readable Evidence

Source of truth: `docs/milestones/M7_5_REVIEWER_EVIDENCE_PRD_TTD.md`

M7.5 makes Profusion explainable.

The first B2B-facing surface is a reviewer-readable evidence package, not a
portal. The first receipt type is `content_video_receipt`, generated from the
existing content item, render, QA, approval, artifact, log, and handoff flow.

Initial architecture:

- typed Python models and templates first
- file-based generated artifacts under `data/evidence/` and `data/receipts/`
- no SQLite migrations until the receipt shape survives real demo or pilot use
- receipt approval separate from content approval

Receipt domain language:

```text
trust_domain: media_trust
receipt_type: content_video_receipt
```

Reserved for later:

```text
receipt_type: live_session_receipt
```

## M7.6 / PP1-W: Work Trust Alpha

Work Trust makes Profusion expandable.

This is deferred until the M7.5 receipt path can generate a credible packet from
the existing content workflow.

Initial internal archetype:

```text
agentic_qa_evaluation_analyst
```

Commercial wedge:

```text
privileged remote AI-mediated worker or contractor access-risk evaluation
```

The first scenario can be "Audit a failed AI support workflow," but it must be
framed around observed behavior, verification, escalation, tool-use judgment,
documentation quality, and human accountability.

Do not include ranking, hire/no-hire, role-fit recommendation, automated
selection, or automated rejection language.

## M8: Workflow Outcome Observations

Status: first slice started on 2026-05-08.

After the 2026-05-17 split, M8 remains in Profusion only as generic workflow
outcome observations. It is not content-channel analytics, education-channel
measurement, a Work Trust build, AI observability build, customer portal, or
public website change.

Implemented first slice:

- file-first manual measurement observations under `data/measurements/`
- `uv run profusion measure record --item-id <id> --platform <slug> --observation-type <slug> --recorded-by <operator> --json`
- `uv run profusion measure list --item-id <id> --json`
- `uv run profusion measure summary --json`
- `GET /api/items/{item_id}/measurements`
- `GET /api/measurements/summary`
- operator cockpit `/measurements` visibility and static snapshot export
- optional manual comparison dimensions:
  `hook_variant`, `content_format`, and `editorial_pillar`
- aggregate comparison rows by hook variant, content format, and editorial
  pillar in the summary read model and cockpit

Current M8 constraints:

- manual imports only
- no platform automation
- no optimization algorithms
- no model feedback loop
- no buyer-facing measurement dashboard
- no public website changes

Later M8 hardening can add stronger operator guidance and controlled imports
after manual comparison records prove useful.

### Historical/Sanitized Demo: Substack Publishing + Evidence Loop Spike

Status: safe first slice implemented on 2026-05-08.

This earlier spike is historical context or a sanitized receipt-demo source
after the split. Real Substack and education/content operations now belong to
`/home/kyle/attention-media-lab`.

```text
approved Profusion item -> Substack-ready package -> human publication ->
Substack URL record -> RSS readback -> receipt packet -> manual measurement
```

Implemented first slice:

- `src/orchestrator/adapters/substack.py`
- `src/orchestrator/substack_publish.py`
- `uv run profusion substack package --item-id <id> --json`
- `uv run profusion substack import-article --draft-path <path> --title <title> --approved-by <operator> --confirm-content-approval --json`
  imports a human-approved local long-form draft as an approved package-ready
  item without SQLite hand-editing
- `uv run profusion substack draft --item-id <id> --mode manual --json`
  reuses an existing manual package when present
- `uv run profusion substack publish --item-id <id> --url <published_url> --confirm-publish --json`
  requires an existing manual package
- `uv run profusion substack verify --item-id <id> --url <published_url> --method rss --json`
  requires a matching recorded publication URL and fails if the URL is absent
  from RSS
- publication artifacts under `data/substack/<item_id>/`
- receipt evidence now carries publish job platform, URL, external id, and
  publish timestamp when present

M8.1 voice run:

- Existing Substack article extracted locally as a source voice sample.
- v0 Profusion Substack voice guide written under `data/style/`.
- Follow-on draft written under `data/drafts/` for human review.
- `substack import-article` creates an approved package-ready item only after
  `--confirm-content-approval`; the draft has not yet been imported or
  published.

Boundary:

- no public website changes
- no hidden Substack write endpoints
- no authenticated Substack dashboard scraping
- no stored browser cookies or sessions
- no automated email/app inbox send
- no Stackhooks or analytics import in the first slice
- no MCP wrapper until the project CLI is the durable source of truth

## Deferred Surfaces

The following are out of scope for M7 and M7.5:

- customer portal
- organization management
- billing
- external reviewer queues
- employer dashboards
- candidate auth
- automated hiring decisions
- candidate ranking
- detector-grade synthetic media claims
- live webcam receipt implementation
- public website rewrite
- Work Trust marketing launch

## Current Verification Baseline

Earlier M8 measurement/cockpit verification baseline on 2026-05-08:

```bash
uv run pytest
uv run profusion smoke --offline
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm build:netlify
cd apps/operator-cockpit && corepack pnpm smoke:static
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
git diff --check
```

Observed results:

- `uv run pytest`: 189 passed
- `uv run profusion smoke --offline`: passed
- `cd apps/operator-cockpit && corepack pnpm test`: 4 files passed, 11 tests passed
- `cd apps/operator-cockpit && corepack pnpm lint`: passed
- `cd apps/operator-cockpit && corepack pnpm build:netlify`: exported 2 static item snapshots and built successfully
- `cd apps/operator-cockpit && corepack pnpm smoke:static`: passed for 2 items
- `cd dashboard && corepack pnpm lint`: passed
- `cd dashboard && corepack pnpm build`: passed
- `git diff --check`: passed

Substack spike QC verification:

- `uv run pytest tests/test_substack_publish.py -q`: 17 passed
- `uv run pytest tests/test_substack_publish.py tests/test_receipts.py tests/test_measurements.py -q`: 31 passed
- `uv run pytest -q`: 206 passed
- `uv run profusion smoke --offline`: passed
- `git diff --check`: passed

The full verification baseline should be rerun after the first real Substack
operator scenario before M8 is closed.

Latest M7 lock verification on 2026-05-06:

```bash
uv run pytest
uv run profusion smoke --offline
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm build:netlify
cd apps/operator-cockpit && corepack pnpm smoke:static
```

Observed results:

- `uv run pytest`: 182 passed
- `uv run profusion smoke --offline`: passed
- `cd apps/operator-cockpit && corepack pnpm test`: 3 files passed, 9 tests passed
- `cd apps/operator-cockpit && corepack pnpm lint`: passed
- `cd apps/operator-cockpit && corepack pnpm build:netlify`: exported 2 static item snapshots and built successfully
- `cd apps/operator-cockpit && corepack pnpm smoke:static`: passed for 2 items

Historical pre-implementation verification on 2026-05-03:

Verification run on 2026-05-03:

```bash
uv run pytest
uv run profusion smoke --offline
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
```

Observed results:

- `uv run pytest`: 171 passed
- `uv run profusion smoke --offline`: passed
- `cd dashboard && pnpm lint`: blocked by local asdf `pnpm` shim
- `cd dashboard && pnpm build`: blocked by local asdf `pnpm` shim
- `cd dashboard && corepack pnpm lint`: passed
- `cd dashboard && corepack pnpm build`: passed

Use `corepack pnpm` for dashboard checks in this local environment unless the
asdf `pnpm` shim is repaired.
