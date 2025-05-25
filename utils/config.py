# utils/config.py
import json
from pathlib import Path

# point at the project root next to vaultplan.py
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
