"""Pond CLI - Command-line interface for Alpha's memory system."""

import sys
from typing import Annotated, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from .client import PondClient

app = typer.Typer(
    name="pond",
    help="Pond CLI - Alpha's memory system",
    no_args_is_help=True,
)

console = Console()


def get_client() -> PondClient:
    """Get a configured Pond client."""
    try:
        return PondClient()
    except ValueError as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def format_memory(mem: dict, index: int | None = None) -> str:
    """Format a single memory for display."""
    content = mem.get("content", "")
    created = mem.get("created_at", "")[:10]  # Just the date
    tags = mem.get("tags", [])

    lines = []
    if index is not None:
        lines.append(f"[bold cyan]#{index}[/bold cyan] [dim]({created})[/dim]")
    else:
        lines.append(f"[dim]({created})[/dim]")

    lines.append(content)

    if tags:
        tag_str = ", ".join(f"[dim]#{t}[/dim]" for t in tags[:5])
        lines.append(tag_str)

    return "\n".join(lines)


@app.command()
def store(
    content: Annotated[
        Optional[str],
        typer.Argument(help="Memory content (or read from stdin if not provided)"),
    ] = None,
    tags: Annotated[
        Optional[str],
        typer.Option("--tags", "-t", help="Comma-separated tags"),
    ] = None,
):
    """Store a memory in Pond."""
    # Read from stdin if no content provided
    if content is None:
        if sys.stdin.isatty():
            rprint("[yellow]Enter memory content (Ctrl+D to finish):[/yellow]")
        content = sys.stdin.read().strip()

    if not content:
        rprint("[red]Error:[/red] No content provided")
        raise typer.Exit(1)

    client = get_client()
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    try:
        result = client.store(content, tag_list)

        rprint("[green]✓ Memory stored[/green]")

        # Show splash (related memories) if present
        splash = result.get("splash", [])
        if splash:
            rprint("\n[dim]Related memories (splash):[/dim]")
            for i, mem in enumerate(splash[:3], 1):
                rprint(format_memory(mem, i))
                rprint()

    except Exception as e:
        rprint(f"[red]Error storing memory:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 10,
):
    """Search memories in Pond."""
    client = get_client()

    try:
        result = client.search(query, limit)
        memories = result.get("memories", [])

        if memories:
            rprint(f"[dim]Found {len(memories)} memories:[/dim]\n")
            for i, mem in enumerate(memories, 1):
                rprint(format_memory(mem, i))
                rprint()
        else:
            rprint("[yellow]No memories found[/yellow]")

    except Exception as e:
        rprint(f"[red]Error searching:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def recent(
    hours: Annotated[float, typer.Option("--hours", "-h", help="Hours to look back")] = 24,
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 10,
):
    """Get recent memories from Pond."""
    client = get_client()

    try:
        result = client.recent(hours, limit)
        memories = result.get("memories", [])

        if memories:
            rprint(f"[dim]Recent {len(memories)} memories (last {hours}h):[/dim]\n")
            for i, mem in enumerate(memories, 1):
                rprint(format_memory(mem, i))
                rprint()
        else:
            rprint("[yellow]No recent memories[/yellow]")

    except Exception as e:
        rprint(f"[red]Error getting recent:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def init():
    """Initialize context with current time and recent memories."""
    client = get_client()

    try:
        result = client.init()

        # Init returns formatted text in 'result' key from MCP
        output = result.get("result", "")
        if output:
            rprint(output)
        else:
            # Fallback: show raw response
            rprint(result)

    except Exception as e:
        rprint(f"[red]Error initializing:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def health():
    """Check Pond system health."""
    client = get_client()

    try:
        result = client.health()

        status = result.get("status", "unknown")
        db = result.get("database", "unknown")
        emb = result.get("embeddings", "unknown")
        version = result.get("version", "?")

        if status == "healthy":
            rprint(f"[green]✓ Pond is healthy[/green] (v{version})")
            rprint(f"  Database: {db}")
            rprint(f"  Embeddings: {emb}")
        else:
            rprint(f"[yellow]⚠ Pond status: {status}[/yellow]")

    except Exception as e:
        rprint(f"[red]Error checking health:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
