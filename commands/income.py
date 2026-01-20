import typer
from datetime import datetime

from utils.helpers import get_db

app = typer.Typer()

@app.command()
def add_income(
    amount: float = typer.Argument(..., help="Income amount"),
    source: str = typer.Option("", help="Income source"),
    account: str = typer.Option(..., help="Account name"),
    date: str = typer.Option(datetime.now().strftime("%Y-%m-%d"), help="Date (YYYY-MM-DD)")
):
    """Log new income (amount, source, date) and update account balance."""
    with get_db() as conn:
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
    typer.echo(f"💰 Logged {amount} income to '{account}' from '{source}'. Balance updated. Streak begun.")
