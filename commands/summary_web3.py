from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from utils.helpers import get_token_prices, get_db
from utils.config import get_display_currency
currency = get_display_currency()

def summary_web3():
    console = Console()
    conn = get_db()
    c = conn.cursor()

    # ── aggregate web3_transactions by type ──
    c.execute("""
        SELECT type,
               COUNT(*) AS cnt,
               SUM(value_aud) FILTER(WHERE type='income')  AS total_in_aud,
               SUM(value_aud) FILTER(WHERE type='expense') AS total_out_aud
        FROM web3_transactions
        GROUP BY type
    """)
    rows = c.fetchall()
    data = {r[0]: {"count": r[1], "sum_in": r[2] or 0, "sum_out": r[3] or 0} for r in rows}
    income  = data.get("income",  {"count": 0, "sum_in": 0})
    expense = data.get("expense", {"count": 0, "sum_out": 0})
    swap    = data.get("swap",    {"count": 0})

    # Build summary table
    summary_table = Table(show_header=True, header_style="bold cyan")
    summary_table.add_column("Type", justify="left")
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("AUD Total", justify="right")
    summary_table.add_row("ETH In (income)",  str(income["count"]),  f"{currency}{income['sum_in']:.2f}")
    summary_table.add_row("ETH Out (expense)", str(expense["count"]), f"{currency}{expense['sum_out']:.2f}")
    summary_table.add_row("Swaps (any token)", str(swap["count"]),    "—")

    summary_panel = Panel(summary_table, title="VaultPlan Web3 Summary", padding=(1, 2))

    # ── Latest 5 transactions preview ──
    c.execute("""
        SELECT date, type, symbol, amount_token, value_aud
        FROM web3_transactions
        ORDER BY date DESC
        LIMIT 5
    """)
    recent = c.fetchall()
    preview_table = Table(show_header=True, header_style="bold magenta")
    preview_table.add_column("Date", justify="left")
    preview_table.add_column("Type", justify="left")
    preview_table.add_column("Symbol", justify="center")
    preview_table.add_column("Token Amount", justify="right")
    preview_table.add_column("AUD Value", justify="right")
    for date, ttype, sym, amt, val in recent:
        preview_table.add_row(date, ttype, sym, f"{amt:.8f}", f"{currency}{val:.2f}")

    preview_panel = Panel(preview_table, title="Latest 5 Transactions", padding=(1, 2))

    # Print side by side
    console.print(Columns([summary_panel, preview_panel], expand=True))

    conn.close()
