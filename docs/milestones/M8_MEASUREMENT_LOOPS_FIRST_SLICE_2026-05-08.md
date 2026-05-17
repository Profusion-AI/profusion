# M8 Measurement Loops First Slice

Date: 2026-05-08

## 2026-05-17 Split Update

After the Profusion / Attention Media Lab split, this M8 slice remains in Profusion only as generic workflow outcome observations. Substack publishing, education-channel analytics, source packs, voice guides, and owned-media measurement now belong to /home/kyle/attention-media-lab.

## Verdict

M8 has started as the canonical workflow outcome observation loop, not as a Work Trust,
AI observability, customer portal, or public website milestone.

This first slice keeps outcome observation manual and file-first. It closes the
decorative `published -> measured` state by letting an operator record a
bounded observation after a workflow item has been published or used in a
controlled demo.

Manual workflow outcome observation means a human operator records what happened after a workflow
item was published, reviewed, or used in a controlled demo. The manual part is
the source of truth for the observation, not direct database editing or a
separate analytics system. Profusion owns the command, storage, read API, and
cockpit display.

## What Shipped

- File-first workflow outcome observations in `src/orchestrator/measurements.py`.
- Observation files under `data/measurements/<item_id>/`.
- `uv run profusion measure record --item-id <id> --platform <slug> --observation-type <slug> --recorded-by <operator> --json`.
- `uv run profusion measure list --item-id <id> --json`.
- `uv run profusion measure summary --json`.
- Automatic transition from `published` to `measured` after the first valid
  observation.
- Additional observations remain allowed for items already in `measured`.
- FastAPI read routes:
  - `GET /api/items/{item_id}/measurements`
  - `GET /api/measurements/summary`
- Operator cockpit `/measurements` page and item-detail outcome observation facts.
- Static cockpit snapshot export for the new measurement read routes.
- Manual comparison dimensions for scenario variants, workflow types, and
  trust domains.
- Aggregate comparison rows in the summary read model and cockpit.

## Boundary

M8 first slice does not add:

- platform or content-channel API metric imports
- automated optimization
- model feedback loops
- ranking or scoring of people
- Work Trust scenario execution
- AI observability claims
- customer portal functionality
- public website changes

## Data Shape

One observation records:

```yaml
content_item_id: <item_id>
platform: internal_demo | workflow_review | other_slug
observation_type: reviewer_feedback | workflow_outcome | other_slug
metrics:
  views: null | integer
  completion_rate: null | 0.0-1.0
  comments: null | integer
dimensions:
  scenario_variant: null | string
  workflow_type: null | string
  trust_domain: null | string
qualitative_signal: null | string
recorded_by: operator name
recorded_at: ISO-8601 UTC timestamp
```

This is an observation seed, not an automated growth loop.

Compatibility note: existing JSON may still store these values under
`dimensions.hook_variant`, `dimensions.content_format`, and
`dimensions.editorial_pillar`. Operators should use the generic CLI labels
`scenario_variant`, `workflow_type`, and `trust_domain`.

## Example Operator Record

Check the live command contract before running a scenario:

```bash
uv run profusion measure record --help
```

Then record the observed outcome:

```bash
uv run profusion measure record \
  --item-id <item_id> \
  --platform internal_demo \
  --observation-type reviewer_feedback \
  --recorded-by Kyle \
  --scenario-variant receipt_boundary_open \
  --workflow-type demo_packet \
  --trust-domain workflow_trust \
  --qualitative-signal "Reviewer understood the evidence boundary but wanted a clearer approval handoff." \
  --json
```

## Follow-On Slice

The next implemented increment keeps the same boundary but makes the manual
records useful for comparison. Operators can tag observations with
`scenario_variant`, `workflow_type`, and `trust_domain`, then inspect grouped
summary rows across those dimensions in CLI/API JSON and the cockpit. The
legacy storage keys remain a compatibility detail, not the operator-facing
contract.

M8 should not be closed merely because the software exists. It should be closed
only after the manual loop has produced useful operator evidence.

Minimum closeout criteria:

- at least three manual workflow outcome observations recorded
- at least two comparison dimensions exercised
- `measure list` and `measure summary` reviewed against real/demo observations
- `/measurements` cockpit page visually QA'd with non-empty data
- one operator runbook or closeout note documents the end-to-end loop
- the full verification baseline rerun after the loop is exercised

## Verification

Verification run:

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

Full verification should be rerun before treating M8 as closed.
