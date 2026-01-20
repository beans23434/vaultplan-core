# clear_tables.py

import sqlite3

from utils.paths import DB_PATH

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
            name TEXT,
            target_amount REAL,
            saved_amount REAL DEFAULT 0,
            deadline TEXT,
            account TEXT,
            priority INTEGER DEFAULT 3,
            note TEXT,
            status TEXT DEFAULT 'active'
        )
    """,
    "debits": """
        CREATE TABLE IF NOT EXISTS debits (
            id INTEGER PRIMARY KEY,
            label TEXT,
            amount_due REAL,
            amount_paid REAL DEFAULT 0,
            due_date TEXT,
            account TEXT,
            status TEXT DEFAULT 'open'
        )
    """,
    "notes": """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            mood INTEGER,
            note TEXT,
            account TEXT,
            tags TEXT,
            created_at TEXT
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
