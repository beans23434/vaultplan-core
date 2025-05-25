from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from utils.helpers import get_db

app = typer.Typer()
console = Console()

def _open_conn() -> sqlite3.Connection:
    return get_db()  # get_db already returns a connection

def _fetch_accounts(c: sqlite3.Cursor, accounts: str | None):
    if accounts:
        c.execute(
            "SELECT name, type, balance, wallet FROM accounts WHERE name = ?",
            (accounts,),
        )
    else:
        c.execute("SELECT name, type, balance, wallet FROM accounts")
    return c.fetchall()

def _print_balance_table(rows):
    table = Table(title="Account Balances")
    table.add_column("Account", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Balance", style="green", justify="right")
    table.add_column("Wallet", style="yellow")
    for name, type_, balance, wallet in rows:
        table.add_row(name, type_, f"${balance:,.2f}", wallet or "—")
    console.print(table)

def _fetch_activity(c: sqlite3.Cursor, accounts: str | None, since: str):
    if accounts:
        c.execute(
            """
            SELECT date, amount * -1, 'Expense', printf('%s: %s', category, description), account
            FROM expenses WHERE account = ? AND date >= ?
            UNION ALL
            SELECT date, amount, 'Income', source, account
            FROM income WHERE account = ? AND date >= ?
            ORDER BY date DESC
            """,
            (accounts, since, accounts, since),
        )
    else:
        c.execute(
            """
            SELECT date, amount * -1, 'Expense', printf('%s: %s', category, description), account
            FROM expenses WHERE date >= ?
            UNION ALL
            SELECT date, amount, 'Income', source, account
            FROM income WHERE date >= ?
            ORDER BY date DESC
            """,
            (since, since),
        )
    return c.fetchall()

def _print_activity_table(rows, days):
    table = Table(title=f"Recent Activity (Last {days} days)")
    table.add_column("Date", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Description", style="yellow")
    table.add_column("Account", style="blue")
    for date, amount, typ, desc, acc in rows:
        sign = "-" if amount < 0 else "+"
        table.add_row(date, typ, f"{sign}${abs(amount):,.2f}", desc, acc)
    console.print(table)

@app.command("balance")
def show_balance(
    accounts: str | None = typer.Option(None, help="Specific account to show (default: all)"),
    days: int = typer.Option(7, min=1, help="Look‑back window for recent activity"),
):
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    with _open_conn() as conn:
        c = conn.cursor()
        result = _fetch_accounts(c, accounts)
        if not result:
            console.print(f"[red]No account found named '{accounts}'.[/red]" if accounts else "[red]No accounts defined yet.[/red]")
            raise typer.Exit(code=1)
        _print_balance_table(result)

        activity = _fetch_activity(c, accounts, since_date)
        if activity:
            _print_activity_table(activity, days)
        else:
            console.print(f"[yellow]No transactions in the last {days} days.[/yellow]")

if __name__ == "__main__":
    app()
