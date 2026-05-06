# M7 Operator Cockpit Closeout

Date: 2026-05-03

## Status

M7 is green as an internal operator cockpit baseline.

The cockpit lives at:

```text
apps/operator-cockpit/
```

The public website remains at:

```text
dashboard/
```

Production `https://profusion.ai` was not promoted or changed during this
closeout pass.

## Current Draft

Receipt-aware Netlify draft:

```text
https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app/queue
```

Deploy logs:

```text
https://app.netlify.com/projects/profusionai/deploys/69f770eec1439a4cd6b2a8c9
```

## Static Preview Boundary

The Netlify draft is a static Vite deploy with generated read-only JSON files
under `apps/operator-cockpit/public/api/`.

It does not run the local FastAPI/SQLite backend. Queue, detail, evidence,
jobs, approvals, logs, handoff, and command visibility can be reviewed in the
browser. Mutations such as approve, schedule, publish, retry, and receipt draft
generation remain terminal/backend operations.

## Local Commands

```bash
uv run profusion serve --dev
cd apps/operator-cockpit && corepack pnpm dev --host 127.0.0.1
```

Static preview build:

```bash
uv run python scripts/seed-m7-5-receipt-demo.py
cd apps/operator-cockpit && corepack pnpm build:netlify
```

Static snapshot smoke:

```bash
cd apps/operator-cockpit && corepack pnpm smoke:static
COCKPIT_BASE_URL=https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app corepack pnpm smoke:static
```

## Route Checklist

The receipt-aware draft smoke covered:

- `/queue`
- `/failures`
- `/approvals`
- `/evidence`
- `/logs`
- `/system`
- `/api/queue`
- `/api/items/m75-demo-content-video-receipt/receipts`

## Screenshot Checklist

Use this checklist for browser review before any production promotion:

- Desktop `/queue`: narrow rail, metrics, filters, queue table, and right-side
  context remain readable.
- Desktop `/evidence`: demo item shows `Receipt Draft` and receipt count `1`.
- Desktop `/items/m75-demo-content-video-receipt`: next safe command and
  evidence/artifact panels remain visible without overlap.
- Mobile `/queue`: rail/top status, table cards, and text wrap without clipping.
- Mobile `/evidence`: receipt path and command presentation remain readable.

## M7 Boundaries

- Cockpit consumes existing FastAPI/read-model contracts.
- Cockpit does not query SQLite directly.
- Broad approve, schedule, publish, archive, and receipt-draft mutations are
  not exposed as ordinary UI buttons.
- Work Trust, customer portals, candidate scoring, and detector-grade claims
  remain deferred.
