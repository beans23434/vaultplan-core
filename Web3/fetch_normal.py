import requests
import os
from utils.helpers import get_config
from datetime import datetime

def fetch_eth_transfers(address, chain_id=1, from_block=None):
    api_key = get_config().get("etherscan_api_key")
    if not api_key:
        print("[ERROR] Missing Etherscan API key in config.json")
        return []

    startblock = from_block if from_block is not None else 0
    url = (
      f"https://api.etherscan.io/v2/api"
      f"?chainid={chain_id}"
      f"&module=account&action=txlist"
      f"&address={address}"
      f"&startblock={startblock}&endblock=99999999"
      f"&sort=asc&apikey={api_key}"
    )

    try:
        r = requests.get(url)
        data = r.json()
        txs = data.get("result", [])
        parsed = []
        for tx in txs:
            # skip failed or contract creation txs
            if tx["isError"] != "0" or tx["to"] == "":
                continue

            direction = "in" if tx["to"].lower() == address.lower() else "out"
            parsed.append({
                "date": datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d"),
                "symbol": "ETH",
                "amount": float(tx["value"]) / 1e18,
                "direction": direction,
                "desc": f"ETH {direction} transfer",
                "hash": tx["hash"]
            })
        return parsed
    except Exception as e:
        print(f"[fetch_eth_transfers] Error: {e}")
        return []
