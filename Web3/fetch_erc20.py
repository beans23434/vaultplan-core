import requests
from utils.helpers import get_config
from datetime import datetime
from datetime import datetime

def fetch_token_transfers(address, tokens, chain_id=1, from_block=None):
    api_key = get_config().get("etherscan_api_key")
    if not api_key:
        print("[ERROR] Missing Etherscan API key in config.json")
        return []

    startblock = from_block if from_block is not None else 0
    url = (
      f"https://api.etherscan.io/v2/api"
      f"?chainid={chain_id}"
      f"&module=account&action=tokentx"
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
            symbol = tx["tokenSymbol"].upper()
            if symbol not in tokens:
                continue
            direction = "in" if tx["to"].lower() == address.lower() else "out"
            amount = float(tx["value"]) / (10 ** int(tx["tokenDecimal"]))

            parsed.append({
                "date": datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d"),
                "symbol": symbol,
                "amount": amount,
                "direction": direction,
                "desc": f"{symbol} {direction} transfer",
                "hash": tx["hash"]
            })
        return parsed
    except Exception as e:
        print(f"[fetch_token_transfers] Error: {e}")
        return []
