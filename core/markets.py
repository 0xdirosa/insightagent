import requests
import json

def get_markets(limit=30):
    url = "https://gamma-api.polymarket.com/markets"
    params = {"limit": limit, "active": "true", "closed": "false"}
    response = requests.get(url, params=params, timeout=10)
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
        liquidity = float(m.get('liquidity', 0))
        result.append({
            "id": m.get('id', ''),
            "question": m['question'],
            "yes": round(yes_price * 100, 1),
            "no": round((1 - yes_price) * 100, 1),
            "volume": round(volume, 0),
            "liquidity": round(liquidity, 0),
            "end_date": m.get('endDate', '')[:10] if m.get('endDate') else 'N/A'
        })
    return result

def filter_interesting(markets, min_volume=100000, min_yes=20, max_yes=80):
    interesting = [
        m for m in markets
        if m['volume'] > min_volume and min_yes <= m['yes'] <= max_yes
    ]
    interesting.sort(key=lambda x: x['volume'], reverse=True)
    return interesting

def get_signal(yes):
    if 45 <= yes <= 55:
        return "HIGH UNCERTAINTY"
    elif yes >= 65:
        return "LIKELY YES"
    elif yes <= 35:
        return "LIKELY NO"
    else:
        return "MONITOR"

def kelly_size(yes_pct, edge=0.05):
    yes = yes_pct / 100
    if yes >= 1:
        return 0
    return min(round((edge / (1 - yes)) * 100, 1), 10)
