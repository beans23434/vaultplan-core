"""VaultPlan debit tracking module (cleaned for v1.0‑rc1)
-----------------------------------------------------------------
Core responsibilities:
• add-debit   — log a new recurring or one-off debit
• pay-debit   — record a payment toward a debit
• list-debits — view outstanding or all debits

All DB access uses get_db() from utils.helpers for consistency.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
import typer
from rich.console import Console
from rich.table import Table

from utils.helpers import get_db

from utils.config import get_display_currency  # if not already
currency = get_display_currency()

app = typer.Typer()
console = Console()

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@app.command("add-debit")
def add_debit(
    label: str = typer.Argument(..., help="Name or label of the debit"),
    amount_due: float = typer.Argument(..., help="Amount due"),
    due_date: str = typer.Option(None, help="Due date (YYYY-MM-DD)"),
    account: str = typer.Option("Pocket", help="Account to pay from"),
):
    """Add a new debit (bill, recurring charge, etc.)"""
    try:
        if due_date:
            datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
        raise typer.Exit(code=1)

    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS debits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                amount_due REAL,
                amount_paid REAL DEFAULT 0.0,
                due_date TEXT,
                account TEXT,
                status TEXT DEFAULT 'open'
            )
            """
        )
        c.execute(
            "INSERT INTO debits (label, amount_due, amount_paid, due_date, account) VALUES (?, ?, ?, ?, ?)",
            (label, amount_due, 0.0, due_date, account)
        )
        conn.commit()
        console.print(f"[green]✅ Debit added:[/green] {label} for ${amount_due:.2f}")


@app.command("pay-debit")
def pay_debit(
    debit_id: int = typer.Argument(..., help="ID of the debit to pay"),
    account: str = typer.Argument(..., help="Account to deduct from"),
    amount: float = typer.Option(None, help="Amount to pay (optional, defaults to full remaining)")
):
    """Make a payment toward a debit."""
    with get_db() as conn:
        c = conn.cursor()

        c.execute("SELECT 1 FROM accounts WHERE name = ?", (account,))
        if not c.fetchone():
            console.print(f"[red]❌ Account '{account}' does not exist.[/red]")
            raise typer.Exit(code=1)

        c.execute("SELECT id, label, amount_due, amount_paid FROM debits WHERE id = ?", (debit_id,))
        row = c.fetchone()

        if not row:
            console.print("[red]❌ Debit not found.[/red]")
            raise typer.Exit(code=1)

        id_, label, due, paid = row
        paid = paid or 0.0
        remaining = due - paid

        if amount is None:
            amount = remaining

        if amount <= 0 or amount > remaining:
            console.print("[red]❌ Invalid payment amount.[/red]")
            raise typer.Exit(code=1)

        c.execute("UPDATE debits SET amount_paid = amount_paid + ? WHERE id = ?", (amount, id_))
        if amount == remaining:
            c.execute("UPDATE debits SET status = 'paid' WHERE id = ?", (id_,))

        c.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, account))
        conn.commit()
        console.print(f"[green]✅ Paid ${amount:.2f} toward '{label}'. Remaining: ${remaining - amount:.2f}")


@app.command("list-debits")
def list_debits(
    show_all: bool = typer.Option(False, "--all", help="Show all debits, not just open ones")
):
    """List all or only outstanding debits."""
    with get_db() as conn:
        c = conn.cursor()
        if show_all:
            c.execute("SELECT id, label, amount_due, amount_paid, due_date, account, status FROM debits ORDER BY due_date")
        else:
            c.execute("SELECT id, label, amount_due, amount_paid, due_date, account, status FROM debits WHERE status = 'open' ORDER BY due_date")

        rows = c.fetchall()
        if not rows:
            console.print("[yellow]No debits found.[/yellow]")
            raise typer.Exit()

        table = Table(title="Debits")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Label", style="magenta")
        table.add_column("Due", style="green", justify="right")
        table.add_column("Paid", style="yellow", justify="right")
        table.add_column("Date", style="blue")
        table.add_column("Account", style="white")
        table.add_column("Status", style="bold")

        for id_, label, due, paid, date, acct, status in rows:
            paid = paid or 0.0
            table.add_row(
                str(id_),
                label,
                f"{currency}{due:.2f}",
                f"{currency}{paid:.2f}",
                date or "—",
                acct or "—",
                status
            )

        console.print(table)


if __name__ == "__main__":
    app()
