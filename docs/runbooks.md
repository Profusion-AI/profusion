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
