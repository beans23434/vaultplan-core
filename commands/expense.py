import typer
from pathlib import Path
import sqlite3
from datetime import datetime
from utils.helpers import ensure_data_dir
import json

app = typer.Typer()

def get_db():
    ensure_data_dir()
    db_path = Path(__file__).parent.parent / "data" / "vaultplan.db"
    conn = sqlite3.connect(db_path)
    return conn

@app.command()
def add_expense(
    amount: str = typer.Argument(..., help="Expense amount (supports $4.97 format)"),
    category: str = typer.Option("general", help="Expense category"),
    description: str = typer.Option("", help="Description"),
    account: str = typer.Option(..., help="Account name"),
    metadata: str = typer.Option("[]", help="JSON array of items [item1, item2, ...]"),
    note: str = typer.Option("", help="Additional note about the expense"),
    date: str = typer.Option(datetime.now().strftime("%Y-%m-%d"), help="Date (YYYY-MM-DD)")
):
    """Log an expense and update account balance."""
    # Clean amount (remove $ and convert to float)
    clean_amount = float(amount.replace('$', '').replace(',', ''))
    
    # Parse metadata
    try:
        items = json.loads(metadata)
    except json.JSONDecodeError:
        items = []
    
    conn = get_db()
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            account TEXT,
            date TEXT,
            note TEXT,
            metadata TEXT
        )
    """)
    
    # Insert expense
    c.execute(
        """INSERT INTO expenses 
           (amount, category, description, account, date, note, metadata) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (clean_amount, category, description, account, date, note, json.dumps(items))
    )
    
    # Update account balance
    c.execute(
        "UPDATE accounts SET balance = balance - ? WHERE name = ?",
        (clean_amount, account)
    )
    
    conn.commit()
    conn.close()
    
    # Format output
    items_str = f" ({', '.join(items)})" if items else ""
    note_str = f"\n📝 Note: {note}" if note else ""
    
    typer.echo(f"🧾 Expense of ${clean_amount:.2f} logged to '{account}' ({category}: {description}){items_str}.{note_str}")
    typer.echo("�� Balance updated.") 