import typer
import sqlite3
from utils.db_init import DB_PATH
from rich.console import Console
from rich.table import Table

console = Console()
todo_app = typer.Typer()

@todo_app.command("add")
def add_todo(task: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY, task TEXT, completed INTEGER DEFAULT 0)")
        conn.execute("INSERT INTO todos (task) VALUES (?)", (task,))
    console.print(f"[green]✓ Added:[/] {task}")

@todo_app.command("list")
def list_todos():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, task FROM todos WHERE completed = 0")
        rows = c.fetchall()
        if not rows:
            console.print("[yellow]No active todos[/yellow]")
            return
        table = Table(title="TODOs", show_lines=True)
        table.add_column("ID", justify="right")
        table.add_column("Task", justify="left")
        for row in rows:
            table.add_row(str(row[0]), row[1])
        console.print(table)

@todo_app.command("done")
def complete_todo(todo_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM todos WHERE id = ? AND completed = 0", (todo_id,))
        row = c.fetchone()
        if not row:
            console.print(f"[red]✗ Todo #{todo_id} not found or already completed[/red]")
            return
        c.execute("UPDATE todos SET completed = 1 WHERE id = ?", (todo_id,))
        console.print(f"[cyan]✓ Marked done:[/] #{todo_id}")

@todo_app.command("delete")
def delete_todo(todo_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
        row = c.fetchone()
        if not row:
            console.print(f"[red]✗ Todo #{todo_id} not found[/red]")
            return
        c.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        console.print(f"[magenta]✓ Deleted todo #[/]{todo_id}")
