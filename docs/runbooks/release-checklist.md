# Release Checklist

Run these before declaring a milestone handoff ready:

```bash
uv run pytest
uv run profusion check-env
uv run profusion status
uv run profusion status --json
uv run profusion smoke --offline
```

For M6, also spot-check:

```bash
uv run profusion handoff --failed-only
uv run profusion inspect --item-id <id>
```

The offline smoke test must not require Anthropic, Turbo, or PostBridge access.
