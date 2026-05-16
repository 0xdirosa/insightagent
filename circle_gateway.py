import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY")
BASE_URL = "https://api.circle.com/v1/w3s"

headers = {
    "Authorization": f"Bearer {CIRCLE_API_KEY}",
    "Content-Type": "application/json"
}

def get_wallets():
    response = requests.get(f"{BASE_URL}/wallets", headers=headers)
    data = response.json()
    return data.get("data", {}).get("wallets", [])

def get_wallet_balance(wallet_id):
    url = f"{BASE_URL}/wallets/{wallet_id}/balances"
    response = requests.get(url, headers=headers)
    data = response.json()
    print(f"Balance response: {data}")
    return data

def simulate_gateway_deposit(wallet, amount="10"):
    """Simulasi deposit USDC ke wallet via Circle Gateway"""
    tx = {
        "id": str(uuid.uuid4())[:8],
        "to": wallet['address'][:10] + "..." + wallet['address'][-6:],
        "amount": amount,
        "token": "USDC",
        "chain": "ARC-TESTNET",
        "status": "SIMULATED",
        "type": "GATEWAY_DEPOSIT"
    }
    print(f"\n✅ Gateway Deposit Simulated!")
    print(f"   To:     {tx['to']}")
    print(f"   Amount: {tx['amount']} USDC")
    print(f"   Chain:  {tx['chain']}")
    print(f"   TX ID:  {tx['id']}")
    return tx

if __name__ == "__main__":
    print("=" * 55)
    print("🌐 INSIGHTAGENT — Circle Gateway")
    print("=" * 55)

    print("\n🔑 Getting wallet...")
    wallets = get_wallets()
    
    if wallets:
        wallet = wallets[0]
        print(f"✅ Wallet: {wallet['address'][:10]}...{wallet['address'][-6:]}")
        
        print(f"\n💰 Checking balance...")
        get_wallet_balance(wallet['id'])
        
        print(f"\n🔄 Simulating Gateway deposit...")
        simulate_gateway_deposit(wallet, "10")
    else:
        print("❌ No wallet found")
