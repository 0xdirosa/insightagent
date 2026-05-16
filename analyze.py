import requests
import json

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

def analyze_markets(markets):
    print("=" * 60)
    print("📊 INSIGHTAGENT — MARKET ANALYSIS")
    print("=" * 60)
    
    # Filter: volume > 100k dan yes antara 20-80%
    interesting = [
        m for m in markets
        if m['volume'] > 100000 and 20 <= m['yes'] <= 80
    ]
    
    # Sort by volume tertinggi
    interesting.sort(key=lambda x: x['volume'], reverse=True)
    
    print(f"\n🎯 TOP MARKETS TO WATCH ({len(interesting)} found)\n")
    
    for i, m in enumerate(interesting[:10], 1):
        yes = m['yes'] / 100
        
        # Kelly Criterion (simplified, edge = 5%)
        edge = 0.05
        kelly = edge / (1 - yes) if yes < 1 else 0
        kelly_pct = min(round(kelly * 100, 1), 10)  # max 10%
        
        # Confidence label
        if 45 <= m['yes'] <= 55:
            signal = "⚡ HIGH UNCERTAINTY"
        elif m['yes'] >= 70:
            signal = "📈 LIKELY YES"
        elif m['yes'] <= 30:
            signal = "📉 LIKELY NO"
        else:
            signal = "🔍 MONITOR"
        
        print(f"{i}. {m['question']}")
        print(f"   Yes: {m['yes']}% | No: {m['no']}% | Vol: ${m['volume']:,.0f}")
        print(f"   {signal} | Kelly size: {kelly_pct}% of bankroll")
        print()

if __name__ == "__main__":
    print("🔍 Fetching Polymarket data...")
    markets = get_markets()
    print(f"✅ Got {len(markets)} markets\n")
    analyze_markets(markets)
