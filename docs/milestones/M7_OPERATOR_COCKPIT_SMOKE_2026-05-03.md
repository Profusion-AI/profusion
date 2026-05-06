# M7 Operator Cockpit Smoke

Date: 2026-05-03

## Scope

This smoke covers the new internal cockpit app at `apps/operator-cockpit/`.
The public Netlify website in `dashboard/` was not modified for this M7 pass.

## Commands Run

```bash
uv run profusion serve --dev
cd apps/operator-cockpit && corepack pnpm dev --host 127.0.0.1
```

Observed local cockpit URL:

```text
http://127.0.0.1:5174/
```

## Browser / HTTP Smoke

```bash
curl -sS -I http://127.0.0.1:5174/
curl -sS http://127.0.0.1:5174/api/queue
curl -sS -I http://127.0.0.1:5174/items/5f062aa8-73ea-41b0-b852-5e822c3d1c03
curl -sS -i http://127.0.0.1:5174/api/nope
curl -sS http://127.0.0.1:5174/api/items/5f062aa8-73ea-41b0-b852-5e822c3d1c03
google-chrome --headless --disable-gpu --no-sandbox --virtual-time-budget=3000 --dump-dom http://127.0.0.1:5174/queue
google-chrome --headless --disable-gpu --no-sandbox --virtual-time-budget=3000 --dump-dom http://127.0.0.1:5174/items/5f062aa8-73ea-41b0-b852-5e822c3d1c03
```

Observed:

- Cockpit root returned `200 OK` and served `Profusion Operator Cockpit`.
- Queue API returned the local item queue and summary through the cockpit Vite proxy.
- Queue browser render showed the current item `Why American schools still optimize for compliance`.
- Item deep link returned `200 OK` with the SPA shell on refresh.
- Item browser render showed lifecycle state, next safe command, jobs, artifacts, approvals, logs, and handoff tabs.
- Invalid API path `/api/nope` returned API JSON `404 Not Found`, not the SPA shell.

## Verification

```bash
uv run pytest
uv run profusion smoke --offline
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm build
```

Observed results:

- `uv run pytest`: 171 passed
- `uv run profusion smoke --offline`: passed
- `dashboard` lint/build: passed
- `operator-cockpit` test/lint/build: passed

## Remaining Boundaries

- Approve, schedule, and publish remain displayed as terminal commands, not broad cockpit buttons.
- The cockpit exposes guarded retry paths only.
- M7.5 receipt generation is not implemented in this pass.
- Work Trust and live-session receipt surfaces remain deferred.

## Netlify Preview

After local M7 closeout, a remote Netlify draft deploy was created for review:

```text
https://69f761d38e28190b47d6ce1d--profusionai.netlify.app
```

Deploy logs:

```text
https://app.netlify.com/projects/profusionai/deploys/69f761d38e28190b47d6ce1d
```

This is not the production `profusion.ai` deploy. It is a static cockpit
preview with a generated read-only `/api/*` snapshot exported from the local
Profusion read models.

Observed:

- draft cockpit root returned `200 OK`
- `/api/queue` returned the static queue snapshot
- `/api/items/5f062aa8-73ea-41b0-b852-5e822c3d1c03` returned the static item detail snapshot
- Chrome headless rendered the queue and showed `Why American schools still optimize for compliance`
- production `https://profusion.ai` still served the public Profusion AI website

## Visual Port Update

Kyle selected `Port the artifact into the existing cockpit app` after reviewing
the design direction from `docs/M7 Operator Cockpit.html`.

Implemented:

- Ported the artifact's dense internal cockpit shape into `apps/operator-cockpit`.
- Preserved Vite routes, API hooks, Netlify static snapshot rewrites, and the public `dashboard/` site boundary.
- Added the narrow icon rail, top status bar, metric strip, filter/search workbench, dense operator table, item detail panels, approvals/evidence/system views, and read-only command presentation.
- Added `src/domain/cockpitViewModel.ts` with tests so queue metrics and rows derive from existing read-model payloads rather than hardcoded prototype rows.
- Kept retry/approve/schedule/publish as terminal-copy command surfaces, not broad cockpit action buttons.

Fresh verification:

```bash
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm build:netlify
```

Observed:

- `operator-cockpit` tests: 3 files passed, 8 tests passed
- `operator-cockpit` lint: passed
- `operator-cockpit` build:netlify: exported 1 static item snapshot and built successfully
- Local Chrome headless screenshots rendered `/queue` and `/items/5f062aa8-73ea-41b0-b852-5e822c3d1c03`
- Deployed Chrome headless screenshots rendered desktop and mobile `/queue`

New Netlify draft:

```text
https://69f76a252d5c305184a15a79--profusionai.netlify.app
```

Deploy logs:

```text
https://app.netlify.com/projects/profusionai/deploys/69f76a252d5c305184a15a79
```

Remote verification:

- `/queue`: `200 OK`
- `/api/queue`: `200 OK`, static queue snapshot returned
- `/api/items/5f062aa8-73ea-41b0-b852-5e822c3d1c03`: `200 OK`, static item detail snapshot returned
- `https://profusion.ai`: `200 OK`, still serving the public Profusion AI website

## Receipt-Aware Closeout Update

M7.5 added one explicit demo receipt item to the static cockpit preview and
reverified the M7 route boundary.

Current receipt-aware draft:

```text
https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app/queue
```

Deploy logs:

```text
https://app.netlify.com/projects/profusionai/deploys/69f770eec1439a4cd6b2a8c9
```

Additional verification:

```bash
uv run pytest
uv run profusion smoke --offline
cd dashboard && corepack pnpm lint
cd dashboard && corepack pnpm build
cd apps/operator-cockpit && corepack pnpm test
cd apps/operator-cockpit && corepack pnpm lint
cd apps/operator-cockpit && corepack pnpm smoke:static
cd apps/operator-cockpit && corepack pnpm build:netlify
cd apps/operator-cockpit && COCKPIT_BASE_URL=https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app corepack pnpm smoke:static
```

Observed:

- `uv run pytest`: 179 passed
- offline smoke: passed
- public dashboard lint/build: passed
- operator cockpit tests: 8 passed
- operator cockpit lint/build: passed
- static cockpit smoke: passed locally and against the Netlify draft
- `/api/items/m75-demo-content-video-receipt/receipts`: `200 OK`,
  `application/json`, `receipt_count=1`
- `https://profusion.ai`: `200 OK`, still serving the public website
