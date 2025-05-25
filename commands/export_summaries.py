import json
from datetime import datetime, timedelta
from pathlib import Path
import typer
from utils.helpers import get_db

app = typer.Typer()

def fetch_rows(c, sql, params=()):
    c.execute(sql, params)
    return [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]

def compress_goals(goals):
    for g in goals:
        g["progress"] = round(float(g.get("saved_amount", 0)) / float(g.get("target_amount", 1)), 4)
    return goals

def compress_debits(debits):
    for d in debits:
        d["progress"] = round(float(d.get("paid_amount", 0)) / float(d.get("amount", 1)), 4)
    return debits

def calc_balance(accounts):
    return sum(float(a["balance"]) for a in accounts)

def summarize_growth(income, expenses):
    total_in = sum(float(i["amount"]) for i in income)
    total_out = sum(float(e["amount"]) for e in expenses)
    net = total_in - total_out
    return {"total_income": total_in, "total_expense": total_out, "net_growth": net}

@app.command("export-summary")
def export_summary(
    mode: str = typer.Option("weekly", help="Choose: full, weekly, last"),
    output_dir: str = typer.Option("reports", help="Directory for output")
):
    conn = get_db()
    c = conn.cursor()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    output_path = Path.home() / "vaultplan" / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Cutoff logic
    if mode == "weekly":
        date_cutoff = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    elif mode == "last":
        files = sorted(output_path.glob("export_*.json"), reverse=True)
        last_date = None
        if files:
            with open(files[0]) as f:
                last_export = json.load(f)
                last_date = last_export.get("timestamp", today)
        date_cutoff = last_date or (now - timedelta(days=1)).strftime("%Y-%m-%d")
    elif mode == "full":
        date_cutoff = "2000-01-01"
    else:
        typer.echo("[red]Invalid mode[/red]")
        raise typer.Exit(1)

    # Fetch tables
    accounts = fetch_rows(c, "SELECT * FROM accounts")
    income = fetch_rows(c, "SELECT * FROM income WHERE date >= ?", (date_cutoff,))
    expenses = fetch_rows(c, "SELECT * FROM expenses WHERE date >= ?", (date_cutoff,))
    transfers = fetch_rows(c, "SELECT * FROM expenses WHERE (description LIKE '%transfer%' OR category LIKE '%transfer%') AND date >= ?", (date_cutoff,))
    notes = fetch_rows(c, "SELECT * FROM notes WHERE created_at >= ?", (date_cutoff,))
    goals = fetch_rows(c, "SELECT * FROM goals")
    debits = fetch_rows(c, "SELECT * FROM debits")
    
    # Always include full goals/debits for AI continuity
    goals = compress_goals(goals)
    debits = compress_debits(debits)

    # Balance calculations
    current_balance = calc_balance(accounts)

    # Net growth since start (for full, otherwise from cutoff)
    all_income = fetch_rows(c, "SELECT * FROM income")
    all_expenses = fetch_rows(c, "SELECT * FROM expenses")
    growth = summarize_growth(all_income, all_expenses)

    export = {
        "timestamp": now.isoformat(),
        "mode": mode,
        "since": date_cutoff,
        "accounts": [{k: a[k] for k in ("name", "type", "balance")} for a in accounts],
        "current_balance": current_balance,
        "growth": growth,
        "goals": goals,
        "debits": debits,
        "recent": {
            "income": income,
            "expenses": expenses,
            "transfers": transfers,
            "notes": notes
        }
    }

    filename = output_path / f"export_{mode}_{now.strftime('%Y-%m-%dT%H-%M-%S')}.json"
    with open(filename, "w") as f:
        json.dump(export, f, indent=2)

    typer.echo(f"[green]Export complete:[/green] {filename}")

if __name__ == "__main__":
    app()
