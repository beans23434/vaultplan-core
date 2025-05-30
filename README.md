


---

📝 Updated README.md


---

📑 VaultPlan Installation Guide

# VaultPlan Core (v1.0.3)

VaultPlan is a terminal-native, offline-first personal finance CLI tool. It helps you survive, stabilize, and grow — from broke to balanced.

## Installation

1. **Unzip and enter directory (if using zip):**
```bash
unzip vaultplan.zip
cd vaultplan
```
2. Make executable:
```bash
chmod +x vaultplan.py
```

3. Link globally (symlink vaultplan to the bin directory):
```bash
mkdir -p ~/.local/bin
ln -sf $(pwd)/vaultplan.py ~/.local/bin/vaultplan
```

4. Run install script to complete the setup:
```bash
./install.sh
```

5. Run VaultPlan (CLI Usage):
```bash
vaultplan --help
```
---
## Core Commands

### Accounts
```bash
vaultplan create-account "Cash" --type wallet --balance 0
vaultplan create-account "Bank" --type bank --balance 20
vaultplan transfer "Bank" "Cash" 20
vaultplan balance
```


### Income
```bash
vaultplan add-income 370 --source "JobA" --account "Bank"
```


### Expenses
```bash
vaultplan add-expense 45.50 --category food --description "groceries" --account "Bank" --note "first run"
```


### Goals
```bash
vaultplan set-goal "Emergency" 1000 --account Bank --priority 2
vaultplan update-goal "Emergency" --amount 50 --account Bank
vaultplan list-goals --status active
```


### Debits
```bash
vaultplan add-debit "Phone Bill" 50 --account "Bank" --due-date 2025-06-01
vaultplan pay-debit 1 "Bank" --amount 25
vaultplan list-debits --all
```


### To-Do List
```bash
vaultplan todo add "Update README"
vaultplan todo list
vaultplan todo done 2
vaultplan todo delete 3
```

### Notes
```bash
vaultplan add-note 6 "holding it together" --account "Bank"
vaultplan list-notes --account "Bank" --days 7
```


### Summaries
```bash
vaultplan summary
vaultplan export-summary --mode weekly --output-dir reports
```

### Web3?

Dont expect much here it is the least thing of my finicial stuff?? i don't know haha
good skeleton to build from. Web 3 is the least focus point for ms right now.
also need to add a free etherscan api key to use.

```bash
vaultplan web3-sync <- will sync all etherscan v2 normal transactions and erc20 transactions for any accounts with a wallet address linked.
vaultplan summary-web3 <-- will disolay a very bare bones summmary of erc20 and normal transactions and what they are worth in USD.
```
---
## Notes:

The `install.sh` script will move all necessary files to the `~/.vaultplan/ directory`.

The config.json and `vaultplan.db` will be located inside `~/.vaultplan/data/`.

To update VaultPlan, simply re-run the `install.sh` to sync any changes.

If you face permission issues on Termux, use `chmod +x` to ensure the `vaultplan.py` script is executable.

---

Quick tool to calculate loose coins based on your total wallet cash.
```bash
vaultplan coins check 55
```

> If your full wallet is $80, this tells you the $25 difference is coins.

#### You’ll get:

🧠 Coin Mode Result
🎯 Action: HOLD
💬 Message: Coins $25.00 not yet at $50 threshold. No deposit triggered.

🧠 Coin Mode Result
🎯 Action: HOLD
💬 Message: Coins $25.00 not yet at $50 threshold. No deposit triggered.

---

## Support

VaultPlan was built during grief, poverty, and recovery — coded on a phone, logged by need.
To support or unlock premium modes: VaultPlan on Gumroad
---
## 🛠️ Troubleshooting:

If you encounter permission issues, run:
```bash
chmod +x ~/.vaultplan/vaultplan.py
```

If installation fails, ensure you have the required dependencies installed:
```bash
pkg install python-pip git sqlite
pip install typer rich
```
---
