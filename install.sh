#!/bin/bash

echo "[*] Installing VaultPlan..."

# Dependencies
pkg install -y python git sqlite
pip install typer rich

# Setup directories
mkdir -p ~/.vaultplan/data

# Move backup DB (if demo provided)
if [ -f demo.db ]; then
    cp demo.db ~/.vaultplan/data/vaultplan.db
fi

# Make script executable
chmod +x vaultplan.py
echo "alias vaultplan='python ~/vaultplan/vaultplan.py'" >> ~/.bashrc
source ~/.bashrc

echo "[✓] Done. Type 'vaultplan wizard' to start."
