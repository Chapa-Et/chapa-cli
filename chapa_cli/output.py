"""Rich output helpers for Chapa CLI."""

import json as _json
from typing import List, Optional, Union

import click
from rich.console import Console
from rich.json import JSON as RichJSON
from rich.panel import Panel
from rich.table import Table

console = Console()
err_console = Console(stderr=True)

STATUS_COLORS = {
    "success": "green",
    "pending": "yellow",
    "failed": "red",
    "expired": "dim red",
    "cancelled": "dim",
    "processing": "cyan",
}


def _is_json_mode() -> bool:
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        return False
    return ctx.find_root().params.get("json_output", False)


def print_json(data: dict):
    """Print data as formatted JSON (always, or when --json is set)."""
    console.print(RichJSON(_json.dumps(data, indent=2, default=str)))


def print_raw_json(data: dict):
    """Print plain JSON to stdout (for piping)."""
    click.echo(_json.dumps(data, indent=2, default=str))


def print_success(message: str, data: Optional[dict] = None):
    if _is_json_mode():
        out = {"status": "success", "message": message}
        if data:
            out["data"] = data
        print_raw_json(out)
        return
    console.print(f"[bold green]✓[/] {message}")
    if data:
        print_json(data)


def print_error(message: str, details: Union[dict, str, None] = None):
    if _is_json_mode():
        out = {"status": "error", "message": message}
        if details:
            out["details"] = details
        print_raw_json(out)
        return
    err_console.print(f"[bold red]✗[/] {message}")
    if isinstance(details, dict):
        print_json(details)
    elif details:
        err_console.print(f"  {details}")


def print_response(response: dict):
    """Print a full API response, respecting --json mode."""
    if _is_json_mode():
        print_raw_json(response)
        return

    status = response.get("status", "")
    message = response.get("message", "")
    data = response.get("data")

    color = STATUS_COLORS.get(status, "white")
    console.print(f"[bold {color}]{status}[/]: {message}")

    if data is not None:
        print_json(data) if isinstance(data, dict) else print_json({"data": data})


def print_table(columns: List[str], rows: List[List[str]], title: str = ""):
    """Render a Rich table."""
    if _is_json_mode():
        items = [dict(zip(columns, row)) for row in rows]
        print_raw_json(items)
        return

    table = Table(title=title, show_lines=False, pad_edge=True)
    for col in columns:
        table.add_column(col, overflow="fold")
    for row in rows:
        table.add_row(*[str(v) for v in row])
    console.print(table)


def print_list_response(response: dict, columns: List[str], row_keys: List[str],
                        title: str = ""):
    """Print a paginated list response as a table with pagination info."""
    if _is_json_mode():
        print_raw_json(response)
        return

    data = response.get("data", response)
    items = data if isinstance(data, list) else data.get("items", data.get("data", []))
    pagination = response.get("pagination") or (
        data.get("pagination") if isinstance(data, dict) else None
    )

    if not items:
        console.print("[dim]No results found.[/]")
        return

    rows = []
    for item in items:
        row = []
        for key in row_keys:
            val = item
            for part in key.split("."):
                val = val.get(part, "") if isinstance(val, dict) else ""
            row.append(str(val) if val is not None else "")
        rows.append(row)

    print_table(columns, rows, title=title)

    if pagination and pagination.get("has_more"):
        next_cursor = pagination.get("next_cursor", "")
        console.print(
            f"\n[dim]More results available. Use --cursor {next_cursor}[/]"
        )


def print_panel(title: str, content: str):
    console.print(Panel(content, title=title, border_style="blue"))
