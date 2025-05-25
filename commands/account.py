"""VaultPlan account management module (cleaned for v1.0‑rc1)
-----------------------------------------------------------------
Core responsibilities
• create‑account — add a new bank/crypto account
• set‑balance    — manually correct a balance (rare)
• transfer       — move funds between accounts (atomic)

The module exposes a Typer sub‑app that gets mounted from vaultplan.py.
All DB access goes through utils.path_helpers.get_db_path() so the CLI
cannot create divergent SQLite files.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from utils.helpers import get_db

app = typer.Typer(help="Account‑related commands")
console = Console()

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
TRANSFER_CATEGORY = "__transfer__"  # unlikely to collide with user categories

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:  # thin wrapper in case we swap driver
    return get_db()

# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

@app.command("create-account")
def create_account(
    name: str = typer.Argument(..., help="Unique account name, e.g., Savings"),
    acct_type: str = typer.Option(
        "bank",
        "--type",
        help="Account type: bank | wallet | cash | other",
        show_default=True,
    ),
    balance: float = typer.Option(0.0, "--balance", help="Opening balance"),
    wallet: Optional[str] = typer.Option(
        None, "--wallet", help="0x… address for on‑chain wallets"
    ),
):
    """Create a new account row."""

    with _connect() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM accounts WHERE name = ?", (name,))
        if c.fetchone():
            console.print(f"[red]Account already exists:[/red] {name}")
            raise typer.Exit(code=1)

        c.execute(
            "INSERT INTO accounts (name, type, balance, wallet) VALUES (?, ?, ?, ?)",
            (name, acct_type, balance, wallet),
        )
        conn.commit()

    console.print(
        f"[green]✓[/green] Created account '[bold]{name}[/bold]' with balance ${balance:.2f}"
    )


@app.command("set-balance")
def set_balance(
    name: str = typer.Argument(..., help="Account to modify"),
    new_balance: float = typer.Argument(..., help="New absolute balance"),
):
    """Force‑set an account balance (use rarely!)."""

    with _connect() as conn:
        c = conn.cursor()
        res = c.execute("UPDATE accounts SET balance = ? WHERE name = ?", (new_balance, name))
        if res.rowcount == 0:
            console.print(f"[red]Account not found:[/red] {name}")
            raise typer.Exit(code=1)
        conn.commit()

    console.print(
        f"[yellow]Balance set[/yellow] — {name} now ${new_balance:.2f} (manual override)"
    )


@app.command("transfer")
def transfer_funds(
    from_account: str = typer.Argument(..., help="Debit this account"),
    to_account: str = typer.Argument(..., help="Credit this account"),
    amount: float = typer.Argument(..., help="Amount to move"),
):
    """Move money between two existing accounts (atomic)."""

    if amount <= 0:
        console.print("[red]Amount must be positive.[/red]")
        raise typer.Exit(code=1)

    with _connect() as conn:
        c = conn.cursor()

        # fetch balances + validate accounts
        c.execute("SELECT balance FROM accounts WHERE name = ?", (from_account,))
        row_from = c.fetchone()
        c.execute("SELECT balance FROM accounts WHERE name = ?", (to_account,))
        row_to = c.fetchone()

        if row_from is None:
            console.print(f"[red]Account not found:[/red] {from_account}")
            raise typer.Exit(code=1)
        if row_to is None:
            console.print(f"[red]Account not found:[/red] {to_account}")
            raise typer.Exit(code=1)
        if row_from[0] < amount:
            console.print(
                f"[red]Insufficient funds:[/red] {from_account} only has ${row_from[0]:.2f}"
            )
            raise typer.Exit(code=1)

        try:
            c.execute("BEGIN")
            c.execute(
                "UPDATE accounts SET balance = balance - ? WHERE name = ?",
                (amount, from_account),
            )
            c.execute(
                "UPDATE accounts SET balance = balance + ? WHERE name = ?",
                (amount, to_account),
            )
            # Record an expense for audit trail
            c.execute(
                "INSERT INTO expenses (amount, category, description, account, metadata, note, date) "
                "VALUES (?, ?, ?, ?, NULL, NULL, DATE('now'))",
                (
                    amount,
                    TRANSFER_CATEGORY,
                    f"Transfer to {to_account}",
                    from_account,
                ),
            )
            conn.commit()
        except Exception as err:
            conn.rollback()
            console.print(f"[red]Transfer failed:[/red] {err}")
            raise typer.Exit(code=1)

    console.print(
        f"✅ Transferred ${amount:.2f} from '[bold]{from_account}[/bold]' → '[bold]{to_account}[/bold]'"
    )


# ---------------------------------------------------------------------------
# legacy shim (keeps old imports alive without code duplication)
# ---------------------------------------------------------------------------

def add_account(*args, **kwargs):
    """Alias for backward compatibility (deprecated)."""

    console.print(
        "[yellow]add_account() is deprecated. Use 'create-account' instead.[/yellow]"
    )
    return create_account(*args, **kwargs)
