import os
import uuid
import hashlib
import hmac
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("CIRCLE_API_KEY")
ENTITY_SECRET = os.getenv("CIRCLE_ENTITY_SECRET")

BASE_URL = "https://api.circle.com/v1/w3s"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_entity_config():
    """Cek konfigurasi entity"""
    url = f"{BASE_URL}/config/entity"
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(response.json())
    return response.json()

def create_wallet_set(name="InsightAgent Wallets"):
    """Buat wallet set baru"""
    url = f"{BASE_URL}/developer/walletSets"
    payload = {
        "idempotencyKey": str(uuid.uuid4()),
        "name": name
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(response.json())
    return response.json()

def create_wallet(wallet_set_id, blockchain="ARB-SEPOLIA"):
    """Buat wallet baru di wallet set"""
    url = f"{BASE_URL}/developer/wallets"
    payload = {
        "idempotencyKey": str(uuid.uuid4()),
        "walletSetId": wallet_set_id,
        "blockchains": [blockchain],
        "count": 1
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(response.json())
    return response.json()

def list_wallets():
    """List semua wallets"""
    url = f"{BASE_URL}/wallets"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    wallets = data.get("data", {}).get("wallets", [])
    if not wallets:
        print("No wallets found")
        return []
    
    for w in wallets:
        print(f"🔑 ID: {w['id']}")
        print(f"   Address: {w.get('address', 'N/A')}")
        print(f"   Chain: {w.get('blockchain', 'N/A')}")
        print(f"   State: {w.get('state', 'N/A')}")
        print()
    
    return wallets

if __name__ == "__main__":
    print("=" * 55)
    print("💳 INSIGHTAGENT — Circle Wallet Setup")
    print("=" * 55)
    
    print("\n1️⃣ Checking entity config...")
    get_entity_config()
    
    print("\n2️⃣ Listing existing wallets...")
    list_wallets()
