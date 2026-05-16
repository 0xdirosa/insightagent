import requests
import os
import uuid
from datetime import datetime

CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY")
BASE_URL = "https://api.circle.com/v1/w3s"

def get_headers():
    return {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type": "application/json"
    }

def get_paymaster_info():
    try:
        response = requests.get(
            f"{BASE_URL}/config/entity",
            headers=get_headers(),
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def simulate_sponsored_tx(wallet_address, operation="BET_PLACEMENT"):
    """Simulasi sponsored transaction via Paymaster — gas dibayar USDC"""
    tx = {
        "id": str(uuid.uuid4())[:8].upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "PAYMASTER_SPONSORED",
        "operation": operation,
        "wallet": wallet_address[:10] + "..." + wallet_address[-6:],
        "gas_sponsored": True,
        "gas_amount": "0.01 USDC",
        "gas_cost_usd": "$0.01",
        "sponsor": "InsightAgent Paymaster",
        "chain": "ARC-TESTNET",
        "status": "SPONSORED"
    }
    return tx

def estimate_gas_savings(num_transactions=10):
    """Estimasi penghematan gas user — Arc pakai USDC untuk gas"""
    gas_per_tx = 0.01
    total_usdc = gas_per_tx * num_transactions
    return {
        "transactions": num_transactions,
        "gas_per_tx": f"~{gas_per_tx} USDC",
        "total_saved": f"~${total_usdc:.2f} USDC",
        "sponsored_by": "InsightAgent Paymaster",
        "note": "Arc Testnet uses USDC for gas — no native token needed"
    }

if __name__ == "__main__":
    print("=" * 55)
    print("⛽ INSIGHTAGENT — Circle Paymaster")
    print("=" * 55)

    print("\n🔧 Getting paymaster config...")
    config = get_paymaster_info()
    print(f"   App ID: {config.get('data', {}).get('appId', 'N/A')}")

    print("\n💸 Simulating sponsored transaction...")
    tx = simulate_sponsored_tx("0x0ee2a024227cd3981e0f6b0923e86ef53ba8b943")
    for k, v in tx.items():
        print(f"   {k}: {v}")

    print("\n📊 Gas savings estimate (10 transactions):")
    savings = estimate_gas_savings(10)
    for k, v in savings.items():
        print(f"   {k}: {v}")
