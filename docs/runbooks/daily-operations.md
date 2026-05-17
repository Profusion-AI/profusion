# Daily Operations

## Queue Review

```bash
uv run profusion status
uv run profusion status --json
uv run profusion handoff --status scheduled
uv run profusion handoff --failed-only
```

Use `inspect` before taking action on an item:

```bash
uv run profusion inspect --item-id <id>
uv run profusion inspect --item-id <id> --json
```

`inspect` is the canonical situational-awareness command. It reports current state,
latest artifacts and jobs, blockage, retryability, and the next safe command.

## Normal Pipeline

Split-era warning: `render`, `publish`, and `publish-due` are legacy/demo media
paths retained only for sanitized demo compatibility. MoneyPrinterTurbo/V2 live
tooling moved to `/home/kyle/attention-media-lab`; these commands are not part
of the current B2B product promise.

```bash
uv run profusion ingest --topic "..."
uv run profusion plan --item-id <id>
uv run profusion script --item-id <id>
uv run profusion render --item-id <id> --wait
uv run profusion qa --item-id <id>
uv run profusion approve --item-id <id>
uv run profusion schedule --item-id <id> --at "2026-04-21T09:00:00-05:00" --target youtube_shorts:<account-id>
uv run profusion publish-due
```

Schedule is idempotent by default for identical item/platform/account/time targets.
Use `--force` only when an intentional duplicate target is required.
