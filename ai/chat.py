import openai
import os
import sqlite3
import typer
import json
import sys
from pathlib import Path
from rich.console import Console
import time
import subprocess
from datetime import datetime

console = Console()
app = typer.Typer(help="VaultAI CLI for financial reflection and querying")

# Paths and config
CONFIG_PATH = Path.home() / "vaultplan" / "config.json"
if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
else:
    config = {}

DB_PATH = os.path.expanduser("~/vaultplan/data/vaultplan.db")
openai.api_key = config.get("openai_api_key", os.getenv("OPENAI_API_KEY"))

# System prompt and conversation history
SYSTEM_PROMPT = """
You are VaultAI, a CLI financial assistant with access to a SQLite database for a user.
The database contains the following tables and fields:

accounts(id, name, type, balance, wallet)
income(id, account, amount, source, date)
expenses(id, account, amount, category, description, date, note, metadata)
notes(id, mood, text, tags, date, note, account, created_at)
goals(id, name, target_amount, saved_amount, deadline, account, priority, note, status)
debits(id, label, amount_due, account, due_date, created_at, paid, status, note)

You may instruct the Python script to run a specific SQL query with [QUERY] tags.
Respond with questions, explanations, or query instructions like:
[QUERY] SELECT AVG(mood) FROM notes WHERE created_at >= DATE('now', '-7 day');

Keep queries secure, scoped, and explainable.
"""

conversation = [{"role": "system", "content": SYSTEM_PROMPT}]


def generate_full_summary():
    """Trigger a full summary export via the VaultPlan CLI."""
    subprocess.run([
        sys.executable if hasattr(sys, 'executable') else 'python',
        "vaultplan.py", "export-summary", "--mode", "full"
    ], check=False)
    time.sleep(0.5)


def load_latest_summary():
    """Load the most recent full summary JSON from reports."""
    reports_dir = Path.home() / "vaultplan" / "reports"
    if not reports_dir.exists():
        return None
    json_files = sorted(reports_dir.glob("export_full_*.json"), reverse=True)
    if not json_files:
        return None
    try:
        with open(json_files[0]) as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading summary:[/] {e}")
        return None


def load_latest_reddit():
    """Load today's Reddit daily JSON if available."""
    reddit_dir = Path.home() / "vaultplan" / "signals" / "reddit"
    today = datetime.utcnow().strftime("%Y-%m-%d")
    file = reddit_dir / f"reddit_daily_{today}.json"
    if file.exists():
        try:
            with open(file) as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[yellow]Error loading Reddit data:[/] {e}")
    return None

@app.command("full-summary")
def full_summary_command():
    """Generate and print the latest full summary report."""
    generate_full_summary()
    data = load_latest_summary()
    if data:
        typer.echo(json.dumps(data, indent=2))
    else:
        typer.echo("No summary data found.")

@app.command("chat")
def chat():
    """Start an interactive VaultAI reflection chat session, seeded with latest financial and Reddit data."""
    console.print("[bold cyan]VaultAI Reflect Chat Active[/bold cyan]")

    # Seed with latest financial summary
    generate_full_summary()
    summary = load_latest_summary()
    if summary:
        conversation.append({
            "role": "user",
            "content": "Here is the latest financial summary:\n" + json.dumps(summary)
        })

    # Seed with today's Reddit posts
    reddit_posts = load_latest_reddit()
    if reddit_posts is not None:
        conversation.append({
            "role": "user",
            "content": "Here are today's Reddit posts:\n" + json.dumps(reddit_posts)
        })

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            console.print("[bold yellow]Session ended.[/bold yellow]")
            break

        conversation.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.4,
            max_tokens=500
        )

        reply = response.choices[0].message.content
        conversation.append({"role": "assistant", "content": reply})

        if "[QUERY]" in reply:
            sql = reply.split("[QUERY]")[-1].strip()
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute(sql)
                rows = c.fetchall()
                conn.close()
            except Exception as db_err:
                rows = f"[DB ERROR] {db_err}"
            console.print(f"[bold green]VaultAI:[/] {reply}")
            console.print(f"[bold magenta]Query Result:[/] {rows}")
            conversation.append({"role": "user", "content": f"Query result: {rows}"})
        else:
            console.print(f"[bold green]VaultAI:[/] {reply}")

if __name__ == "__main__":
    app()
