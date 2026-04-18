"""Profusion CLI — operator entry point.

Usage: profusion <command> [options]
"""

from __future__ import annotations

import subprocess
import sys
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


def _db_path() -> Path:
    from orchestrator import config
    return config.DB_PATH


def _ensure_db() -> None:
    from orchestrator.db import init_db
    init_db(_db_path())


# ---------------------------------------------------------------------------
# Real commands
# ---------------------------------------------------------------------------

@app.command()
def status() -> None:
    """Show the current content queue grouped by status."""
    _ensure_db()
    from orchestrator.db import get_all_items

    items = get_all_items(_db_path())

    table = Table(title="Profusion Content Queue", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Topic", min_width=30)
    table.add_column("Status", style="bold")
    table.add_column("Pillar")
    table.add_column("Priority", justify="right")

    if not items:
        console.print("[dim]Queue is empty. Use [bold]profusion ingest[/bold] to add topics.[/dim]")
        return

    status_colors = {
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

    for item in items:
        s = item["status"]
        color = status_colors.get(s, "white")
        table.add_row(
            item["id"][:8],
            item["topic"],
            f"[{color}]{s}[/{color}]",
            item["pillar"] or "—",
            str(item["priority"]),
        )

    console.print(table)


@app.command("check-env")
def check_env() -> None:
    """Check environment dependencies (ffmpeg, NVENC, API key)."""
    console.print("[bold]Profusion environment check[/bold]\n")

    # --- ffmpeg + NVENC ---
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

    # --- Anthropic API key ---
    from orchestrator import config
    if config.ANTHROPIC_API_KEY:
        console.print("[green]✓[/green] ANTHROPIC_API_KEY: set")
    else:
        console.print("[red]✗[/red] ANTHROPIC_API_KEY: not set — copy .env.example to .env")

    # --- Firecrawl ---
    import httpx
    try:
        r = httpx.get(f"{config.FIRECRAWL_URL}/health", timeout=3)
        if r.status_code < 400:
            console.print(f"[green]✓[/green] Firecrawl: reachable at {config.FIRECRAWL_URL}")
        else:
            console.print(f"[yellow]~[/yellow] Firecrawl: {config.FIRECRAWL_URL} returned {r.status_code}")
    except Exception:
        console.print(f"[yellow]~[/yellow] Firecrawl: not reachable at {config.FIRECRAWL_URL} (start service or ignore for now)")

    console.print()


# ---------------------------------------------------------------------------
# Stub commands (implemented in later milestones)
# ---------------------------------------------------------------------------

def _stub(name: str) -> None:
    console.print(f"[yellow]{name}[/yellow] is not yet implemented (scheduled for a future milestone).")
    raise typer.Exit(code=0)


@app.command()
def ingest() -> None:
    """Ingest topics into the content queue. (M1)"""
    _stub("ingest")


@app.command()
def plan() -> None:
    """Generate content briefs and editorial plans for queued topics. (M1)"""
    _stub("plan")


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
