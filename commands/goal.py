"""VaultPlan goal tracking module (cleaned for v1.0‑rc3)
-----------------------------------------------------------------
Core responsibilities:
• set-goal        — define a savings goal with target, deadline, priority, and note
• update-goal     — increment savings toward a goal from account funds
• list-goals      — display current or filtered goals
• complete-goal   — mark a goal as completed
• delete-goal     — remove a goal
• goal-history    — view finished goals

All DB access uses get_db() from utils.helpers.
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

@app.command("set-goal")
def set_goal(
    name: str = typer.Argument(..., help="Name of the goal"),
    target_amount: float = typer.Argument(..., help="Target amount to save"),
    deadline: str = typer.Option(None, help="Deadline (YYYY-MM-DD), optional"),
    account: str = typer.Option("Goals", help="Account name for savings transfer"),
    priority: int = typer.Option(3, min=1, max=5, help="Goal priority (1-5)"),
    note: str = typer.Option("", help="Optional description or note")
):
    """Define a new goal with optional deadline, priority, and note."""
    try:
        if deadline:
            datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        console.print("[red]❌ Invalid deadline format. Use YYYY-MM-DD.[/red]")
        raise typer.Exit(code=1)

    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                target_amount REAL,
                saved_amount REAL DEFAULT 0.0,
                deadline TEXT,
                account TEXT,
                priority INTEGER DEFAULT 3,
                note TEXT,
                status TEXT DEFAULT 'active'
            )
            """
        )
        c.execute("INSERT INTO goals (name, target_amount, deadline, account, priority, note) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, target_amount, deadline, account, priority, note))
        conn.commit()
        console.print(f"[green]✅ Goal created:[/green] {name} → ${target_amount:.2f}")


@app.command("update-goal")
def update_goal(
    name: str = typer.Argument(..., help="Goal name"),
    amount: float = typer.Option(..., help="Amount to add to goal"),
    account: str = typer.Option(..., help="Account to deduct from")
):
    """Transfer funds from account toward a goal."""
    with get_db() as conn:
        c = conn.cursor()

        c.execute("SELECT saved_amount, target_amount FROM goals WHERE name = ?", (name,))
        row = c.fetchone()
        if not row:
            console.print("[red]❌ Goal not found.[/red]")
            raise typer.Exit()


        saved, target = row
        saved = saved or 0.0
        remaining = target - saved

        if amount <= 0 or amount > remaining:
            console.print("[red]❌ Invalid amount. Must be positive and <= remaining.[/red]")
            raise typer.Exit()

        c.execute("SELECT balance FROM accounts WHERE name = ?", (account,))
        bal_row = c.fetchone()
        if not bal_row:
            console.print(f"[red]❌ Account '{account}' not found.[/red]")
            raise typer.Exit()

        current_balance = bal_row[0]
        if current_balance < amount:
            console.print("[red]❌ Insufficient account balance.[/red]")
            raise typer.Exit()

        c.execute("UPDATE goals SET saved_amount = saved_amount + ? WHERE name = ?", (amount, name))
        c.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, account))
        conn.commit()
        console.print(f"[green]✅ Added ${amount:.2f} to '{name}'[/green]")


@app.command("list-goals")
def list_goals(
    status: str = typer.Option("active", help="Goal status to filter by (active/completed)"),
    account: str = typer.Option(None, help="Optional account filter")
):
    """List goals by status and optional account."""
    with get_db() as conn:
        c = conn.cursor()

        query = "SELECT name, target_amount, saved_amount, deadline, priority, note FROM goals WHERE status = ?"
        params = [status]

        if account:
            query += " AND account = ?"
            params.append(account)

        c.execute(query, tuple(params))
        rows = c.fetchall()

        if not rows:
            console.print("[yellow]No goals found.[/yellow]")
            raise typer.Exit()

        table = Table(title=f"Goals ({status.title()})")
        table.add_column("Name", style="cyan")
        table.add_column("Target", style="magenta", justify="right")
        table.add_column("Saved", style="green", justify="right")
        table.add_column("%", style="yellow", justify="right")
        table.add_column("Deadline", style="blue")
        table.add_column("Priority", justify="center")
        table.add_column("Note", style="dim")

        for name, target, saved, deadline, priority, note in rows:
            saved = saved or 0.0
            pct = f"{(saved / target) * 100:.0f}%" if target else "—"
            table.add_row(
                name,
                f"{currency}{target:.2f}",
                f"{currency}{saved:.2f}",
                pct,
                deadline or "—",
                str(priority),
                note or "—"
            )

        console.print(table)


@app.command("complete-goal")
def complete_goal(name: str):
    """Mark a goal as complete."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE goals SET status = 'completed' WHERE name = ?", (name,))
        conn.commit()
        console.print(f"[green]✅ Goal marked complete:[/green] {name}")


@app.command("delete-goal")
def delete_goal(name: str):
    """Delete a goal permanently."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM goals WHERE name = ?", (name,))
        conn.commit()
        console.print(f"[red]🗑 Goal deleted:[/red] {name}")


@app.command("goal-history")
def goal_history():
    """View all completed goals."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT name, target_amount, saved_amount, deadline, priority, note FROM goals WHERE status = 'completed'")
        rows = c.fetchall()

        if not rows:
            console.print("[yellow]No completed goals.[/yellow]")
            raise typer.Exit()

        table = Table(title="Completed Goals")
        table.add_column("Name", style="cyan")
        table.add_column("Target", style="magenta", justify="right")
        table.add_column("Saved", style="green", justify="right")
        table.add_column("Deadline", style="blue")
        table.add_column("Priority", justify="center")
        table.add_column("Note", style="dim")

        for name, target, saved, deadline, priority, note in rows:
            saved = saved or 0.0
            table.add_row(
                name,
                f"{currency}{target:.2f}",
                f"{currency}{saved:.2f}",
                deadline or "—",
                str(priority),
                note or "—"
            )

        console.print(table)


if __name__ == "__main__":
    app()
