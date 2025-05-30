#!/data/data/com.termux/files/usr/bin/bash

echo "[*] Installing VaultPlan..."

INSTALL_DIR="$HOME/.vaultplan"
BIN_DIR="$HOME/.local/bin"
SRC_DIR="$(pwd)"
DEPENDENCIES="python-pip sqlite git"

# Install dependencies
pkg update -y
apt install $DEPENDENCIES -y
pip install -r requirements.txt

# Create necessary dirs
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$BIN_DIR"

# Copy everything to ~/.vaultplan
cp -r "$SRC_DIR"/* "$INSTALL_DIR"/

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
