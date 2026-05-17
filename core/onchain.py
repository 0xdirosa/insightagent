import requests
import os
import uuid
import hashlib
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY")
ENTITY_SECRET = os.getenv("CIRCLE_ENTITY_SECRET")
BASE_URL = "https://api.circle.com/v1/w3s"

def get_headers():
    return {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type": "application/json"
    }

def get_entity_public_key():
    """Get public key untuk encrypt entity secret"""
    try:
        response = requests.get(f"{BASE_URL}/config/entity/publicKey", headers=get_headers())
        data = response.json()
        return data.get("data", {}).get("publicKey")
    except Exception as e:
        print(f"Error getting public key: {e}")
        return None

def create_transfer(from_wallet_id, to_address, amount="1"):
    """Transfer USDC on-chain via Circle API"""
    try:
        idempotency_key = str(uuid.uuid4())
        
        payload = {
            "idempotencyKey": idempotency_key,
            "amounts": [amount],
            "destinationAddress": to_address,
            "feeLevel": "MEDIUM",
            "tokenId": "7adb2b7d-c9cd-4667-aef6-443c1f74d957",  # USDC on Arc Testnet
            "walletId": from_wallet_id
        }
        
        response = requests.post(
            f"{BASE_URL}/developer/transactions/transfer",
            headers=get_headers(),
            json=payload
        )
        
        data = response.json()
        print(f"Transfer response: {json.dumps(data, indent=2)}")
        return data
        
    except Exception as e:
        print(f"Transfer error: {e}")
        return {"error": str(e)}

def get_transaction_status(tx_id):
    """Cek status transaksi"""
    try:
        response = requests.get(
            f"{BASE_URL}/transactions/{tx_id}",
            headers=get_headers()
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def list_transactions(wallet_id):
    """List semua transaksi wallet"""
    try:
        response = requests.get(
            f"{BASE_URL}/transactions?walletIds={wallet_id}",
            headers=get_headers()
        )
        data = response.json()
        txs = data.get("data", {}).get("transactions", [])
        return txs
    except Exception as e:
        return []

if __name__ == "__main__":
    print("=" * 55)
    print("⛓️  INSIGHTAGENT — On-Chain Transaction Test")
    print("=" * 55)
    
    # Wallet 2 ID yang punya 20 USDC
    WALLET_ID = "de34ea85-bf6a-532b-8b4c-b6db8db6ab63"
    WALLET_ADDR = "0xb0c9fa9885b3e8ee5a130c1d5cdd20e6ec344c2a"
    
    print(f"\n📋 Listing recent transactions...")
    txs = list_transactions(WALLET_ID)
    if txs:
        for tx in txs[:3]:
            print(f"  TX: {tx.get('id','')[:16]}...")
            print(f"  Status: {tx.get('state','')}")
            print(f"  Amount: {tx.get('amounts',['?'])}")
            print()
    else:
        print("  No transactions found")
