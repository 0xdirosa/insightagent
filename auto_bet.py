import requests
import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY")
BASE_URL = "https://api.circle.com/v1/w3s"
TRANSACTIONS_FILE = "transactions.json"

def load_transactions():
    with open(TRANSACTIONS_FILE, "r") as f:
        return json.load(f)

def save_transaction(tx):
    txs = load_transactions()
    txs.insert(0, tx)
    txs = txs[:50]  # simpan max 50
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump(txs, f, indent=2)

def get_markets():
    url = "https://gamma-api.polymarket.com/markets"
    params = {"limit": 30, "active": "true", "closed": "false"}
    response = requests.get(url, params=params)
    markets = response.json()
    result = []
    for m in markets:
        prices = m.get('outcomePrices', '[]')
        if isinstance(prices, str):
            try:
                prices = json.loads(prices)
            except:
                prices = []
        yes_price = float(prices[0]) if prices else 0
        volume = float(m.get('volume', 0))
        result.append({
            "question": m['question'],
            "yes": round(yes_price * 100, 1),
            "no": round((1 - yes_price) * 100, 1),
            "volume": round(volume, 0)
        })
    return result

def pick_best_market(markets):
    """Pilih market terbaik berdasarkan volume + uncertainty"""
    interesting = [
        m for m in markets
        if m['volume'] > 500000 and 30 <= m['yes'] <= 70
    ]
    if not interesting:
        return None
    interesting.sort(key=lambda x: x['volume'], reverse=True)
    return interesting[0]

def get_wallet():
    headers = {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{BASE_URL}/wallets", headers=headers)
    data = response.json()
    wallets = data.get("data", {}).get("wallets", [])
    return wallets[0] if wallets else None

def simulate_bet(market, wallet, amount_usdc=1.0):
    """Simulasi place bet dan catat sebagai transaksi"""
    yes = market['yes'] / 100
    kelly = min(round((0.05 / (1 - yes)) * 100, 1), 10)
    
    # Tentukan posisi
    if market['yes'] >= 55:
        position = "YES"
        price = market['yes']
    else:
        position = "NO"
        price = market['no']
    
    tx = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market": market['question'][:60] + "...",
        "position": position,
        "price": price,
        "amount_usdc": amount_usdc,
        "kelly_pct": kelly,
        "wallet": wallet['address'][:10] + "..." + wallet['address'][-6:],
        "chain": wallet.get('blockchain', 'ARC-TESTNET'),
        "status": "SIMULATED",
        "potential_return": round(amount_usdc / (price / 100), 2)
    }
    
    save_transaction(tx)
    return tx

def run_auto_bet():
    print("=" * 60)
    print("🤖 INSIGHTAGENT — Auto Bet Engine")
    print("=" * 60)
    
    print("\n📊 Fetching markets...")
    markets = get_markets()
    
    print("🎯 Picking best market...")
    best = pick_best_market(markets)
    
    if not best:
        print("❌ No suitable market found")
        return
    
    print(f"✅ Selected: {best['question']}")
    print(f"   Yes: {best['yes']}% | No: {best['no']}% | Vol: ${best['volume']:,.0f}")
    
    print("\n🔑 Getting wallet...")
    wallet = get_wallet()
    if not wallet:
        print("❌ No wallet found")
        return
    
    print(f"✅ Wallet: {wallet['address'][:10]}...{wallet['address'][-6:]}")
    
    print("\n💸 Simulating bet (1 USDC)...")
    tx = simulate_bet(best, wallet, amount_usdc=1.0)
    
    print(f"\n✅ BET PLACED!")
    print(f"   Market: {tx['market']}")
    print(f"   Position: {tx['position']} @ {tx['price']}%")
    print(f"   Amount: ${tx['amount_usdc']} USDC")
    print(f"   Potential return: ${tx['potential_return']} USDC")
    print(f"   Chain: {tx['chain']}")
    print(f"   TX ID: {tx['id']}")

if __name__ == "__main__":
    run_auto_bet()
