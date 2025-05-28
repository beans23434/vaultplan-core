from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from utils.helpers import get_db

from utils.config import get_display_currency
currency = get_display_currency()

app = typer.Typer()
console = Console()

@app.command("summary")
def show_summary(days: int = typer.Option(30, help="Days to look back for recent activity")):
    """Display full summary of balances, Web3 stats, and recent activity."""
    with get_db() as conn:
        c = conn.cursor()

        # Account balances summary
        acct_table = Table(title="VaultPlan Account Summary")
        acct_table.add_column("Name", style="cyan")
        acct_table.add_column("Type", style="magenta")
        acct_table.add_column("Balance", style="green", justify="right")

        try:
            c.execute("SELECT name, type, balance FROM accounts")
            for name, typ, bal in c.fetchall():
                acct_table.add_row(name, typ, f"{currency}{bal:,.2f}")
            console.print(acct_table)
        except sqlite3.OperationalError:
            console.print("[red]⚠ No accounts table found.[/red]")

        # Income vs Expense summary
        try:
            c.execute("SELECT amount, source FROM income")
            income_rows = c.fetchall()
            total_income = sum(a for a, s in income_rows if not s.lower().startswith("transfer"))
            c.execute("SELECT SUM(amount) FROM expenses WHERE category != ?", ("__transfer__",))
            total_expenses = c.fetchone()[0] or 0.0

            net = total_income - total_expenses
            summary_table = Table(title="Income vs Expenses (Excludes Transfers)")
            summary_table.add_column("Type")
            summary_table.add_column("Amount", justify="right")
            summary_table.add_row("Income", f"{currency}{total_income:,.2f}")
            summary_table.add_row("Expenses", f"{currency}{total_expenses:,.2f}")
            summary_table.add_row("Net", f"{currency}{net:,.2f}")
            console.print(summary_table)
        except sqlite3.OperationalError:
            console.print("[yellow]Could not calculate totals.[/yellow]")

        # Web3 transaction totals
        try:
            c.execute("SELECT tx_type, COUNT(*), SUM(amount_aud) FROM web3_transactions GROUP BY tx_type")
            rows = c.fetchall()
            if rows:
                tx_table = Table(title="Web3 Transaction Totals")
                tx_table.add_column("Type", style="cyan")
                tx_table.add_column("Count", justify="right")
                tx_table.add_column("AUD Total", style="green", justify="right")

                for tx_type, count, total in rows:
                    tx_table.add_row(tx_type, str(count), f"{currency}{total:,.2f}")

                console.print(tx_table)
        except sqlite3.OperationalError:
            console.print("[yellow]No web3 transaction data found.[/yellow]")

        # Activity summary
        try:
            since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            c.execute("""
                SELECT date, amount * -1, 'Expense', category || ': ' || description, account FROM expenses WHERE date >= ? AND category != '__transfer__'
                UNION ALL
                SELECT date, amount, 'Income', source, account FROM income WHERE date >= ?
                ORDER BY date DESC
            """, (since, since))

            rows = c.fetchall()
            if rows:
                activity_table = Table(title=f"Recent Activity (Last {days} days)")
                activity_table.add_column("Date", style="cyan")
                activity_table.add_column("Type", style="magenta")
                activity_table.add_column("Amount", style="green", justify="right")
                activity_table.add_column("Description", style="yellow")
                activity_table.add_column("Account", style="blue")

                for date, amount, typ, desc, acc in rows:
                    sign = "+" if amount >= 0 else "-"
                    activity_table.add_row(date, typ, f"{sign}{currency}{abs(amount):,.2f}", desc, acc)

                console.print(activity_table)
            else:
                console.print(f"[yellow]No transactions found in last {days} days.[/yellow]")
        except sqlite3.OperationalError:
            console.print("[red]Activity summary failed.[/red]")

        # Transfers summary
        try:
            c.execute("""
                SELECT date, amount, account, description
                FROM expenses
                WHERE category = ?
                ORDER BY date DESC
            """, ("__transfer__",))
            rows = c.fetchall()
            if rows:
                transfer_table = Table(title="Recent Transfers")
                transfer_table.add_column("Date", style="cyan")
                transfer_table.add_column("From", style="red")
                transfer_table.add_column("To", style="green")
                transfer_table.add_column("Amount", justify="right")

                for date, amt, from_acct, desc in rows:
                    to_acct = desc.replace("Transfer to ", "")
                    transfer_table.add_row(date, from_acct, to_acct, f"{currency}{amt:,.2f}")
                console.print(transfer_table)
        except sqlite3.OperationalError:
            console.print("[yellow]Could not load transfers.[/yellow]")

@app.command("summary-export")
def summary_export(
    days: int = typer.Option(30, help="Days to include in summary"),
    output_dir: str = typer.Option("reports", help="Directory to export summary JSON")
):
    """Export summarized data to a JSON file in the specified directory."""
    output = {
        "total_income": 0.0,
        "total_expenses": 0.0,
        "web3": [],
        "recent_activity": [],
        "transfers": []
    }

    with get_db() as conn:
        c = conn.cursor()

        try:
            c.execute("SELECT amount, source FROM income")
            output["total_income"] = sum(a for a, s in c.fetchall() if not s.lower().startswith("transfer"))
            c.execute("SELECT SUM(amount) FROM expenses WHERE category != ?", ("__transfer__",))
            total_expenses = c.fetchone()[0] or 0.0
            output["total_expenses"] = total_expenses
        except:
            pass

        try:
            c.execute("SELECT tx_type, COUNT(*), SUM(amount_aud) FROM web3_transactions GROUP BY tx_type")
            output["web3"] = [{"type": r[0], "count": r[1], "total_aud": r[2] or 0.0} for r in c.fetchall()]
        except:
            pass

        try:
            since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            c.execute("""
                SELECT date, amount * -1, 'Expense', category || ': ' || description, account FROM expenses WHERE date >= ? AND category != '__transfer__'
                UNION ALL
                SELECT date, amount, 'Income', source, account FROM income WHERE date >= ?
                ORDER BY date DESC
            """, (since, since))
            output["recent_activity"] = [
                {"date": r[0], "amount": float(r[1]), "type": r[2], "desc": r[3], "account": r[4]}
                for r in c.fetchall()
            ]
        except:
            pass

        try:
            c.execute("""
                SELECT date, amount, account, description
                FROM expenses
                WHERE category = ?
                ORDER BY date DESC
            """, ("__transfer__",))
            output["transfers"] = [
                {
                    "date": r[0],
                    "amount": float(r[1]),
                    "from": r[2],
                    "to": r[3].replace("Transfer to ", "")
                }
                for r in c.fetchall()
            ]
        except:
            output["transfers"] = []

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_path = Path.home() / "vaultplan" / "reports" / f"summary_{timestamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    console.print(f"[green]✅ Summary exported to:[/green] {out_path}")

if __name__ == "__main__":
    app()
