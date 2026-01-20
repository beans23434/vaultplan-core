from pathlib import Path

INSTALL_DIR = Path.home() / ".vaultplan"
DATA_DIR = INSTALL_DIR / "data"
DB_PATH = DATA_DIR / "vaultplan.db"
CONFIG_PATH = INSTALL_DIR / "config.json"
