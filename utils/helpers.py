from pathlib import Path
import os
import sqlite3
import requests
import json
from datetime import datetime

DB_PATH = Path.home() / ".vaultplan" / "data" / "vaultplan.db"

def get_token_prices(symbols: list[str]) -> dict:
    """
    For each token symbol, query Dexscreener search API and return AUD prices.
    """
    prices = {}
    for symbol in symbols:
        try:
            url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
            r = requests.get(url, timeout=5)
            result = r.json().get("pairs", [])
            if not result:
                prices[symbol] = 0
                continue

            # Prefer USD-quoted price
            for pair in result:
                if pair.get("quoteToken", {}).get("symbol", "").upper() == "USD":
                    usd = float(pair.get("priceUsd", 0.0))
                    prices[symbol] = round(usd * 1.54, 6)
                    break
            else:
                # Fallback: take first match
                usd = float(result[0].get("priceUsd", 0.0))
                prices[symbol] = round(usd * 1.54, 6)

        except Exception:
            prices[symbol] = 0

    return prices

def ensure_data_dir():
    os.makedirs(DB_PATH.parent, exist_ok=True)

def get_db():
    ensure_data_dir()
    return sqlite3.connect(DB_PATH)

def get_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}

def get_display_currency():
    return get_config().get("display_currency", "AUD")
