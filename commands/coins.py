# commands/coin_mode.py
import typer
from rich.console import Console
from pathlib import Path
import json

app = typer.Typer()
console = Console()

def coin_mode(pocket_total: float, notes: float):
    coins = pocket_total - notes
    if coins >= 50:
        return {
            "action": "DEPOSIT_NOTES",
            "amount_to_bank": notes,
            "message": f"Coin mode triggered: Deposit ${notes:.2f} in notes. Survive on ${coins:.2f} in coins."
        }
    else:
        return {
            "action": "HOLD",
            "message": f"Coins ${coins:.2f} not yet at $50 threshold. No deposit triggered."
        }

@app.command("check")
def run_coin_mode(notes: float = typer.Argument(..., help="How much in paper notes you have"),
                  pocket: float = typer.Option(None, help="Override current Pocket balance")):
    """Run the BUNB Coin Mode protocol."""
    from utils.helpers import get_db

    if pocket is None:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT balance FROM accounts WHERE name = 'Pocket'")
        row = c.fetchone()
        if not row:
            console.print("[red]Error:[/] No Pocket account found.")
            raise typer.Exit(1)
        pocket = row[0]

    result = coin_mode(pocket_total=pocket, notes=notes)
    console.print(f"\n[bold]🧠 Coin Mode Result[/bold]")
    console.print(f"🎯 Action: [cyan]{result['action']}[/cyan]")
    console.print(f"💬 Message: {result['message']}")
