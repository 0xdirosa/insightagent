import uuid
import json
import os
from datetime import datetime

TRANSACTIONS_FILE = "transactions.json"

def load_transactions():
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_transaction(tx):
    txs = load_transactions()
    txs.insert(0, tx)
    txs = txs[:100]
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump(txs, f, indent=2)

def place_bet(market, wallet, amount_usdc=1.0):
    yes = market['yes'] / 100
    kelly = min(round((0.05 / (1 - yes)) * 100, 1), 10) if yes < 1 else 0

    if market['yes'] >= 50:
        position = "YES"
        price = market['yes']
    else:
        position = "NO"
        price = market['no']

    potential_return = round(amount_usdc / (price / 100), 2)
    profit = round(potential_return - amount_usdc, 2)

    tx = {
        "id": str(uuid.uuid4())[:8].upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market": market['question'][:70],
        "market_id": market.get('id', ''),
        "position": position,
        "price": price,
        "amount_usdc": amount_usdc,
        "potential_return": potential_return,
        "profit": profit,
        "kelly_pct": kelly,
        "wallet": wallet['short'],
        "wallet_address": wallet['address'],
        "chain": wallet.get('chain', 'ARC-TESTNET'),
        "status": "SIMULATED",
        "type": "POLYMARKET_BET"
    }

    save_transaction(tx)
    return tx

def pick_best_market(markets):
    candidates = [
        m for m in markets
        if m['volume'] > 500000 and 30 <= m['yes'] <= 70
    ]
    if not candidates:
        candidates = [
            m for m in markets
            if m['volume'] > 100000 and 20 <= m['yes'] <= 80
        ]
    if not candidates:
        return None
    candidates.sort(key=lambda x: x['volume'], reverse=True)
    return candidates[0]
