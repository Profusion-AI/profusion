# Failure Recovery

## Start Here

```bash
uv run profusion handoff --failed-only
uv run profusion inspect --item-id <id>
uv run profusion logs --item-id <id>
```

Avoid direct SQLite edits for normal recovery. M6 retry commands preserve failed
history and expose the next safe command.

## Publish Job Failed

Split-era warning: `render`, `publish`, and `publish-due` are legacy/demo media
paths retained only for sanitized demo compatibility. MoneyPrinterTurbo/V2 live
tooling moved to `/home/kyle/attention-media-lab`; these commands are not part
of the current B2B product promise.

```bash
uv run profusion jobs --item-id <id>
uv run profusion retry --job-id <publish-job-id>
uv run profusion publish-due
```

Scheduled publish failures are requeued from `failed` to `scheduled` when the
parent item is still `scheduled`. Completed publish jobs are immutable.

Immediate publish retries create a linked publish job attempt. The old failed job
is preserved through `retry_of_job_id` / `attempt_group_id`.

## Render Job Failed

```bash
uv run profusion renders --item-id <id>
uv run profusion retry --render-job-id <render-job-id>
uv run profusion render --item-id <id> --wait
```

Render retries submit a new linked Turbo task and preserve the failed render job.
Completed render jobs are immutable.

## QA Failed

```bash
uv run profusion retry --item-id <id> --stage qa
uv run profusion qa --item-id <id>
```

QA retry requires a valid local render package. The item is explicitly returned
from `qa_failed` to `rendered` before QA is re-run.
