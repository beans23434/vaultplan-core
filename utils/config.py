# utils/config.py
import json
from pathlib import Path

# point at the project root next to vaultplan.py
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

def load_config() -> dict:
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
    except Exception:
        pass
    return {}

def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

# Default fallback is dollar symbol
DEFAULT_CURRENCY_SYMBOL = "$"

def get_display_currency():
    currency_map = {
        "USD": "$",
        "AUD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "INR": "₹",
        "KRW": "₩",
        "BTC": "₿",
        "ETH": "Ξ"
    }

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            code = data.get("display_currency", "USD")
            return currency_map.get(code.upper(), DEFAULT_CURRENCY_SYMBOL)
        except Exception:
            return DEFAULT_CURRENCY_SYMBOL
    return DEFAULT_CURRENCY_SYMBOL
