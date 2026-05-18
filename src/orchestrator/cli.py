"""Profusion CLI — operator entry point.

Usage: profusion <command> [options]
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="profusion",
    help="Profusion B2B workflow trust and evidence receipt operator system.",
    no_args_is_help=True,
)
receipt_app = typer.Typer(help="Generate and inspect reviewer evidence receipts.")
app.add_typer(receipt_app, name="receipt")
measure_app = typer.Typer(help="Record and inspect manual M8 workflow outcome observations.")
app.add_typer(measure_app, name="measure")
m8_app = typer.Typer(help="Run M8-GTM fixture-backed workflow receipt demos.")
app.add_typer(m8_app, name="m8")
console = Console()


STATUS_COLORS: dict[str, str] = {
    "idea": "white",
    "planned": "blue",
    "scripted": "cyan",
    "rendered": "yellow",
    "qa_failed": "red",
    "qa_passed": "green",
    "awaiting_approval": "magenta",
    "approved": "bright_green",
    "scheduled": "bright_cyan",
    "published": "bright_blue",
    "measured": "bright_magenta",
    "archived": "dim",
}


def _db_path() -> Path:
    from orchestrator import config
    return config.DB_PATH


def _ensure_db() -> None:
    from orchestrator.db import init_db
    init_db(_db_path())


def _resolve_item(item_id: str) -> dict:
    """Resolve an id or id-prefix to a content_item or exit with a clear error."""
    from orchestrator.db import find_item_by_prefix, get_item

    item = get_item(_db_path(), item_id)
    if item is not None:
        return item
    try:
        item = find_item_by_prefix(_db_path(), item_id)
    except ValueError as e:
        console.print(f"[red]{e}. Provide a longer prefix.[/red]")
        raise typer.Exit(code=1)
    if item is None:
        console.print(f"[red]No content item matches id or prefix {item_id!r}.[/red]")
        raise typer.Exit(code=1)
    return item


class PublishPackageError(ValueError):
    """Raised when a content item is not ready to publish or schedule."""


def _normalize_iso_datetime(value: str) -> str:
    """Parse an operator ISO datetime and store it as UTC with stable sorting."""
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(
            "Use an ISO datetime like '2026-04-21T09:00:00-05:00'"
        ) from exc
    if parsed.tzinfo is None:
        raise ValueError("Scheduled datetimes must include a timezone offset")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _parse_schedule_targets(targets: list[str] | None) -> list[tuple[str, int]]:
    if not targets:
        raise ValueError("Provide at least one --target platform:account_id")
    parsed: list[tuple[str, int]] = []
    for target in targets:
        if ":" not in target:
            raise ValueError(f"Invalid target {target!r}; expected platform:account_id")
        platform, account_id_raw = target.split(":", 1)
        platform = platform.strip()
        if not platform:
            raise ValueError(f"Invalid target {target!r}; platform is empty")
        try:
            account_id = int(account_id_raw)
        except ValueError as exc:
            raise ValueError(
                f"Invalid target {target!r}; account_id must be an integer"
            ) from exc
        parsed.append((platform, account_id))
    return parsed


def _load_platform_metadata(metadata: str | None) -> dict:
    if not metadata:
        return {}
    try:
        loaded = json.loads(metadata)
    except ValueError as exc:
        raise ValueError("--metadata must be valid JSON") from exc
    if not isinstance(loaded, dict):
        raise ValueError("--metadata must decode to a JSON object")
    return loaded


def _metadata_for_platform(metadata: dict, platform: str) -> dict:
    if not metadata:
        return {}
    platform_specific = metadata.get(platform)
    if isinstance(platform_specific, dict):
        return platform_specific
    return metadata


def _validate_publish_package(item: dict) -> Path:
    """Validate that an item has a coherent approved render package."""
    from orchestrator import config, db

    render_job = db.get_completed_render_job_for_item(config.DB_PATH, item["id"])
    if render_job is None:
        raise PublishPackageError(
            f"No completed render job found for item {item['id']!r}"
        )

    if not render_job.get("output_path"):
        raise PublishPackageError("Render job has no output_path recorded")

    mp4_path = Path(render_job["output_path"])
    if not mp4_path.exists() or mp4_path.stat().st_size == 0:
        raise PublishPackageError(f"Render artifact missing or empty: {mp4_path}")

    manifest_path = mp4_path.parent / "manifest.json"
    if not manifest_path.exists():
        raise PublishPackageError(f"manifest.json not found at {manifest_path}")

    qa_report_path = mp4_path.parent / "qa_report.json"
    if not qa_report_path.exists():
        raise PublishPackageError(f"qa_report.json not found at {qa_report_path}")

    approval_records = db.get_approval_records(config.DB_PATH, item["id"])
    if not any(r["decision"] == "approved" for r in approval_records):
        raise PublishPackageError(
            f"No approved approval record found for item {item['id']!r}"
        )

    return mp4_path


def _emit_json(payload: object) -> None:
    typer.echo(json.dumps(payload, indent=2, default=str))


def _print_key_values(title: str, rows: list[tuple[str, object]]) -> None:
    table = Table(title=title, show_header=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")
    for key, value in rows:
        table.add_row(key, "—" if value is None or value == "" else str(value))
    console.print(table)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@app.command()
def status(
    status_filter: str | None = typer.Option(
        None, "--status", help="Filter by lifecycle status (e.g. idea, planned)."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Emit machine-readable JSON for dashboard/handoff use."
    ),
) -> None:
    """Show the current content queue."""
    _ensure_db()
    from orchestrator.db import get_all_items
    from orchestrator.read_models import status_payload
    from orchestrator.state import ContentStatus

    if status_filter is not None:
        try:
            ContentStatus(status_filter)
        except ValueError:
            valid = ", ".join(s.value for s in ContentStatus)
            console.print(f"[red]Unknown status {status_filter!r}.[/red] Valid: {valid}")
            raise typer.Exit(code=2)

    if json_output:
        _emit_json(status_payload(_db_path(), status=status_filter))
        return

    items = get_all_items(_db_path(), status=status_filter)

    title = "Profusion Content Queue"
    if status_filter:
        title += f" (status={status_filter})"
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Topic", min_width=30)
    table.add_column("Status", style="bold")
    table.add_column("Pillar")
    table.add_column("Priority", justify="right")
    table.add_column("Created", style="dim")

    for item in items:
        s = item["status"]
        color = STATUS_COLORS.get(s, "white")
        table.add_row(
            item["id"][:12],
            item["topic"],
            f"[{color}]{s}[/{color}]",
            item["pillar"] or "—",
            str(item["priority"]),
            (item.get("created_at") or "")[:19],
        )

    console.print(table)
    if not items:
        if status_filter:
            console.print(f"[dim]No items with status={status_filter!r}.[/dim]")
        else:
            console.print(
                "[dim]Queue is empty. Use [bold]profusion ingest[/bold] to add topics.[/dim]"
            )


# ---------------------------------------------------------------------------
# M6 inspection surfaces
# ---------------------------------------------------------------------------

@app.command()
def inspect(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Inspect one content item, its artifacts, jobs, blockage, and next safe command."""
    _ensure_db()
    from orchestrator.read_models import inspect_payload

    item = _resolve_item(item_id)
    payload = inspect_payload(_db_path(), _logs_dir(), item)
    if json_output:
        _emit_json(payload)
        return

    _print_key_values(
        "Profusion Inspect",
        [
            ("Item", payload["item"]["id"]),
            ("Topic", payload["item"]["topic"]),
            ("Status", payload["lifecycle_state"]),
            ("Milestone", payload["milestone"]),
            ("Latest render", (payload["latest_render_job"] or {}).get("id")),
            ("Latest publish", (payload["latest_publish_job"] or {}).get("id")),
            ("Blockage", (payload["blockage"] or {}).get("message")),
            ("Retryable", payload["retry"].get("retryable")),
            ("Next", payload.get("next_safe_command")),
        ],
    )
    artifacts = payload["artifacts"]
    console.print(
        f"[dim]Artifacts:[/dim] mp4={artifacts.get('mp4_path') or '—'} "
        f"manifest={artifacts.get('manifest_path') or '—'} "
        f"qa={artifacts.get('qa_report_path') or '—'}"
    )


