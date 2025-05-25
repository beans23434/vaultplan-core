# VaultPlan Core

A terminal-native, offline-first personal finance tool designed for resilience and self-reliance. VaultPlan Core helps you:

- Track account balances
- Log income and expenses
- Manage savings goals
- Record personal notes with moods
- Visualize summaries
- Maintain total local control

> Built for those who want to survive, plan, and grow — even offline.

---

## Install

1. **Unzip the repo:**
```bash
unzip vaultplan.zip
cd vaultplan
```

2. **Make the CLI executable:**
```bash
chmod +x vaultplan.py
```

3. **Link the CLI globally:**
```bash
mkdir -p ~/.local/bin
ln -sf $(pwd)/vaultplan.py ~/.local/bin/vaultplan
```

4. **Run install script (creates DB folders):**
```bash
./install.sh
```

5. **Run CLI help:**
```bash
vaultplan --help
```

---

## Core Commands

### Accounts
```bash
vaultplan account create "Cash" --type wallet --balance 0
vaultplan account transfer "Bank" "Cash" 20
vaultplan balance
```

### Income
```bash
vaultplan income add 370 --source "Centrelink" --account "Bank"
```

### Expenses
```bash
vaultplan expense add 45.50 --category food --description "groceries" --account "Bank" --note "first run"
```

### Goals
```bash
vaultplan goal set "Emergency" 1000 --account "Bank" --priority 2
vaultplan goal update "Emergency" --amount 50 --account "Bank"
vaultplan goal list --status active
```

### Debits
```bash
vaultplan debit add "Phone Bill" 50 --account "Bank"
vaultplan debit pay 1 "Bank" --amount 25
vaultplan debit list --all
```

### Notes
```bash
vaultplan note add 6 "holding it together" --account "Bank"
vaultplan note list --account "Bank" --days 7
```

### Summaries
```bash
vaultplan summary --days 14
vaultplan export --days 14 --output-dir reports
```

---

## Thank You

VaultPlan was built by someone climbing back from the bottom, coding on a budget phone, logging every dollar to survive.

If this tool helps you — financially, mentally, emotionally — please share it.

To support the project or unlock AI + Web3 features:
**[gumroad.com/vaultplan](https://gumroad.com/vaultplan)**

Stay grounded. Stay moving.
— VaultPlan
