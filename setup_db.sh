#!/data/data/com.termux/files/usr/bin/bash

DB_DIR="$HOME/.vaultplan/data"
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
    date TEXT,
    note TEXT,
    metadata TEXT
);

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
);

CREATE TABLE IF NOT EXISTS debits (
    id INTEGER PRIMARY KEY,
    label TEXT,
    amount_due REAL,
    amount_paid REAL DEFAULT 0,
    due_date TEXT,
    account TEXT,
    status TEXT DEFAULT 'open'
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY,
    mood INTEGER,
    note TEXT,
    account TEXT,
    tags TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS web3_seen_tx (
    hash TEXT,
    direction TEXT,
    account TEXT,
    chain_id INTEGER,
    date TEXT,
    PRIMARY KEY (hash, direction)
);

CREATE TABLE IF NOT EXISTS web3_scan_state (
    wallet TEXT,
    chain_id INTEGER,
    last_block INTEGER,
    PRIMARY KEY (wallet, chain_id)
);

CREATE TABLE IF NOT EXISTS web3_transactions (
    date TEXT,
    tx_type TEXT,
    symbol TEXT,
    amount_token REAL,
    value_fiat REAL,
    account TEXT,
    description TEXT,
    hash TEXT,
    PRIMARY KEY (hash, account)
);
EOF

echo "✅ VaultPlan database initialized at $DB_PATH"
