# utils/db_init.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "vaultplan.db"

def init_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            balance REAL,
            wallet TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY,
            account TEXT,
            amount REAL,
            source TEXT,
            date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            account TEXT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT,
            note TEXT,
            metadata TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            title TEXT,
            target_amount REAL,
            current_amount REAL DEFAULT 0,
            account TEXT,
            priority INTEGER,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            note TEXT,
            deadline TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS debits (
            id INTEGER PRIMARY KEY,
            label TEXT,
            amount_due REAL,
            account TEXT,
            due_date TEXT,
            created_at TEXT,
            paid REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            note TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            mood INTEGER,
            note TEXT,
            account TEXT,
            tags TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS web3_seen_tx (
            hash TEXT,
            direction TEXT,
            account TEXT,
            chain_id INTEGER,
            date TEXT,
            PRIMARY KEY (hash, direction)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS web3_scan_state (
            wallet TEXT,
            chain_id INTEGER,
            last_block INTEGER,
            PRIMARY KEY (wallet, chain_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS web3_transactions (
            date TEXT,
            type TEXT, -- “income” or “expense”
            symbol TEXT,
            amount_token REAL,
            price_at_time REAL,
            value_aud REAL,
            account TEXT,
            description TEXT,
            hash TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()
