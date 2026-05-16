import requests
import json

def get_polymarket_markets():
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "limit": 20,
        "active": "true",
        "closed": "false"
    }
    
    response = requests.get(url, params=params)
    markets = response.json()
    
    for m in markets:
        # Parse harga
        prices = m.get('outcomePrices', '[]')
        if isinstance(prices, str):
            try:
                prices = json.loads(prices)
            except:
                prices = []
        
        yes_price = float(prices[0]) * 100 if prices else 0
        no_price = float(prices[1]) * 100 if len(prices) > 1 else 0
        volume = float(m.get('volume', 0))
        
        print(f"📊 {m['question']}")
        print(f"   Yes: {yes_price:.1f}% | No: {no_price:.1f}% | Volume: ${volume:,.0f}")
        print()

if __name__ == "__main__":
    get_polymarket_markets()
