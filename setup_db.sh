#!/data/data/com.termux/files/usr/bin/bash

DB_DIR="$HOME/vaultplan/data"
DB_PATH="$DB_DIR/vaultplan.db"

mkdir -p "$DB_DIR"

sqlite3 "$DB_PATH" <<EOF
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    name TEXT,
    type TEXT,
    balance REAL,
    wallet TEXT
);

CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY,
    account TEXT,
    amount REAL,
    source TEXT,
    date TEXT
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    account TEXT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TEXT
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    title TEXT,
    target_amount REAL,
    current_amount REAL,
    account TEXT,
    priority INTEGER,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS debits (
    id INTEGER PRIMARY KEY,
    label TEXT,
    amount_due REAL,
    due_date TEXT,
    paid INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY,
    mood INTEGER,
    text TEXT,
    tags TEXT,
    date TEXT
);
EOF

echo "✅ VaultPlan database initialized at $DB_PATH"
