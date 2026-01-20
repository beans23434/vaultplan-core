#!/data/data/com.termux/files/usr/bin/bash

echo "[*] Installing VaultPlan..."

INSTALL_DIR="$HOME/.vaultplan"
BIN_DIR="$HOME/.local/bin"
SRC_DIR="$(pwd)"
BACKUP_DIR=""

# Create necessary dirs
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$BIN_DIR"

# Backup existing user data/config to avoid overwrite during updates
BACKUP_DIR="$(mktemp -d)"
if [ -d "$INSTALL_DIR/data" ]; then
  cp -a "$INSTALL_DIR/data" "$BACKUP_DIR/data"
fi
if [ -f "$INSTALL_DIR/config.json" ]; then
  cp -a "$INSTALL_DIR/config.json" "$BACKUP_DIR/config.json"
fi

# Copy everything to ~/.vaultplan (code + scripts)
cp -r "$SRC_DIR"/* "$INSTALL_DIR"/

# Restore user data/config
if [ -d "$BACKUP_DIR/data" ]; then
  rm -rf "$INSTALL_DIR/data"
  cp -a "$BACKUP_DIR/data" "$INSTALL_DIR/data"
fi
if [ -f "$BACKUP_DIR/config.json" ]; then
  cp -a "$BACKUP_DIR/config.json" "$INSTALL_DIR/config.json"
fi

# Ensure config.json exists
if [ ! -f "$INSTALL_DIR/config.json" ]; then
  echo '{}' > "$INSTALL_DIR/config.json"
  echo "[+] Created blank config.json"
fi

# Symlink vaultplan to ~/.local/bin
# Set executable permissions
cat > "$BIN_DIR/vaultplan" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
python $INSTALL_DIR/vaultplan.py "\$@"
EOF
chmod +x "$BIN_DIR/vaultplan"

echo "[✓] VaultPlan installed to $INSTALL_DIR"
echo "[✓] Symlinked 'vaultplan' CLI to $BIN_DIR/vaultplan"
echo "[i] Run: vaultplan --help"
