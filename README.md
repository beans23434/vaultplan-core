


---

📝 Updated README.md

Here’s the structure we’ll focus on:


---

📑 VaultPlan Installation Guide

# VaultPlan Core (v1.0.3)

VaultPlan is a terminal-native, offline-first personal finance CLI tool. It helps you survive, stabilize, and grow — from broke to balanced.

---

## Installation

1. **Unzip and enter directory (if using zip):**
```bash
unzip vaultplan.zip
cd vaultplan

2. Make executable:



chmod +x vaultplan.py

3. Link globally (symlink vaultplan to the bin directory):



mkdir -p ~/.local/bin
ln -sf $(pwd)/vaultplan.py ~/.local/bin/vaultplan

4. Run install script to complete the setup:



./install.sh

5. Run VaultPlan (CLI Usage):



vaultplan --help


---

Core Commands

Accounts

vaultplan create-account "Cash" --type wallet --balance 0
vaultplan create-account "Bank" --type bank --balance 20
vaultplan transfer "Bank" "Cash" 20
vaultplan balance

Income

vaultplan add-income 370 --source "JobA" --account "Bank"

Expenses

vaultplan add-expense 45.50 --category food --description "groceries" --account "Bank" --note "first run"

Goals

vaultplan set-goal "Emergency" 1000 --account Bank --priority 2
vaultplan update-goal "Emergency" --amount 50 --account Bank
vaultplan list-goals --status active

Debits

vaultplan add-debit "Phone Bill" 50 --account "Bank" --due-date 2025-06-01
vaultplan pay-debit 1 "Bank" --amount 25
vaultplan list-debits --all

To-Do List

vaultplan todo add "Update README"
vaultplan todo list
vaultplan todo done 2
vaultplan todo delete 3


Notes

vaultplan add-note 6 "holding it together" --account "Bank"
vaultplan list-notes --account "Bank" --days 7

Summaries

vaultplan summary
vaultplan export-summary --mode weekly --output-dir reports


Web3?

Dont expect much here it is the keast focus point of my finicial stuff?? i dont know haha
good skeleton to build from. Web 3 is the least focua point for ms right now.
also need to add a free etherscan api key to use.

vaultplan web3-sync <- will sync all etherscan v2 normal transactions and erc20 transactions for any accounts with a wallet address linked.
vaultplan summary-web3 <-- will disolay a very bare bones summmary of erc20 and normal transactions and what they are worth in USD.

---

Notes:

The install.sh script will move all necessary files to the ~/.vaultplan/ directory.

The config.json and vaultplan.db will be located inside ~/.vaultplan/data/.

To update VaultPlan, simply re-run the install.sh to sync any changes.

If you face permission issues on Termux, use chmod +x to ensure the vaultplan.py script is executable.



---

Support

VaultPlan was built during grief, poverty, and recovery — coded on a phone, logged by need.
To support or unlock premium modes: VaultPlan on Gumroad


---

🛠️ Troubleshooting:

If you encounter permission issues, run:

chmod +x ~/.vaultplan/vaultplan.py

If installation fails, ensure you have the required dependencies installed:

pkg install python git sqlite
pip install typer rich

---
