"""VaultPlan note tracking module (cleaned for v1.0‑rc1)
-----------------------------------------------------------------
Core responsibilities:
• add-note    — log mood, emotional tone, and optional tags/account
• list-notes  — filter notes by account and date range

Uses consistent DB connection from utils.helpers.get_db().
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.panel import Panel

from utils.helpers import get_db

app = typer.Typer()
console = Console()

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@app.command("add-note")
def add_note(
    mood: int = typer.Argument(..., help="Mood rating (1-10)"),
    note: str = typer.Argument(..., help="Note content"),
    account: str = typer.Option(None, help="Related account (optional)"),
    tags: str = typer.Option("[]", help="JSON array of tags [tag1, tag2, ...]")
):
    """Log a mood/mental state note with optional metadata."""
    if not 1 <= mood <= 10:
        console.print("[red]❌ Mood rating must be between 1 and 10.[/red]")
        raise typer.Exit()

    with get_db() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mood INTEGER,
                note TEXT,
                account TEXT,
                tags TEXT,
                created_at TEXT
            )
        """)

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
            INSERT INTO notes (mood, note, account, tags, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (mood, note, account, tags, created_at))

        conn.commit()

    account_str = f" (Account: {account})" if account else ""
    typer.echo(f"📝 Note logged{account_str}")
    typer.echo(f"Mood: {'😊' * mood} ({mood}/10)")


@app.command("list-notes")
def list_notes(
    account: str = typer.Option(None, help="Filter by account"),
    days: int = typer.Option(7, help="Show notes from last N days")
):
    """List recent notes filtered by date or account."""
    with get_db() as conn:
        c = conn.cursor()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        since = start_date.strftime("%Y-%m-%d")

        if account:
            c.execute("""
                SELECT mood, note, account, tags, created_at
                FROM notes
                WHERE account = ? AND created_at >= ?
                ORDER BY created_at DESC
            """, (account, since))
        else:
            c.execute("""
                SELECT mood, note, account, tags, created_at
                FROM notes
                WHERE created_at >= ?
                ORDER BY created_at DESC
            """, (since,))

        rows = c.fetchall()

        if not rows:
            console.print("[yellow]No notes found.[/yellow]")
            raise typer.Exit()

        for mood, content, acct, tags, created_at in rows:
            panel = f'''
[bold]Mood:[/bold] {'😊' * mood} ({mood}/10)
[bold]Time:[/bold] {created_at}
[bold]Account:[/bold] {acct or '—'}
[bold]Tags:[/bold] {tags}

{content}
'''
            console.print(Panel(panel.strip(), border_style="cyan"))


if __name__ == "__main__":
    app()
