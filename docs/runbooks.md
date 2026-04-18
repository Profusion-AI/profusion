# Runbooks

## Local Setup (M0)

```bash
# 1. Clone with submodules
git clone --recurse-submodules <repo-url> ~/profusion
cd ~/profusion

# 2. Ensure uv is installed
curl -Ls https://astral.sh/uv/install.sh | sh   # if needed

# 3. Install Python 3.11 + project deps
uv python install 3.11
uv sync

# 4. Configure secrets
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Verify environment
uv run profusion check-env

# 6. Check empty queue
uv run profusion status
```

## Editorial Workflow (M1)

```bash
# Ingest a single topic
uv run profusion ingest --topic "Why American schools optimize for compliance" \
    --pillar education_reform --audience educators --priority 5

# Ingest from CSV (columns: topic,pillar,audience,priority,source)
uv run profusion ingest --file data/topics/example.csv

# Inspect the queue (supports --status filter)
uv run profusion status
uv run profusion status --status idea
uv run profusion status --status planned

# Generate a brief (idea → planned). Requires ANTHROPIC_API_KEY.
uv run profusion plan --item-id <id-or-prefix>

# Generate script variants (planned → scripted).
uv run profusion script --item-id <id-or-prefix>
uv run profusion script --item-id <id-or-prefix> --duration 45
```

`<id-or-prefix>` can be the full UUID or any unique prefix shown in `status`.

Claude output is parsed as strict JSON and validated with Pydantic before it
lands in the DB. If Claude returns malformed JSON, an invalid risk category,
or drops a requested variant, the transition is aborted and the item stays
in its prior state.

Brief metadata (`risk_flags`, `claims_to_verify`, `source_refs`) is stored on
`content_briefs` as JSON. Raw source material attaches to a content item via
the `source_documents` table; populate it manually until Firecrawl ingest is
wired up.

## Secret Configuration

Required secrets in `.env`:
- `ANTHROPIC_API_KEY` — get from console.anthropic.com
- `FIRECRAWL_URL` — default `http://localhost:3002` if running locally

Never commit `.env`. It is in `.gitignore`.

## Render Troubleshooting (M2, when implemented)

- If NVENC unavailable: `profusion check-env` will report it. FFmpeg falls back to software x264.
- MoneyPrinterTurbo requires its own Python 3.11/3.12 venv (separate from orchestrator).
- Render logs stored in `data/renders/<job_id>/render.log`.

## Publishing Troubleshooting (M4, when implemented)

- YouTube upload requires a browser profile with valid Google session.
- MoneyPrinterV2 requires its own Python 3.12 venv.
- All publish jobs default to `private` visibility until operator approves.
- Retry a failed publish: `profusion retry --job-id <id>`

## Rollback / Retry

- Content items never lose state history (approval_records table).
- Re-render: set item status back to `scripted`, run `profusion render`.
- Re-publish: set publish_job status to `pending`, run `profusion publish`.
- To archive and abandon: `profusion approve --reject --item-id <id>`

## Agent Handoff Notes

Before handing off to a new agent:
1. Run `profusion status` and paste the output as context.
2. Reference `DECISIONS.md` for architecture rationale.
3. Reference `STATUS.md` for current milestone and blockers.
4. Check `data/logs/` for any recent error logs.