@app.command()
def jobs(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Show render and publish jobs for a content item."""
    _ensure_db()
    from orchestrator.read_models import jobs_payload

    item = _resolve_item(item_id)
    payload = jobs_payload(_db_path(), item["id"])
    if json_output:
        _emit_json(payload)
        return

    table = Table(title=f"Jobs for {item['id'][:12]}")
    table.add_column("Kind")
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Target / Variant")
    table.add_column("Retryable")
    for job in payload["render_jobs"]:
        table.add_row(
            "render",
            job["id"][:12],
            job["status"],
            job.get("variant_name") or "—",
            str(job["retry"].get("retryable")),
        )
    for job in payload["publish_jobs"]:
        table.add_row(
            "publish",
            job["id"][:12],
            job["status"],
            f"{job.get('platform')}:{job.get('account_id')}",
            str(job["retry"].get("retryable")),
        )
    console.print(table)


@app.command()
def renders(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Show render history and artifacts for a content item."""
    _ensure_db()
    from orchestrator.read_models import renders_payload

    item = _resolve_item(item_id)
    payload = renders_payload(_db_path(), item["id"])
    if json_output:
        _emit_json(payload)
        return

    table = Table(title=f"Renders for {item['id'][:12]}")
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Variant")
    table.add_column("Output")
    table.add_column("Retry")
    for job in payload["render_jobs"]:
        table.add_row(
            job["id"][:12],
            job["status"],
            job.get("variant_name") or "—",
            job.get("output_path") or "—",
            str(job["retry"].get("retryable")),
        )
    console.print(table)


@app.command()
def approvals(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Show approval history for a content item."""
    _ensure_db()
    from orchestrator.read_models import approvals_payload

    item = _resolve_item(item_id)
    payload = approvals_payload(_db_path(), item["id"])
    if json_output:
        _emit_json(payload)
        return

    table = Table(title=f"Approvals for {item['id'][:12]}")
    table.add_column("ID")
    table.add_column("Decision")
    table.add_column("By")
    table.add_column("Timestamp")
    table.add_column("Notes")
    for record in payload["approval_records"]:
        table.add_row(
            record["id"][:12],
            record["decision"],
            record["approved_by"],
            record["timestamp"],
            record.get("notes") or "—",
        )
    console.print(table)


@app.command()
def logs(
    item_id: str | None = typer.Option(None, "--item-id", help="Content item id (or unique prefix)."),
    job_id: str | None = typer.Option(None, "--job-id", help="Render or publish job id."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
    limit: int = typer.Option(20, "--limit", min=1, max=100),
) -> None:
    """List diagnostic logs for an item or job."""
    from orchestrator.diagnostics import list_logs

    _ensure_db()
    resolved_item_id = None
    if item_id:
        resolved_item_id = _resolve_item(item_id)["id"]
    if resolved_item_id and job_id:
        console.print("[red]Use either --item-id or --job-id, not both.[/red]")
        raise typer.Exit(code=2)
    payload = {
        "item_id": resolved_item_id,
        "job_id": job_id,
        "logs": list_logs(_logs_dir(), item_id=resolved_item_id, job_id=job_id, limit=limit),
    }
    if json_output:
        _emit_json(payload)
        return
    table = Table(title="Profusion Logs")
    table.add_column("Modified")
    table.add_column("Path")
    table.add_column("Bytes", justify="right")
    for row in payload["logs"]:
        table.add_row(row["modified_at"], row["path"], str(row["size_bytes"]))
    console.print(table)


@app.command()
def handoff(
    item_id: str | None = typer.Option(None, "--item-id", help="Content item id (or unique prefix)."),
    status_filter: str | None = typer.Option(None, "--status", help="Filter queue by lifecycle status."),
    failed_only: bool = typer.Option(False, "--failed-only", help="Only include blocked/failed items."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Produce a concise handoff report for a fresh operator or agent context."""
    _ensure_db()
    from orchestrator.read_models import handoff_payload
    from orchestrator.state import ContentStatus

    item = _resolve_item(item_id) if item_id else None
    if status_filter is not None:
        try:
            ContentStatus(status_filter)
        except ValueError:
            valid = ", ".join(s.value for s in ContentStatus)
            console.print(f"[red]Unknown status {status_filter!r}.[/red] Valid: {valid}")
            raise typer.Exit(code=2)

    payload = handoff_payload(
        _db_path(),
        _logs_dir(),
        item=item,
        status=status_filter,
        failed_only=failed_only,
    )
    if json_output:
        _emit_json(payload)
        return
    typer.echo(_format_handoff_markdown(payload))


def _logs_dir() -> Path:
    from orchestrator import config
    return config.LOGS_DIR


def _format_handoff_markdown(payload: dict) -> str:
    git = payload["git"]
    queue = ", ".join(
        f"{row['status']}={row['count']}" for row in payload["queue_summary"]
    ) or "empty"
    lines = [
        "# Profusion Handoff",
        "",
        f"- Milestone: {payload['milestone']}",
        f"- Git: {git.get('branch') or 'unknown'} @ {git.get('sha') or 'unknown'} dirty={git.get('dirty')}",
        f"- Queue: {queue}",
        "",
        "## Items",
    ]
    if not payload["items"]:
        lines.append("- No matching items.")
    for entry in payload["items"]:
        item = entry["item"]
        lines.extend([
            f"- {item['id']} [{item['status']}] {item['topic']}",
            f"  - Next: {entry.get('next_safe_command') or 'manual review'}",
            f"  - Blockage: {(entry.get('blockage') or {}).get('message') or 'none'}",
            f"  - Retry: {entry.get('retry', {}).get('command') or entry.get('retry', {}).get('reason')}",
        ])
    if payload["recent_logs"]:
        lines.extend(["", "## Recent Logs"])
        for row in payload["recent_logs"][:5]:
            lines.append(f"- {row['modified_at']} {row['path']}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# M7.5 receipt surfaces
# ---------------------------------------------------------------------------

@receipt_app.command("draft")
def receipt_draft(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Generate a draft content_video_receipt evidence packet."""
    _ensure_db()
    import orchestrator.config as config
    from orchestrator.receipts.generator import (
        ReceiptEligibilityError,
        generate_content_video_receipt,
    )

    item = _resolve_item(item_id)
    try:
        receipt = generate_content_video_receipt(
            db_path=_db_path(),
            logs_dir=_logs_dir(),
            receipts_dir=config.RECEIPTS_DIR,
            item_id=item["id"],
        )
    except ReceiptEligibilityError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    payload = receipt.to_payload()
    if json_output:
        _emit_json(payload)
        return

    _print_key_values(
        "Profusion Receipt Draft",
        [
            ("Receipt", payload["receipt_id"]),
            ("Type", payload["receipt_type"]),
            ("Status", payload["receipt_status"]),
            ("Item", payload["subject_id"]),
            ("Packet", payload["packet_dir"]),
            ("Receipt Markdown", payload["receipt_md"]),
            ("Evidence JSON", payload["evidence_json"]),
        ],
    )


@receipt_app.command("list")
def receipt_list(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """List generated receipt packets for a content item."""
    _ensure_db()
    import orchestrator.config as config
    from orchestrator.receipts.generator import receipts_payload

    item = _resolve_item(item_id)
    payload = receipts_payload(receipts_dir=config.RECEIPTS_DIR, item_id=item["id"])
    if json_output:
        _emit_json(payload)
        return

    table = Table(title=f"Receipts for {item['id'][:12]}")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Created")
    table.add_column("Packet")
    for receipt in payload["receipts"]:
        table.add_row(
            str(receipt.get("receipt_id", ""))[:18],
            str(receipt.get("receipt_type") or "—"),
            str(receipt.get("receipt_status") or "—"),
            str(receipt.get("created_at") or "—"),
            str(receipt.get("packet_dir") or "—"),
        )
    console.print(table)


@receipt_app.command("transition")
def receipt_transition(
    receipt_id: str = typer.Option(..., "--receipt-id", help="Receipt packet id."),
    to_status: str = typer.Option(
        ...,
        "--to",
        help="Next status: reviewed, approved_for_packet, or delivered.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Move a receipt packet through the reviewer delivery lifecycle."""
    import orchestrator.config as config
    from orchestrator.receipts.generator import (
        ReceiptTransitionError,
        transition_receipt,
    )

    try:
        payload = transition_receipt(
            receipts_dir=config.RECEIPTS_DIR,
            receipt_id=receipt_id,
            to_status=to_status,
        )
    except ReceiptTransitionError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    if json_output:
        _emit_json(payload)
        return

    _print_key_values(
        "Profusion Receipt Transition",
        [
            ("Receipt", payload["receipt_id"]),
            ("Type", payload["receipt_type"]),
            ("Status", payload["receipt_status"]),
            ("Item", payload["subject_id"]),
            ("Packet", payload["packet_dir"]),
            ("Updated", payload.get("receipt_status_updated_at") or "unknown"),
        ],
    )


# ---------------------------------------------------------------------------
# M8 measurement surfaces
# ---------------------------------------------------------------------------

@measure_app.command("record")
def measure_record(
    item_id: str = typer.Option(..., "--item-id", help="Published workflow item id (or unique prefix)."),
    platform: str = typer.Option(..., "--platform", help="Workflow type slug, e.g. internal_demo."),
    observation_type: str = typer.Option(
        ...,
        "--observation-type",
        help="Outcome observation type slug, e.g. reviewer_feedback or workflow_outcome.",
    ),
    recorded_by: str = typer.Option(..., "--recorded-by", help="Operator who recorded this observation."),
    qualitative_signal: str | None = typer.Option(
        None,
        "--qualitative-signal",
        help="Plain-English signal or operator interpretation.",
    ),
    views: int | None = typer.Option(None, "--views", min=0, help="Manual outcome count, when relevant."),
    completion_rate: float | None = typer.Option(
        None,
        "--completion-rate",
        min=0.0,
        max=1.0,
        help="Manual workflow completion rate from 0 to 1, when relevant.",
    ),
    comments: int | None = typer.Option(None, "--comments", min=0, help="Manual feedback/comment count."),
    scenario_variant: str | None = typer.Option(
        None,
        "--scenario-variant",
        help="Scenario variant label.",
    ),
    workflow_type: str | None = typer.Option(
        None,
        "--workflow-type",
        help="Workflow type label.",
    ),
    trust_domain: str | None = typer.Option(
        None,
        "--trust-domain",
        help="Trust domain label.",
    ),
    legacy_hook_variant: str | None = typer.Option(None, "--hook-variant", hidden=True),
    legacy_content_format: str | None = typer.Option(None, "--content-format", hidden=True),
    legacy_editorial_pillar: str | None = typer.Option(None, "--editorial-pillar", hidden=True),
    recorded_at: str | None = typer.Option(
        None,
        "--recorded-at",
        help="Observed-at timestamp with timezone; defaults to now.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Record a manual M8 workflow outcome observation."""
    _ensure_db()
    import orchestrator.config as config
    from orchestrator.measurements import (
        MeasurementEligibilityError,
        MeasurementValidationError,
        record_measurement_observation,
    )

    item = _resolve_item(item_id)
    try:
        payload = record_measurement_observation(
            db_path=_db_path(),
            measurements_dir=config.MEASUREMENTS_DIR,
            item_id=item["id"],
            platform=platform,
            observation_type=observation_type,
            recorded_by=recorded_by,
            qualitative_signal=qualitative_signal,
            views=views,
            completion_rate=completion_rate,
            comments=comments,
            hook_variant=scenario_variant or legacy_hook_variant,
            content_format=workflow_type or legacy_content_format,
            editorial_pillar=trust_domain or legacy_editorial_pillar,
            recorded_at=recorded_at,
        )
    except (MeasurementEligibilityError, MeasurementValidationError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    if json_output:
        _emit_json(payload)
        return

    _print_key_values(
        "Profusion Outcome Observation",
        [
            ("Observation", payload["observation_id"]),
            ("Item", payload["content_item_id"]),
            ("Workflow type", payload["platform"]),
            ("Type", payload["observation_type"]),
            ("Recorded by", payload["recorded_by"]),
            ("Recorded at", payload["recorded_at"]),
            ("Scenario variant", payload["display_dimensions"].get("scenario_variant")),
            ("Workflow type label", payload["display_dimensions"].get("workflow_type")),
            ("Trust domain", payload["display_dimensions"].get("trust_domain")),
            ("Status", f"{payload['status_before']} -> {payload['status_after']}"),
            ("Path", payload["observation_path"]),
        ],
    )


@measure_app.command("list")
def measure_list(
    item_id: str = typer.Option(..., "--item-id", help="Workflow item id (or unique prefix)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """List M8 workflow outcome observations for one item."""
    _ensure_db()
    import orchestrator.config as config
    from orchestrator.measurements import measurements_payload

    item = _resolve_item(item_id)
    payload = measurements_payload(
        measurements_dir=config.MEASUREMENTS_DIR,
        item_id=item["id"],
    )
    if json_output:
        _emit_json(payload)
        return

    table = Table(title=f"Outcome Observations for {item['id'][:12]}")
    table.add_column("ID")
    table.add_column("Workflow type")
    table.add_column("Type")
    table.add_column("Recorded")
    table.add_column("Signal")
    for observation in payload["observations"]:
        table.add_row(
            str(observation.get("observation_id", ""))[:18],
            str(observation.get("platform") or "—"),
            str(observation.get("observation_type") or "—"),
            str(observation.get("recorded_at") or "—"),
            str(observation.get("qualitative_signal") or "—"),
        )
    console.print(table)


@measure_app.command("summary")
def measure_summary(
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Show aggregate M8 workflow outcome observation summary."""
    _ensure_db()
    import orchestrator.config as config
    from orchestrator.measurements import measurement_summary_payload

    payload = measurement_summary_payload(
        db_path=_db_path(),
        measurements_dir=config.MEASUREMENTS_DIR,
    )
    if json_output:
        _emit_json(payload)
        return

    metrics = payload["aggregate_metrics"]
    _print_key_values(
        "Profusion Outcome Observation Summary",
        [
            ("Observations", payload["observation_count"]),
            ("Measured items", payload["measured_item_count"]),
            ("Views", metrics.get("views")),
            ("Comments", metrics.get("comments")),
            ("Average completion", metrics.get("average_completion_rate")),
        ],
    )


# ---------------------------------------------------------------------------
# M8-GTM demo receipt surfaces
# ---------------------------------------------------------------------------

@m8_app.command("demo")
def m8_demo(
    workflow_slug: str = typer.Argument(..., help="M8-GTM workflow slug to run."),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Receipt output root. Defaults to data/receipts/m8-gtm.",
    ),
) -> None:
    """Generate a fixture-backed M8-GTM workflow receipt packet."""

    from orchestrator.m8_gtm.harness import generate_demo_packet
    from orchestrator.m8_gtm.schemas import M8GTMError

    try:
        result = generate_demo_packet(workflow_slug, output_root=output_dir)
    except M8GTMError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    console.print(f"Loaded workflow fixture: {workflow_slug}")
    console.print(
        "Loaded run artifacts: routine_invoice, sensitive_billing_complaint"
    )
    console.print("Validated artifact manifest")
    console.print("Generated M8 observation")
    console.print("Generated workflow receipt JSON")
    console.print("Generated workflow receipt Markdown")
    console.print("Generated workflow receipt HTML")
    typer.echo(f"Receipt: {result['workflow_receipt_html']}")


# ---------------------------------------------------------------------------
# check-env
# ---------------------------------------------------------------------------

@app.command("check-env")
def check_env() -> None:
    """Check environment dependencies (ffmpeg, NVENC, API key)."""
    console.print("[bold]Profusion environment check[/bold]\n")

    try:
        result = subprocess.run(
            ["ffmpeg", "-encoders"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        encoder_output = result.stdout + result.stderr
        if "h264_nvenc" in encoder_output:
            console.print("[green]✓[/green] ffmpeg: present")
            console.print("[green]✓[/green] NVENC (h264_nvenc): available — GPU encoding enabled")
        else:
            console.print("[green]✓[/green] ffmpeg: present")
            console.print("[yellow]~[/yellow] NVENC (h264_nvenc): not available — will use software encoding")
    except FileNotFoundError:
        console.print("[red]✗[/red] ffmpeg: not found in PATH — required for rendering")
    except subprocess.TimeoutExpired:
        console.print("[yellow]~[/yellow] ffmpeg: timed out checking encoders")

    from orchestrator import config
    if config.ANTHROPIC_API_KEY:
        console.print("[green]✓[/green] ANTHROPIC_API_KEY: set")
    else:
        console.print("[red]✗[/red] ANTHROPIC_API_KEY: not set — copy .env.example to .env")

    import httpx
    try:
        r = httpx.get(f"{config.FIRECRAWL_URL}/health", timeout=3)
        if r.status_code < 400:
            console.print(f"[green]✓[/green] Firecrawl: reachable at {config.FIRECRAWL_URL}")
        else:
            console.print(f"[yellow]~[/yellow] Firecrawl: {config.FIRECRAWL_URL} returned {r.status_code}")
    except Exception:
        console.print(
            f"[yellow]~[/yellow] Firecrawl: not reachable at {config.FIRECRAWL_URL} "
            "(start service or ignore for now)"
        )

    try:
        r = httpx.get(
            f"{config.TURBO_URL}/api/v1/tasks",
            params={"page": 1, "page_size": 1},
            timeout=3,
        )
        if r.status_code < 400:
            console.print(f"[green]✓[/green] MoneyPrinterTurbo: reachable at {config.TURBO_URL}")
        else:
            console.print(
                f"[yellow]~[/yellow] MoneyPrinterTurbo: {config.TURBO_URL} "
                f"returned {r.status_code}"
            )
    except Exception:
        console.print(
            f"[yellow]~[/yellow] MoneyPrinterTurbo: not reachable at {config.TURBO_URL} "
            "(start vendor/MoneyPrinterTurbo or ignore for now)"
        )

    console.print()


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------

@app.command()
def ingest(
    topic: str | None = typer.Option(None, "--topic", help="Single topic text to ingest."),
    file: Path | None = typer.Option(
        None,
        "--file",
        exists=True,
        readable=True,
        help="CSV with columns: topic,pillar,audience,priority,source.",
    ),
    pillar: str | None = typer.Option(None, "--pillar"),
    audience: str | None = typer.Option(None, "--audience"),
    priority: int = typer.Option(0, "--priority", min=0),
    source: str | None = typer.Option(None, "--source"),
) -> None:
    """Ingest topics into the content queue as idea-stage items."""
    _ensure_db()
    from orchestrator.db import insert_content_item

    if topic is None and file is None:
        console.print("[red]Provide --topic or --file.[/red]")
        raise typer.Exit(code=2)

    created: list[tuple[str, str]] = []

    if topic:
        item_id = insert_content_item(
            _db_path(),
            topic=topic,
            pillar=pillar,
            audience=audience,
            priority=priority,
            source=source,
        )
        created.append((item_id, topic))

    if file:
        try:
            rows = _read_topic_csv(file)
        except ValueError as e:
            console.print(f"[red]CSV error:[/red] {e}")
            raise typer.Exit(code=2)
        for row in rows:
            item_id = insert_content_item(
                _db_path(),
                topic=row["topic"],
                pillar=row.get("pillar") or pillar,
                audience=row.get("audience") or audience,
                priority=row["_priority"],
                source=row.get("source") or source,
            )
            created.append((item_id, row["topic"]))

    if not created:
        console.print("[yellow]No items ingested. Check your --topic value or CSV content.[/yellow]")
        raise typer.Exit(code=2)

    for item_id, t in created:
        console.print(f"[green]+[/green] {item_id[:12]}  [bold]{t}[/bold]")
    console.print(f"\n[dim]Ingested {len(created)} item(s).[/dim]")


def _read_topic_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "topic" not in reader.fieldnames:
            raise ValueError("CSV must have a 'topic' column header")
        rows: list[dict] = []
        for lineno, raw in enumerate(reader, start=2):
            topic_val = (raw.get("topic") or "").strip()
            if not topic_val:
                continue
            priority_raw = (raw.get("priority") or "").strip() or "0"
            try:
                priority_val = int(priority_raw)
            except ValueError:
                raise ValueError(
                    f"Row {lineno}: priority {priority_raw!r} is not an integer"
                )
            if priority_val < 0:
                raise ValueError(
                    f"Row {lineno}: priority must be >= 0, got {priority_val}"
                )
            row = {k: (v or "").strip() for k, v in raw.items()}
            row["_priority"] = priority_val
            rows.append(row)
        return rows


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------

@app.command()
def plan(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
) -> None:
    """Generate a structured editorial brief for an idea-stage item."""
    _ensure_db()
    from orchestrator.db import (
        get_source_documents,
        insert_content_brief,
        update_item_status,
    )
    from orchestrator.editorial import BriefGenerationError, generate_brief
    from orchestrator.state import ContentStatus, transition

    from orchestrator.state import InvalidTransitionError

    item = _resolve_item(item_id)
    try:
        transition(item["status"], ContentStatus.PLANNED)
    except InvalidTransitionError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    sources = get_source_documents(_db_path(), item["id"])
    source_payload = [
        {
            "title": s.get("title"),
            "url": s.get("url"),
            "excerpt": (s.get("markdown") or "")[:4000],
        }
        for s in sources
    ] or None

    console.print(f"[dim]Planning brief for[/dim] [bold]{item['topic']}[/bold] …")
    try:
        brief = generate_brief(
            topic=item["topic"],
            pillar=item.get("pillar"),
            audience=item.get("audience"),
            sources=source_payload,
        )
    except BriefGenerationError as e:
        console.print(f"[red]Brief generation failed:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:  # covers MissingAPIKeyError and other adapter errors
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    brief_id = insert_content_brief(
        _db_path(),
        content_item_id=item["id"],
        thesis=brief.thesis,
        angle=brief.angle,
        hook_options=brief.hook_options,
        cta=brief.cta,
        claims_to_verify=[c.model_dump() for c in brief.claims_to_verify],
        brand_notes=brief.brand_notes,
        risk_flags=[r.model_dump() for r in brief.risk_flags],
        source_refs=[s.model_dump() for s in brief.source_refs],
    )
    update_item_status(_db_path(), item["id"], ContentStatus.PLANNED.value)

    console.print(f"[green]✓[/green] Brief {brief_id[:12]} stored for item {item['id'][:12]}.")
    console.print(f"  thesis: {brief.thesis}")
    console.print(
        f"  hooks: {len(brief.hook_options)} · claims: {len(brief.claims_to_verify)} · "
        f"risks: {len(brief.risk_flags)} · sources: {len(brief.source_refs)}"
    )
    console.print(f"  status: [blue]idea[/blue] → [blue]planned[/blue]")


# ---------------------------------------------------------------------------
# script
# ---------------------------------------------------------------------------

@app.command()
def script(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    duration: int = typer.Option(60, "--duration", min=10, max=180, help="Target seconds."),
) -> None:
    """Generate script variants for a planned item."""
    _ensure_db()
    from orchestrator.db import (
        get_latest_brief,
        insert_script_variant,
        update_item_status,
    )
    from orchestrator.editorial import ScriptGenerationError, generate_scripts
    from orchestrator.models import BriefDraft, ClaimToVerify, RiskFlag, SourceRef
    from orchestrator.state import ContentStatus, transition
    import json as _json

    from orchestrator.state import InvalidTransitionError

    item = _resolve_item(item_id)
    try:
        transition(item["status"], ContentStatus.SCRIPTED)
    except InvalidTransitionError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    brief_row = get_latest_brief(_db_path(), item["id"])
    if not brief_row:
        console.print(f"[red]No brief found for item {item['id'][:12]}. Run `profusion plan` first.[/red]")
        raise typer.Exit(code=1)

    brief = BriefDraft(
        thesis=brief_row["thesis"],
        angle=brief_row.get("angle"),
        hook_options=_json.loads(brief_row.get("hook_options") or "[]"),
        cta=brief_row.get("cta"),
        claims_to_verify=[
            ClaimToVerify(**c) if isinstance(c, dict) else ClaimToVerify(claim=c)
            for c in _json.loads(brief_row.get("claims_to_verify") or "[]")
        ],
        brand_notes=brief_row.get("brand_notes"),
        risk_flags=[RiskFlag(**r) for r in _json.loads(brief_row.get("risk_flags") or "[]")],
        source_refs=[SourceRef(**s) for s in _json.loads(brief_row.get("source_refs") or "[]")],
    )

    console.print(f"[dim]Scripting variants for[/dim] [bold]{item['topic']}[/bold] …")
    try:
        variants = generate_scripts(
            topic=item["topic"],
            brief=brief,
            duration_target_seconds=duration,
        )
    except ScriptGenerationError as e:
        console.print(f"[red]Script generation failed:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:  # covers MissingAPIKeyError and other adapter errors
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    for v in variants:
        variant_id = insert_script_variant(
            _db_path(),
            content_item_id=item["id"],
            variant_name=v.variant_name,
            script_text=v.script_text,
            duration_target_seconds=v.duration_target_seconds,
        )
        console.print(
            f"[green]+[/green] {variant_id[:12]}  [bold]{v.variant_name}[/bold]  "
            f"({v.duration_target_seconds}s, {len(v.script_text)} chars)"
        )

    update_item_status(_db_path(), item["id"], ContentStatus.SCRIPTED.value)
    console.print(f"\n[green]✓[/green] {len(variants)} variant(s) stored.")
    console.print(f"  status: [blue]planned[/blue] → [cyan]scripted[/cyan]")


# ---------------------------------------------------------------------------
# Stub commands (later milestones)
# ---------------------------------------------------------------------------

def _stub(name: str) -> None:
    console.print(f"[yellow]{name}[/yellow] is not yet implemented (scheduled for a future milestone).")
    raise typer.Exit(code=0)


@app.command()
def render(
    item_id: str = typer.Option(..., "--item-id", help="Content item id (or unique prefix)."),
    variant: str = typer.Option(
        "straight_explainer", "--variant", help="Script variant name to render."
    ),
    wait: bool = typer.Option(False, "--wait", help="Poll until render completes."),
    max_polls: int = typer.Option(
        60, "--max-polls", help="Max poll attempts when --wait (×5s each, default 5 min)."
    ),
    force: bool = typer.Option(
        False, "--force", help="Submit even if a pending/processing job already exists."
    ),
) -> None:
    """Legacy/demo render path. Not part of the current B2B product promise."""
    import json as _json
    import time
    from dataclasses import asdict
    from datetime import datetime, timezone

    import httpx as _httpx

    from orchestrator import config
    from orchestrator.adapters import turbo
    from orchestrator.db import (
        get_render_jobs_by_variant,
        get_script_variants,
        insert_render_job,
        update_item_status,
        update_render_job,
    )
    from orchestrator.state import ContentStatus, InvalidTransitionError, transition

    console.print(
        "[yellow]Legacy demo path:[/yellow] live MoneyPrinter render/publish tooling has moved to "
        "/home/kyle/attention-media-lab. Profusion keeps this only for sanitized demo compatibility."
    )

    _ensure_db()
    item = _resolve_item(item_id)

    try:
        transition(item["status"], ContentStatus.RENDERED)
    except InvalidTransitionError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    variants = get_script_variants(_db_path(), item["id"])
    if not variants:
        console.print("[red]No script variants found. Run 'profusion script' first.[/red]")
        raise typer.Exit(code=1)

    variant_map = {v["variant_name"]: v for v in variants}
    if variant not in variant_map:
        console.print(
            f"[red]Variant {variant!r} not found.[/red] "
            f"Available: {sorted(variant_map.keys())}"
        )
        raise typer.Exit(code=1)

    selected = variant_map[variant]

    profile = turbo.RenderProfile()
    result: turbo.RenderJobResult | None = None

    if not force:
        existing = get_render_jobs_by_variant(_db_path(), selected["id"])
        active = [j for j in existing if j["status"] in ("pending", "processing")]
        if active:
            if wait:
                # Resume polling the existing job rather than blocking.
                result = turbo.RenderJobResult(
                    task_id=active[0]["id"], status=active[0]["status"]
                )
                console.print(
                    f"[yellow]Resuming wait for existing job:[/yellow] "
                    f"{result.task_id} ({active[0]['status']})"
                )
            else:
                console.print(
                    f"[yellow]Active render job already exists:[/yellow] "
                    f"{active[0]['id']} ({active[0]['status']})"
                )
                console.print("Use --force to submit a new job anyway.")
                raise typer.Exit(code=0)

    if result is None:
        console.print(
            f"[dim]Submitting render for[/dim] [bold]{item['topic']}[/bold] "
            f"(variant: {variant}) …"
        )
        try:
            result = turbo.render(
                subject=item["topic"],
                script=selected["script_text"],
                profile=profile,
            )
        except turbo.TurboUnavailableError as e:
            console.print(f"[red]Render failed:[/red] {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

        insert_render_job(
            _db_path(),
            task_id=result.task_id,
            script_variant_id=selected["id"],
            render_profile=asdict(profile),
        )
        console.print(f"[green]Render job submitted:[/green] {result.task_id}")

    if not wait:
        console.print("Re-run with [bold]--wait[/bold] to poll for completion.")
        return

    POLL_INTERVAL = 5
    console.print(f"Polling every {POLL_INTERVAL}s (max {max_polls} polls) …")
    job_status: turbo.RenderJobResult | None = None

    for poll_num in range(max_polls):
        time.sleep(POLL_INTERVAL)
        try:
            job_status = turbo.get_job_status(result.task_id)
        except turbo.TurboUnavailableError as e:
            log_path = _write_render_log(
                result, config.LOGS_DIR,
                job_status=None, poll_num=poll_num, max_polls=max_polls, error=str(e),
            )
            update_render_job(_db_path(), result.task_id, status="failed", log_path=log_path)
            console.print(f"[red]Poll failed:[/red] {e}")
            raise typer.Exit(code=1)

        console.print(
            f"  [{poll_num + 1}/{max_polls}] {job_status.status} ({job_status.progress}%)"
        )

        if job_status.status == "completed":
            if not job_status.output_url:
                log_path = _write_render_log(
                    result, config.LOGS_DIR,
                    job_status=job_status, poll_num=poll_num, max_polls=max_polls,
                    error="Turbo returned completed but no video URL",
                )
                update_render_job(_db_path(), result.task_id, status="failed", log_path=log_path)
                console.print(
                    "[red]Render completed by Turbo but no video URL returned.[/red]"
                )
                raise typer.Exit(code=1)

            renders_dir = config.RENDERS_DIR / result.task_id
            renders_dir.mkdir(parents=True, exist_ok=True)
            dest = renders_dir / "final.mp4"

            try:
                mp4_resp = _httpx.get(job_status.output_url, timeout=120.0)
                mp4_resp.raise_for_status()
                dest.write_bytes(mp4_resp.content)
                if dest.stat().st_size == 0:
                    raise ValueError("Downloaded MP4 is empty (0 bytes)")
            except Exception as download_err:
                log_path = _write_render_log(
                    result, config.LOGS_DIR,
                    job_status=job_status, poll_num=poll_num, max_polls=max_polls,
                    error=f"{type(download_err).__name__}: {download_err}",
                )
                update_render_job(_db_path(), result.task_id, status="failed", log_path=log_path)
                console.print(f"[red]MP4 download failed:[/red] {download_err}")
                raise typer.Exit(code=1)

            output_path = str(dest)
            manifest = {
                "content_item_id": item["id"],
                "script_variant_id": selected["id"],
                "task_id": result.task_id,
                "render_profile": asdict(profile),
                "output_path": output_path,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            (renders_dir / "manifest.json").write_text(
                _json.dumps(manifest, indent=2), encoding="utf-8"
            )

            update_render_job(_db_path(), result.task_id, status="completed", output_path=output_path)
            update_item_status(_db_path(), item["id"], ContentStatus.RENDERED.value)
            console.print(
                f"[green]✓[/green] Render complete!  "
                f"status: [cyan]scripted[/cyan] → [yellow]rendered[/yellow]"
            )
            console.print(f"  output: {output_path}")
            return

        if job_status.status == "failed":
            log_path = _write_render_log(
                result, config.LOGS_DIR,
                job_status=job_status, poll_num=poll_num, max_polls=max_polls,
                error="Turbo reported task failed",
            )
            update_render_job(_db_path(), result.task_id, status="failed", log_path=log_path)
            console.print("[red]Render job failed.[/red]")
            raise typer.Exit(code=1)

    log_path = _write_render_log(
        result, config.LOGS_DIR,
        job_status=job_status, poll_num=max_polls - 1, max_polls=max_polls,
        error=f"Timed out after {max_polls} polls (last status: {job_status.status if job_status else 'unknown'})",
    )
    update_render_job(_db_path(), result.task_id, status="failed", log_path=log_path)
    console.print(f"[red]Timed out after {max_polls} polls.[/red]")
    raise typer.Exit(code=1)


def _write_render_log(
    result: "turbo.RenderJobResult",
    logs_dir: "Path",
    *,
    job_status: "turbo.RenderJobResult | None",
    poll_num: int,
    max_polls: int,
    error: str,
) -> str | None:
    from datetime import datetime, timezone

    actual = job_status or result
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / f"render-{result.task_id}.log"
        log_file.write_text(
            f"task_id: {result.task_id}\n"
            f"poll: {poll_num + 1}/{max_polls}\n"
            f"status: {actual.status}\n"
            f"progress: {actual.progress}\n"
            f"output_url: {actual.output_url}\n"
            f"error: {error}\n"
            f"timestamp: {datetime.now(timezone.utc).isoformat()}\n",
            encoding="utf-8",
        )
        return str(log_file)
    except Exception:
        return None


@app.command()
def qa(
    item_id: str = typer.Option(..., "--item-id"),
) -> None:
    """Run QA checks on a rendered content item."""
    import json as _json
    from datetime import datetime

    from orchestrator import config, db, editorial
    from orchestrator.diagnostics import write_diagnostic
    from orchestrator.state import ContentStatus, InvalidTransitionError, transition

    _ensure_db()
    item = _resolve_item(item_id)

    try:
        transition(item["status"], ContentStatus.QA_PASSED)
    except InvalidTransitionError:
        typer.echo(f"[error] Item {item_id!r} is in status {item['status']!r}, expected 'rendered'")
        raise typer.Exit(1)

    render_job = db.get_completed_render_job_for_item(config.DB_PATH, item["id"])
    if render_job is None:
        typer.echo(f"[error] No completed render job found for item {item_id!r}")
        raise typer.Exit(1)

    if not render_job["output_path"]:
        db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
        typer.echo(f"[qa_failed] Completed render job has no output_path recorded")
        raise typer.Exit(1)

    output_path = Path(render_job["output_path"])
    if not output_path.exists() or output_path.stat().st_size == 0:
        db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
        typer.echo(f"[qa_failed] Render artifact missing or empty: {output_path}")
        raise typer.Exit(1)

    manifest_path = output_path.parent / "manifest.json"
    if not manifest_path.exists():
        db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
        typer.echo(f"[qa_failed] manifest.json not found at {manifest_path}")
        raise typer.Exit(1)
    try:
        manifest = _json.loads(manifest_path.read_text())
    except (ValueError, OSError) as e:
        db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
        typer.echo(f"[qa_failed] Could not parse manifest.json: {e}")
        raise typer.Exit(1)

    mismatches = []
    if manifest.get("content_item_id") != item["id"]:
        mismatches.append(
            f"content_item_id: manifest={manifest.get('content_item_id')!r} db={item['id']!r}"
        )
    if manifest.get("task_id") != render_job["id"]:
        mismatches.append(
            f"task_id: manifest={manifest.get('task_id')!r} db={render_job['id']!r}"
        )
    if manifest.get("script_variant_id") != render_job["script_variant_id"]:
        mismatches.append(
            f"script_variant_id: manifest={manifest.get('script_variant_id')!r} "
            f"db={render_job['script_variant_id']!r}"
        )
    if manifest.get("output_path") != str(output_path):
        mismatches.append(
            f"output_path: manifest={manifest.get('output_path')!r} db={str(output_path)!r}"
        )
    if mismatches:
        db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
        typer.echo("[qa_failed] Manifest mismatch:\n" + "\n".join(f"  {m}" for m in mismatches))
        raise typer.Exit(1)

    brief = db.get_latest_brief(config.DB_PATH, item["id"])
    if brief is None:
        db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
        typer.echo(f"[qa_failed] No brief found for item {item_id!r}")
        raise typer.Exit(1)
    brief_dict = dict(brief)
    for field in ("claims_to_verify", "risk_flags", "source_refs", "hook_options"):
        if isinstance(brief_dict.get(field), str):
            try:
                brief_dict[field] = _json.loads(brief_dict[field])
            except ValueError:
                db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
                typer.echo(f"[qa_failed] Brief field {field!r} contains invalid JSON")
                raise typer.Exit(1)

    variants = db.get_script_variants(config.DB_PATH, item["id"])
    variant_map = {v["id"]: v for v in variants}
    variant = variant_map.get(render_job["script_variant_id"])
    script_text = variant["script_text"] if variant else ""

    try:
        qa_result = editorial.run_qa_check(
            topic=item["topic"],
            script_text=script_text,
            brief_dict=brief_dict,
        )
    except Exception as e:
        write_diagnostic(
            config.LOGS_DIR,
            stage="qa",
            item_id=item["id"],
            job_id=render_job["id"],
            error=e,
            error_code=type(e).__name__,
            context={"status": item["status"]},
        )
        typer.echo(f"[error] QA check failed, item left as rendered: {e}")
        raise typer.Exit(1)

    report = {
        "content_item_id": item["id"],
        "task_id": render_job["id"],
        "overall_go_no_go": qa_result.overall_go_no_go,
        "risk_flags": [rf.model_dump() for rf in qa_result.risk_flags],
        "claims_to_verify": [c.model_dump() for c in qa_result.claims_to_verify],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    report_path = output_path.parent / "qa_report.json"
    try:
        report_path.write_text(_json.dumps(report, indent=2))
    except OSError as e:
        write_diagnostic(
            config.LOGS_DIR,
            stage="qa",
            item_id=item["id"],
            job_id=render_job["id"],
            error=e,
            error_code=type(e).__name__,
            context={"report_path": str(report_path)},
        )
        typer.echo(f"[error] Failed to write qa_report.json, item left as rendered: {e}")
        raise typer.Exit(1)

    if qa_result.overall_go_no_go == "go":
        db.update_item_status(config.DB_PATH, item["id"], "qa_passed")
        typer.echo(f"[qa_passed] QA passed. Report: {report_path}")
    else:
        db.update_item_status(config.DB_PATH, item["id"], "qa_failed")
        flags = "\n".join(
            f"  [{f.category}] {f.description}" for f in qa_result.risk_flags
        )
        typer.echo(f"[qa_failed] Hold verdict. Risk flags:\n{flags}")
        raise typer.Exit(1)


@app.command()
def approve(
    item_id: str = typer.Option(..., "--item-id"),
    decision: str = typer.Option(
        "approved",
        "--decision",
        help="approved | rejected | revision_requested",
    ),
    notes: str | None = typer.Option(None, "--notes"),
    operator: str = typer.Option("operator", "--operator"),
) -> None:
    """Record an approval decision for a qa_passed content item."""
    from orchestrator import config, db
    from orchestrator.state import InvalidTransitionError

    _ensure_db()
    item = _resolve_item(item_id)

    valid_decisions = {"approved", "rejected", "revision_requested"}
    if decision not in valid_decisions:
        typer.echo(
            f"[error] Unknown decision {decision!r}. "
            f"Choose from: {', '.join(sorted(valid_decisions))}"
        )
        raise typer.Exit(2)

    try:
        record_id = db.record_approval_decision(
            config.DB_PATH,
            content_item_id=item["id"],
            decision=decision,
            approved_by=operator,
            notes=notes,
        )
    except (ValueError, InvalidTransitionError) as e:
        typer.echo(f"[error] {e}")
        raise typer.Exit(1)

    _DECISION_FINAL = {
        "approved": "approved",
        "rejected": "archived",
        "revision_requested": "scripted",
    }
    final = _DECISION_FINAL[decision]
    typer.echo(
        f"[{final}] Decision={decision!r} recorded (record={record_id}) "
        f"qa_passed → awaiting_approval → {final}"
    )


@app.command()
def schedule(
    item_id: str = typer.Option(..., "--item-id"),
    at: str = typer.Option(
        ...,
        "--at",
        help="ISO datetime with timezone offset, e.g. 2026-04-21T09:00:00-05:00",
    ),
    target: list[str] | None = typer.Option(
        None,
        "--target",
        help="Repeatable PostBridge target in platform:account_id form.",
    ),
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
    metadata: str | None = typer.Option(
        None,
        "--metadata",
        help="Optional JSON object for platform-specific scheduling metadata.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow duplicate identical scheduled targets intentionally.",
    ),
) -> None:
    """Schedule approved content for future publication."""
    from orchestrator import config, db
    from orchestrator.state import InvalidTransitionError

    _ensure_db()
    item = _resolve_item(item_id)

    if item["status"] != "approved":
        typer.echo(f"[error] Item {item_id!r} is in status {item['status']!r}, expected 'approved'")
        raise typer.Exit(1)

    try:
        scheduled_for = _normalize_iso_datetime(at)
        parsed_targets = _parse_schedule_targets(target)
        metadata_obj = _load_platform_metadata(metadata)
        if len(set(parsed_targets)) != len(parsed_targets) and not force:
            raise ValueError("Duplicate --target values require --force")
        if not force:
            for platform, account_id in parsed_targets:
                existing = db.find_duplicate_scheduled_publish_jobs(
                    config.DB_PATH,
                    content_item_id=item["id"],
                    platform=platform,
                    account_id=account_id,
                    scheduled_for=scheduled_for,
                )
                if existing:
                    raise ValueError(
                        f"Duplicate scheduled target exists for {platform}:{account_id} at {scheduled_for}; use --force to create another"
                    )
        _validate_publish_package(item)
    except (ValueError, PublishPackageError) as e:
        typer.echo(f"[error] {e}")
        raise typer.Exit(1)

    jobs = [
        {
            "platform": platform,
            "account_id": account_id,
            "title": title or item.get("topic", ""),
            "description": description or "",
            "scheduled_for": scheduled_for,
            "platform_metadata": _metadata_for_platform(metadata_obj, platform),
        }
        for platform, account_id in parsed_targets
    ]

    try:
        job_ids = db.record_schedule_created(
            config.DB_PATH,
            content_item_id=item["id"],
            jobs=jobs,
        )
    except (ValueError, InvalidTransitionError) as e:
        typer.echo(f"[error] {e}")
        raise typer.Exit(1)

    targets = ", ".join(
        f"{platform}:{account_id}" for platform, account_id in parsed_targets
    )
    typer.echo(
        f"[scheduled] item={item['id']} at={scheduled_for} targets={targets} "
        f"jobs={len(job_ids)}"
    )


@app.command()
def publish(
    item_id: str = typer.Option(..., "--item-id"),
    platform: str = typer.Option(..., "--platform", help="PostBridge platform slug (e.g. youtube_shorts, tiktok)"),
    account_id: int = typer.Option(..., "--account-id", help="PostBridge social account ID"),
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    """Legacy/demo publish path. Not part of the current B2B product promise."""
    from orchestrator import config, db
    from orchestrator.adapters import v2
    from orchestrator.diagnostics import write_diagnostic
    from orchestrator.state import InvalidTransitionError

    console.print(
        "[yellow]Legacy demo path:[/yellow] live MoneyPrinter render/publish tooling has moved to "
        "/home/kyle/attention-media-lab. Profusion keeps this only for sanitized demo compatibility."
    )

    _ensure_db()
    item = _resolve_item(item_id)

    if item["status"] != "approved":
        typer.echo(f"[error] Item {item_id!r} is in status {item['status']!r}, expected 'approved'")
        raise typer.Exit(1)

    try:
        mp4_path = _validate_publish_package(item)
    except PublishPackageError as e:
        typer.echo(f"[error] {e}")
        raise typer.Exit(1)

    api_key = config.POST_BRIDGE_API_KEY
    if not api_key:
        typer.echo("[error] POST_BRIDGE_API_KEY is not set in .env")
        raise typer.Exit(1)

    job_id = db.insert_publish_job(
        config.DB_PATH,
        content_item_id=item["id"],
        platform=platform,
        account_id=account_id,
        title=title or item.get("topic", ""),
        description=description or "",
    )

    profile = v2.PublishProfile(
        platform=platform,
        account_id=account_id,
        api_key=api_key,
        title=title or item.get("topic", ""),
        description=description or "",
    )

    try:
        result = v2.publish(str(mp4_path), profile)
    except Exception as e:
        log_path, _ = write_diagnostic(
            config.LOGS_DIR,
            stage="publish",
            item_id=item["id"],
            job_id=job_id,
            attempt=1,
            error=e,
            error_code=type(e).__name__,
            context={"platform": platform, "account_id": account_id},
        )
        db.mark_publish_job_failed(
            config.DB_PATH,
            job_id,
            str(e),
            error_code=type(e).__name__,
            log_path=log_path,
        )
        typer.echo(f"[error] Publishing failed, item remains 'approved': {e}")
        raise typer.Exit(1)

    try:
        db.record_publish_complete(
            config.DB_PATH,
            content_item_id=item["id"],
            job_id=job_id,
            published_url=result.published_url,
            external_post_id=result.external_post_id,
        )
    except (ValueError, InvalidTransitionError) as e:
        log_path, _ = write_diagnostic(
            config.LOGS_DIR,
            stage="publish",
            item_id=item["id"],
            job_id=job_id,
            attempt=1,
            error=e,
            error_code=type(e).__name__,
            context={"phase": "record_publish_complete"},
        )
        db.mark_publish_job_failed(
            config.DB_PATH,
            job_id,
            str(e),
            error_code=type(e).__name__,
            log_path=log_path,
        )
        typer.echo(f"[error] State transition failed: {e}")
        raise typer.Exit(1)

    typer.echo(
        f"[published] platform={platform!r} post_id={result.external_post_id!r} "
        f"url={result.published_url!r}"
    )


@app.command("publish-due")
def publish_due(
    now: str | None = typer.Option(
        None,
        "--now",
        help="Override current time as ISO datetime with timezone offset.",
    ),
    limit: int = typer.Option(100, "--limit", min=1),
) -> None:
    """Legacy/demo scheduled publish path. Not part of the current B2B product promise."""
    from orchestrator import config, db
    from orchestrator.adapters import v2
    from orchestrator.diagnostics import write_diagnostic
    from orchestrator.state import InvalidTransitionError

    console.print(
        "[yellow]Legacy demo path:[/yellow] live MoneyPrinter render/publish tooling has moved to "
        "/home/kyle/attention-media-lab. Profusion keeps this only for sanitized demo compatibility."
    )

    _ensure_db()
    if now:
        try:
            now_utc = _normalize_iso_datetime(now)
        except ValueError as e:
            typer.echo(f"[error] {e}")
            raise typer.Exit(1)
    else:
        now_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )

    api_key = config.POST_BRIDGE_API_KEY
    if not api_key:
        typer.echo("[error] POST_BRIDGE_API_KEY is not set in .env")
        raise typer.Exit(1)

    jobs = db.get_due_publish_jobs(config.DB_PATH, now=now_utc, limit=limit)
    if not jobs:
        typer.echo(f"[dim]No scheduled publish jobs due at {now_utc}.[/dim]")
        return

    failures = 0
    completed = 0
    for job in jobs:
        job_id = job["id"]
        item = db.get_item(config.DB_PATH, job["content_item_id"])
        if item is None:
            log_path, _ = write_diagnostic(
                config.LOGS_DIR,
                stage="publish",
                job_id=job_id,
                error="Content item not found",
                error_code="ContentItemMissing",
            )
            db.mark_publish_job_failed(
                config.DB_PATH,
                job_id,
                "Content item not found",
                error_code="ContentItemMissing",
                log_path=log_path,
            )
            typer.echo(f"[error] job={job_id} content item not found")
            failures += 1
            continue
        if item["status"] != "scheduled":
            error = (
                f"Item {item['id']} is in status {item['status']!r}, expected 'scheduled'"
            )
            log_path, _ = write_diagnostic(
                config.LOGS_DIR,
                stage="publish",
                item_id=item["id"],
                job_id=job_id,
                error=error,
                error_code="InvalidItemStatus",
            )
            db.mark_publish_job_failed(
                config.DB_PATH,
                job_id,
                error,
                error_code="InvalidItemStatus",
                log_path=log_path,
            )
            typer.echo(f"[error] job={job_id} {error}")
            failures += 1
            continue
        if job.get("account_id") is None:
            log_path, _ = write_diagnostic(
                config.LOGS_DIR,
                stage="publish",
                item_id=item["id"],
                job_id=job_id,
                error="Missing account_id",
                error_code="MissingAccountId",
            )
            db.mark_publish_job_failed(
                config.DB_PATH,
                job_id,
                "Missing account_id",
                error_code="MissingAccountId",
                log_path=log_path,
            )
            typer.echo(f"[error] job={job_id} missing account_id")
            failures += 1
            continue

        try:
            mp4_path = _validate_publish_package(item)
        except PublishPackageError as e:
            log_path, _ = write_diagnostic(
                config.LOGS_DIR,
                stage="publish",
                item_id=item["id"],
                job_id=job_id,
                error=e,
                error_code="PublishPackageError",
            )
            db.mark_publish_job_failed(
                config.DB_PATH,
                job_id,
                str(e),
                error_code="PublishPackageError",
                log_path=log_path,
            )
            typer.echo(f"[error] job={job_id} package validation failed: {e}")
            failures += 1
            continue

        db.mark_publish_job_processing(config.DB_PATH, job_id)
        profile = v2.PublishProfile(
            platform=job["platform"],
            account_id=int(job["account_id"]),
            api_key=api_key,
            title=job.get("title") or item.get("topic", ""),
            description=job.get("description") or "",
        )
        try:
            result = v2.publish(str(mp4_path), profile)
            item_published = db.record_scheduled_publish_complete(
                config.DB_PATH,
                content_item_id=item["id"],
                job_id=job_id,
                published_url=result.published_url,
                external_post_id=result.external_post_id,
            )
        except (Exception, InvalidTransitionError) as e:
            log_path, _ = write_diagnostic(
                config.LOGS_DIR,
                stage="publish",
                item_id=item["id"],
                job_id=job_id,
                attempt=(job.get("attempt_count") or 0) + 1,
                error=e,
                error_code=type(e).__name__,
                context={"platform": job["platform"], "account_id": job.get("account_id")},
            )
            db.mark_publish_job_failed(
                config.DB_PATH,
                job_id,
                str(e),
                error_code=type(e).__name__,
                log_path=log_path,
            )
            typer.echo(f"[error] job={job_id} publishing failed: {e}")
            failures += 1
            continue

        completed += 1
        status_note = " item=published" if item_published else ""
        typer.echo(
            f"[published] job={job_id} platform={job['platform']!r} "
            f"post_id={result.external_post_id!r}{status_note}"
        )

    if failures:
        typer.echo(f"[error] publish-due completed with {failures} failure(s), {completed} completed")
        raise typer.Exit(1)
    typer.echo(f"[done] publish-due completed {completed} job(s)")


@app.command()
def retry(
    item_id: str | None = typer.Option(None, "--item-id", help="Content item id (or unique prefix)."),
    job_id: str | None = typer.Option(None, "--job-id", help="Publish job id to retry."),
    render_job_id: str | None = typer.Option(None, "--render-job-id", help="Render job id to retry."),
    stage: str | None = typer.Option(None, "--stage", help="Stage retry for --item-id, currently: qa."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Retry a failed render, QA, or publish surface without direct DB edits."""
    from orchestrator import config, db
    from orchestrator.retry import (
        RetryError,
        retry_publish_job,
        retry_qa_stage,
        retry_render_job,
    )

    _ensure_db()
    targets = [bool(item_id), bool(job_id), bool(render_job_id)]
    if sum(targets) != 1:
        typer.echo("[error] Provide exactly one of --item-id, --job-id, or --render-job-id")
        raise typer.Exit(2)

    try:
        if job_id:
            payload = retry_publish_job(
                config.DB_PATH,
                config.LOGS_DIR,
                job_id=job_id,
                api_key=config.POST_BRIDGE_API_KEY,
            )
        elif render_job_id:
            payload = retry_render_job(
                config.DB_PATH,
                config.LOGS_DIR,
                render_job_id=render_job_id,
            )
        else:
            item = _resolve_item(item_id or "")
            if stage == "qa":
                payload = retry_qa_stage(config.DB_PATH, item_id=item["id"])
            elif stage is None:
                failed_publish = [
                    j for j in db.get_publish_jobs_for_item(config.DB_PATH, item["id"])
                    if j["status"] == "failed"
                ]
                failed_render = [
                    j for j in db.get_render_jobs_for_item(config.DB_PATH, item["id"])
                    if j["status"] == "failed"
                ]
                options = []
                if item["status"] == "qa_failed":
                    options.append(("qa", item["id"]))
                options.extend(("publish", j["id"]) for j in failed_publish)
                options.extend(("render", j["id"]) for j in failed_render)
                if len(options) != 1:
                    choices = ", ".join(f"{kind}:{ident}" for kind, ident in options) or "none"
                    raise RetryError(
                        f"Cannot infer a single retry surface for item {item['id']}; candidates: {choices}"
                    )
                kind, ident = options[0]
                if kind == "qa":
                    payload = retry_qa_stage(config.DB_PATH, item_id=ident)
                elif kind == "publish":
                    payload = retry_publish_job(
                        config.DB_PATH,
                        config.LOGS_DIR,
                        job_id=ident,
                        api_key=config.POST_BRIDGE_API_KEY,
                    )
                else:
                    payload = retry_render_job(
                        config.DB_PATH,
                        config.LOGS_DIR,
                        render_job_id=ident,
                    )
            else:
                raise RetryError(f"Unsupported retry stage {stage!r}; currently supported: qa")
    except RetryError as e:
        typer.echo(f"[error] {e}")
        raise typer.Exit(1)

    if json_output:
        _emit_json(payload)
        return
    typer.echo(f"[retry] {payload['action']}")
    if payload.get("new_job_id"):
        typer.echo(f"new_job_id={payload['new_job_id']}")
    if payload.get("new_render_job_id"):
        typer.echo(f"new_render_job_id={payload['new_render_job_id']}")
    if payload.get("next_safe_command"):
        typer.echo(f"next: {payload['next_safe_command']}")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind address."),
    port: int = typer.Option(4000, "--port", help="TCP port."),
    dev: bool = typer.Option(False, "--dev", help="Enable CORS for Vite dev server on :5173."),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on source changes."),
) -> None:
    """Start the local operator dashboard API server."""
    import os

    try:
        import uvicorn  # noqa: F401
    except ImportError:
        console.print("[red]uvicorn is not installed. Run: uv sync[/red]")
        raise typer.Exit(1)

    _ensure_db()
    if dev:
        os.environ["PROFUSION_DEV"] = "1"
    console.print(f"[bold]Profusion dashboard API[/bold] → http://{host}:{port}")
    if dev:
        console.print("[dim]Dev mode: CORS enabled for http://localhost:5173[/dim]")
    import uvicorn as _uvicorn

    _uvicorn.run("orchestrator.api:app", host=host, port=port, reload=reload)


@app.command()
def smoke(
    offline: bool = typer.Option(False, "--offline", help="Run fixture-backed smoke checks without live vendor calls."),
) -> None:
    """Run a local smoke path for M6 operator surfaces."""
    if not offline:
        typer.echo("[error] Only --offline smoke is implemented for M6")
        raise typer.Exit(2)

    import tempfile
    from orchestrator import db
    from orchestrator.read_models import handoff_payload, inspect_payload, status_payload
    from orchestrator.retry import retry_qa_stage

    with tempfile.TemporaryDirectory(prefix="profusion-smoke-") as tmp:
        root = Path(tmp)
        db_path = root / "content.db"
        logs_dir = root / "logs"
        renders_dir = root / "renders" / "smoke-render"
        renders_dir.mkdir(parents=True)
        mp4_path = renders_dir / "final.mp4"
        mp4_path.write_bytes(b"SMOKE_MP4")

        db.init_db(db_path)
        item_id = db.insert_content_item(db_path, topic="offline smoke topic")
        db.update_item_status(db_path, item_id, "planned")
        db.insert_content_brief(
            db_path,
            content_item_id=item_id,
            thesis="Smoke thesis",
            angle=None,
            hook_options=[],
            cta=None,
            claims_to_verify=[],
            brand_notes=None,
            risk_flags=[],
            source_refs=[],
        )
        db.update_item_status(db_path, item_id, "scripted")
        variant_id = db.insert_script_variant(
            db_path,
            content_item_id=item_id,
            variant_name="straight_explainer",
            script_text="Smoke script.",
        )
        (renders_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "content_item_id": item_id,
                    "script_variant_id": variant_id,
                    "task_id": "smoke-render",
                    "output_path": str(mp4_path),
                    "created_at": "2026-04-20T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        db.insert_render_job(
            db_path,
            task_id="smoke-render",
            script_variant_id=variant_id,
            render_profile={},
        )
        db.update_render_job(
            db_path,
            "smoke-render",
            status="completed",
            output_path=str(mp4_path),
        )
        db.update_item_status(db_path, item_id, "rendered")
        db.update_item_status(db_path, item_id, "qa_failed")

        status_doc = status_payload(db_path)
        item = db.get_item(db_path, item_id)
        inspect_doc = inspect_payload(db_path, logs_dir, item)
        handoff_doc = handoff_payload(db_path, logs_dir, item=item)
        retry_doc = retry_qa_stage(db_path, item_id=item_id)
        due = db.get_due_publish_jobs(db_path, now="2026-04-20T00:00:00Z")

        checks = {
            "status_payload": bool(status_doc["items"]),
            "inspect_next_command": bool(inspect_doc["next_safe_command"]),
            "handoff_items": bool(handoff_doc["items"]),
            "qa_retry": retry_doc["action"] == "returned_to_rendered_for_qa",
            "due_runner_skip": due == [],
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            typer.echo(f"[error] offline smoke failed: {', '.join(failed)}")
            raise typer.Exit(1)
        typer.echo("[ok] offline smoke passed")
