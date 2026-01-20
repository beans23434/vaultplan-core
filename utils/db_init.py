# utils/db_init.py
import sqlite3

from utils.paths import DB_PATH

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
            name TEXT,
            target_amount REAL,
            saved_amount REAL DEFAULT 0,
            deadline TEXT,
            account TEXT,
            priority INTEGER DEFAULT 3,
            note TEXT,
            status TEXT DEFAULT 'active'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS debits (
            id INTEGER PRIMARY KEY,
            label TEXT,
            amount_due REAL,
            amount_paid REAL DEFAULT 0.0,
            due_date TEXT,
            account TEXT,
            status TEXT DEFAULT 'open'
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
            tx_type TEXT,
            symbol TEXT,
            amount_token REAL,
            value_fiat REAL,
            account TEXT,
            description TEXT,
            hash TEXT,
            PRIMARY KEY(hash, account)
        )
    """)

    conn.commit()
    conn.close()
