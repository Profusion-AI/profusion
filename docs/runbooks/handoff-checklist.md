# Handoff Checklist

Use this before a context reset, agent handoff, or operator shift.

```bash
uv run profusion handoff
uv run profusion handoff --failed-only
uv run profusion status --json
uv run profusion logs --limit 10
```

For a specific item:

```bash
uv run profusion inspect --item-id <id>
uv run profusion jobs --item-id <id>
uv run profusion renders --item-id <id>
uv run profusion approvals --item-id <id>
uv run profusion logs --item-id <id>
```

Include the handoff output, current git branch/SHA/dirty state, failed jobs, and
the exact next safe command from `inspect`.
