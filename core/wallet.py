import requests
import os
import uuid
import json
from datetime import datetime

CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY")
BASE_URL = "https://api.circle.com/v1/w3s"

def get_headers():
    return {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type": "application/json"
    }

def get_wallets():
    try:
        response = requests.get(f"{BASE_URL}/wallets", headers=get_headers(), timeout=5)
        data = response.json()
        wallets = data.get("data", {}).get("wallets", [])
        return [{
            "id": w.get("id"),
            "address": w.get("address", "N/A"),
            "chain": w.get("blockchain", "N/A"),
            "state": w.get("state", "N/A"),
            "short": w.get("address", "")[:8] + "..." + w.get("address", "")[-6:]
        } for w in wallets]
    except:
        return []

def get_balance(wallet_id):
    try:
        url = f"{BASE_URL}/wallets/{wallet_id}/balances"
        response = requests.get(url, headers=get_headers(), timeout=5)
        data = response.json()
        balances = data.get("data", {}).get("tokenBalances", [])
        if not balances:
            return "0.00 USDC"
        for b in balances:
            if "USDC" in b.get("token", {}).get("symbol", ""):
                return f"{float(b.get('amount', 0)):.2f} USDC"
        return "0.00 USDC"
    except:
        return "N/A"

def get_stats():
    try:
        with open("transactions.json", "r") as f:
            txs = json.load(f)
        total_bets = len(txs)
        total_usdc = sum(float(t.get("amount_usdc", 0)) for t in txs)
        total_return = sum(float(t.get("potential_return", 0)) for t in txs)
        yes_bets = sum(1 for t in txs if t.get("position") == "YES")
        no_bets = sum(1 for t in txs if t.get("position") == "NO")
        return {
            "total_bets": total_bets,
            "total_usdc": round(total_usdc, 2),
            "total_return": round(total_return, 2),
            "pnl": round(total_return - total_usdc, 2),
            "yes_bets": yes_bets,
            "no_bets": no_bets
        }
    except:
        return {
            "total_bets": 0,
            "total_usdc": 0,
            "total_return": 0,
            "pnl": 0,
            "yes_bets": 0,
            "no_bets": 0
        }
