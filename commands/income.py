import typer
from pathlib import Path
import sqlite3
from datetime import datetime
from utils.helpers import ensure_data_dir

app = typer.Typer()

def get_db():
    ensure_data_dir()
    db_path = Path(__file__).parent.parent / "data" / "vaultplan.db"
    conn = sqlite3.connect(db_path)
    return conn

@app.command()
def add_income(
    amount: float = typer.Argument(..., help="Income amount"),
    source: str = typer.Option("", help="Income source"),
    account: str = typer.Option(..., help="Account name"),
    date: str = typer.Option(datetime.now().strftime("%Y-%m-%d"), help="Date (YYYY-MM-DD)")
):
    """Log new income (amount, source, date) and update account balance."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            source TEXT,
            account TEXT,
            date TEXT
        )
    """)
    c.execute(
        "INSERT INTO income (amount, source, account, date) VALUES (?, ?, ?, ?)",
        (amount, source, account, date)
    )
    c.execute(
        "UPDATE accounts SET balance = balance + ? WHERE name = ?",
        (amount, account)
    )
    conn.commit()
    conn.close()
    typer.echo(f"💰 Logged {amount} income to '{account}' from '{source}'. Balance updated. Streak begun.") 