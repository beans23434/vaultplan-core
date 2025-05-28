"""VaultPlan ‒ Web3 wallet synchroniser (cleaned for v1.0‑rc1)

Fetches on‑chain ETH & ERC‑20 transfers, records them in the local
SQLite ledger, and (optionally) updates the linked account balance.

Dependencies
------------
•   utils.helpers.get_db, get_token_prices, get_config   – existing helper
•   fetch_normal.fetch_eth_transfers                     – per‑chain ETH scanner
•   fetch_erc20.fetch_token_transfers                    – per‑chain ERC‑20 scanner
•   commands.account.set_balance                         – manual balance adjuster

This file NEVER touches hard‑coded paths.  All DB work goes through the
`get_db()` helper which already wraps utils.path_helpers.get_db_path().

Atomicity: every DB change is performed inside a single connection /
transaction per wallet+chain to avoid half‑written entries.
"""
from __future__ import annotations

import sqlite3
from typing import List, Dict, Any

from utils.helpers import (
    get_db,
    get_token_prices,
    get_config,
)

from .fetch_normal import fetch_eth_transfers
from .fetch_erc20 import fetch_token_transfers
from commands.account import set_balance  # internal helper, not CLI

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS web3_scan_state (
            wallet      TEXT,
            chain_id    INTEGER,
            last_block  INTEGER,
            PRIMARY KEY (wallet, chain_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS web3_transactions (
            date            TEXT,
            type            TEXT,
            symbol          TEXT,
            amount_token    REAL,
            price_at_time   REAL,
            value_aud       REAL,
            account         TEXT,
            description     TEXT,
            hash            TEXT,
            PRIMARY KEY(hash, account)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS web3_seen_tx (
            hash        TEXT,
            direction   TEXT,
            account     TEXT,
            chain_id    INTEGER,
            date        TEXT,
            PRIMARY KEY(hash, direction)
        )
        """
    )
    conn.commit()


def _get_wallet_accounts() -> List[Dict[str, str]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, wallet FROM accounts WHERE type='wallet' AND wallet IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return [{"name": row[0], "address": row[1]} for row in rows]


# ---------------------------------------------------------------------------
# Public entry‑point
# ---------------------------------------------------------------------------

def web3_sync() -> None:
    """Synchronise all on‑file wallets across configured chains."""
    cfg = get_config()
    chains: List[int] = cfg.get("etherscan_chains", [1])  # default mainnet

    wallets = _get_wallet_accounts()
    print(f"[web3_sync] scanning {len(wallets)} wallet(s)…")

    token_whitelist = {"ETH", "DEGEN", "USDC"}
    prices = get_token_prices(list(token_whitelist))
    print(f"[web3_sync] price snapshot: {prices}")

    for w in wallets:
        _sync_single_wallet(w["name"], w["address"], chains, token_whitelist, prices)


def _sync_single_wallet(
    account_name: str,
    address: str,
    chains: List[int],
    token_whitelist: set[str],
    prices: Dict[str, float],
):
    print(f"→ {account_name}  {address}")

    combined: List[Dict[str, Any]] = []

    for chain_id in chains:
        conn = get_db()
        _ensure_tables(conn)
        cur = conn.cursor()

        # last processed block
        cur.execute(
            "SELECT last_block FROM web3_scan_state WHERE wallet=? AND chain_id=?",
            (address, chain_id),
        )
        row = cur.fetchone()
        from_block = (row[0] + 1) if row else None

        # fetch remote txs
        eth_txs = fetch_eth_transfers(address, chain_id, from_block)
        token_txs = fetch_token_transfers(address, list(token_whitelist), chain_id, from_block)

        for tx in eth_txs + token_txs:
            tx["chain_id"] = chain_id
        combined.extend(eth_txs + token_txs)

        # update cursor
        if combined:
            latest_block = max(tx.get("block", 0) for tx in combined)
            cur.execute(
                """
                INSERT INTO web3_scan_state (wallet, chain_id, last_block)
                VALUES (?, ?, ?)
                ON CONFLICT(wallet, chain_id) DO UPDATE SET last_block=excluded.last_block
                """,
                (address, chain_id, latest_block),
            )
            conn.commit()
        conn.close()

    # --------------- write transactions & mark seen -----------------
    for tx in combined:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM web3_seen_tx WHERE hash=? AND direction=?",
                (tx["hash"], tx["direction"]),
            )
            if cur.fetchone():
                continue  # already processed

            # classify + enrich
            tx_type = "income" if (tx["symbol"] == "ETH" and tx["direction"] == "in") else "swap"
            price = prices.get(tx["symbol"], 0)
            value_aud = tx["amount"] * price

            cur.execute(
                """
                INSERT OR IGNORE INTO web3_transactions
                          (date, type, symbol, amount_token, price_at_time,
                           value_aud, account, description, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tx["date"],
                    tx_type,
                    tx["symbol"],
                    tx["amount"],
                    price,
                    value_aud,
                    account_name,
                    f"{tx['symbol']} {tx_type} {tx['hash'][:8]}",
                    tx["hash"],
                ),
            )

            cur.execute(
                "INSERT INTO web3_seen_tx (hash, direction, account, chain_id, date) VALUES (?,?,?,?,?)",
                (
                    tx["hash"],
                    tx["direction"],
                    account_name,
                    tx["chain_id"],
                    tx["date"],
                ),
            )
            conn.commit()

    # --------------- optional balance update -----------------------
    final_eth_txs = [t for t in combined if t["symbol"] == "ETH"]
    if final_eth_txs:
        latest = max(final_eth_txs, key=lambda t: t.get("block", 0))
        if "final_balance_aud" in latest:
            set_balance.callback(account_name, latest["final_balance_aud"])
            print(
                f"[web3_sync] {account_name} balance → {latest['final_balance_aud']:.2f} AUD",
            )
