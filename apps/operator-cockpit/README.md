# Profusion Operator Cockpit

Internal M7 cockpit for inspecting and recovering Profusion local workflow state.

Run the API:

```bash
uv run profusion serve
```

Run the cockpit:

```bash
cd apps/operator-cockpit
corepack pnpm dev
```

The cockpit consumes the FastAPI/read-model contracts. It does not query SQLite
directly, does not replace the public `dashboard/` website, and only exposes
guarded retry mutations. Approve, schedule, and publish remain terminal commands.

For a remote Netlify preview, export a read-only snapshot of the local API:

```bash
corepack pnpm snapshot-api
corepack pnpm build
```

That snapshot serves queue, item detail, job, render, approval, and log payloads
as static `/api/*` files. It is for remote review only; it does not run the
local FastAPI process or perform retry mutations.
