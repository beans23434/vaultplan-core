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

# Local imports
from commands.account import create_account, transfer_funds
from commands.income import add_income
from commands.expense import add_expense
from commands.goal import set_goal, list_goals, update_goal, delete_goal, complete_goal, goal_history
from commands.debit import add_debit, pay_debit, list_debits
from commands.balance import show_balance
from commands.summary import show_summary, summary_export
from commands.note import add_note, list_notes
from utils.db_init import init_tables, DB_PATH
from utils.config import load_config
from Web3.web3_sync import web3_sync  # adjust path as needed
from commands.summary_web3 import summary_web3
from commands.export_summaries import export_summary
from commands.wizard import wizard
from ai import app as ai_app
from signals.Reddit import app as reddit_app

app = typer.Typer(help="VaultPlan - Your personal finance command center")
console = Console()

# Initialize database tables
init_tables()

# --- Reddit Daemon Management ---

def ensure_reddit_daemon(poll_interval: int = 60):
    """
    Ensure the reddit_daemon.py process is running when reddit_enabled is True.
    """
    cfg = load_config()
    if cfg.get("reddit_enabled", False):
        try:
            # Check if daemon is already running
            subprocess.check_output(["pgrep", "-f", "reddit_daemon.py"]);
        except subprocess.CalledProcessError:
            # Not running → start in background
            daemon_script = Path(__file__).parent / "reddit_daemon.py"
            subprocess.Popen(
                [sys.executable, str(daemon_script), "--poll-interval", str(poll_interval)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setpgrp,
            )

@app.callback(invoke_without_command=True)
def on_startup(ctx: typer.Context):
    # Always ensure our Reddit daemon is alive (if enabled)
    ensure_reddit_daemon()
    # If no subcommand was provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

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
app.command("wizard")(wizard)
app.add_typer(ai_app, name="AI")
app.add_typer(reddit_app, name="reddit")  # Reddit subcommands

@app.command("doctor")
def doctor():
    console.print(Panel(f"Connected to database: [bold green]{DB_PATH}[/bold green]"))
    expected_schema = {
        "notes": {"mood": "INTEGER", "note": "TEXT", "account": "TEXT", "tags": "TEXT", "created_at": "TEXT"},
        "income": {"amount": "REAL", "source": "TEXT", "account": "TEXT", "date": "TEXT"},
        "expenses": {"amount": "REAL", "category": "TEXT", "description": "TEXT", "account": "TEXT", "metadata": "TEXT", "note": "TEXT", "date": "TEXT"},
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
