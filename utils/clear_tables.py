# clear_tables.py

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "vaultplan" / "data" / "vaultplan.db"

TABLES = [
    "accounts",
    "income",
    "expenses",
    "goals",
    "debits",
    "notes"
]

SCHEMAS = {
    "accounts": """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            balance REAL,
            wallet TEXT
        )
    """,
    "income": """
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY,
            amount REAL,
            source TEXT,
            date TEXT,
            account TEXT
        )
    """,
    "expenses": """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount REAL,
            category TEXT,
            description TEXT,
            account TEXT,
            metadata TEXT,
            note TEXT,
            date TEXT
        )
    """,
    "goals": """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            title TEXT,
            target_amount REAL,
            current_amount REAL DEFAULT 0,
            account TEXT,
            priority INTEGER,
            deadline TEXT,
            note TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'active'
        )
    """,
    "debits": """
        CREATE TABLE IF NOT EXISTS debits (
            id INTEGER PRIMARY KEY,
            label TEXT,
            amount REAL,
            account TEXT,
            due_date TEXT,
            note TEXT,
            paid REAL DEFAULT 0,
            created_at TEXT,
            status TEXT DEFAULT 'pending'
        )
    """,
    "notes": """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            mood INTEGER,
            note TEXT,
            timestamp TEXT
        )
    """
}

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for table in TABLES:
    print(f"Dropping and recreating: {table}")
    c.execute(f"DROP TABLE IF EXISTS {table}")
    c.execute(SCHEMAS[table])

conn.commit()
conn.close()
print("✅ All VaultPlan tables reset.")
