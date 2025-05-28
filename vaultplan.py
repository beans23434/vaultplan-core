import typer
import sqlite3
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils.config import get_display_currency, load_config
from utils.db_init import init_tables, DB_PATH
from commands.account import create_account, transfer_funds
from commands.income import add_income
from commands.expense import add_expense
from commands.goal import set_goal, list_goals, update_goal, delete_goal, complete_goal, goal_history
from commands.debit import add_debit, pay_debit, list_debits
from commands.balance import show_balance
from commands.summary import show_summary, summary_export
from commands.note import add_note, list_notes
from commands.summary_web3 import summary_web3
from commands.export_summaries import export_summary
from Web3.web3_sync import web3_sync
from commands import todo

currency = get_display_currency()

app = typer.Typer(help="VaultPlan - Your personal finance command center")
console = Console()

DB_PATH = Path.home() / ".vaultplan" / "data" / "vaultplan.db"
# Initialize database tables
init_tables()


# Register commands
app.command("create-account")(create_account)
app.command("add-income")(add_income)
app.command("transfer")(transfer_funds)
app.command("add-expense")(add_expense)
app.command("set-goal")(set_goal)
app.command("list-goals")(list_goals)
app.command("update-goal")(update_goal)
app.command("delete-goal")(delete_goal)
app.command("complete-goal")(complete_goal)
app.command("goal-history")(goal_history)
app.command("add-debit")(add_debit)
app.command("pay-debit")(pay_debit)
app.command("list-debits")(list_debits)
app.command("balance")(show_balance)
app.command("summary")(show_summary)
app.command("summary-export")(summary_export)
app.command("add-note")(add_note)
app.command("list-notes")(list_notes)
app.command("web3-sync")(web3_sync)
app.command("summary-web3")(summary_web3)
app.command("export-summary")(export_summary)
app.add_typer(todo.todo_app, name="todo")

@app.command("doctor")
def doctor():
    console.print(Panel(f"Connected to database: [bold green]{DB_PATH}[/bold green]"))

    # --- One-time upgrade: rename value_aud to value_fiat ---
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("PRAGMA table_info(web3_transactions)")
            col_names = {row[1] for row in c.fetchall()}
            if "value_aud" in col_names and "value_fiat" not in col_names:
                c.execute("ALTER TABLE web3_transactions RENAME COLUMN value_aud TO value_fiat")
                console.print("[yellow]⏎ Renamed:[/] web3_transactions.value_aud → value_fiat")
    except Exception as e:
        console.print(f"[red]⚠ Column rename failed:[/] {e}")

    expected_schema = {
        "accounts": {"name": "TEXT", "type": "TEXT", "balance": "REAL", "wallet": "TEXT"},
        "income": {"amount": "REAL", "source": "TEXT", "account": "TEXT", "date": "TEXT"},
        "expenses": {"amount": "REAL", "category": "TEXT", "description": "TEXT", "account": "TEXT", "note": "TEXT", "metadata": "TEXT", "date": "TEXT"},
        "notes": {"mood": "INTEGER", "note": "TEXT", "account": "TEXT", "tags": "TEXT", "created_at": "TEXT"},
        "goals": {"name": "TEXT", "target_amount": "REAL", "saved_amount": "REAL", "deadline": "TEXT", "account": "TEXT", "priority": "INTEGER", "note": "TEXT", "status": "TEXT"},
        "debits": {"label": "TEXT", "amount_due": "REAL", "amount_paid": "REAL", "due_date": "TEXT", "account": "TEXT", "status": "TEXT"},
        "web3_transactions": {"tx_type": "TEXT", "symbol": "TEXT", "amount_token": "REAL", "value_fiat": "REAL", "date": "TEXT"}
    }
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        console.print("Tables found:", tables)
        for table, expected_cols in expected_schema.items():
            if table in tables:
                c.execute(f"PRAGMA table_info({table})")
                existing_cols = {row[1] for row in c.fetchall()}
                for col, col_type in expected_cols.items():
                    if col not in existing_cols:
                        console.print(f"[yellow]Missing column in {table}:[/] {col} — Adding...")
                        try:
                            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                        except Exception as e:
                            console.print(f"[red]Failed to add {col} to {table}:[/] {e}")
            else:
                console.print(f"[red]Table not found:[/] {table}")

if __name__ == "__main__":
    app()
