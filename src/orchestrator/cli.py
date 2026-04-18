"""Profusion CLI — operator entry point.

Usage: profusion <command> [options]
"""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="profusion",
    help="Profusion Content Pipeline — semi-autonomous educational media engine.",
    no_args_is_help=True,
)
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


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@app.command()
def status(
    status_filter: str | None = typer.Option(
        None, "--status", help="Filter by lifecycle status (e.g. idea, planned)."
    ),
) -> None:
    """Show the current content queue."""
    _ensure_db()
    from orchestrator.db import get_all_items
    from orchestrator.state import ContentStatus

    if status_filter is not None:
        try:
            ContentStatus(status_filter)
        except ValueError:
            valid = ", ".join(s.value for s in ContentStatus)
            console.print(f"[red]Unknown status {status_filter!r}.[/red] Valid: {valid}")
            raise typer.Exit(code=2)

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
def render() -> None:
    """Render scripted content via MoneyPrinterTurbo. (M2)"""
    _stub("render")


@app.command()
def qa() -> None:
    """Run QA checks on rendered artifacts. (M3)"""
    _stub("qa")


@app.command()
def approve() -> None:
    """Mark a content item as approved for publishing. (M3)"""
    _stub("approve")


@app.command()
def schedule() -> None:
    """Schedule approved content for publication. (M5)"""
    _stub("schedule")


@app.command()
def publish() -> None:
    """Publish approved content via MoneyPrinterV2. (M4)"""
    _stub("publish")


@app.command()
def retry() -> None:
    """Retry a failed stage for a content item. (M3)"""
    _stub("retry")
