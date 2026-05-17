import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def analyze_market_parallel(market, analyze_fn):
    """Analyze single market — untuk parallel execution"""
    from core.markets import get_signal, kelly_size
    news = analyze_fn(market['question'])
    signal = get_signal(market['yes'])
    kelly = kelly_size(market['yes'])
    return {**market, "news": news, "signal": signal, "kelly": kelly}

def analyze_markets_parallel(markets, analyze_fn, max_workers=5):
    """Parallel news analysis untuk semua markets"""
    results = [None] * len(markets)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(analyze_market_parallel, m, analyze_fn): i
            for i, m in enumerate(markets)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except:
                results[idx] = {**markets[idx], "news": {"sentiment": "🟡 NEUTRAL", "score": 0, "count": 0, "headlines": []}, "signal": get_signal(markets[idx]['yes']), "kelly": kelly_size(markets[idx]['yes'])}
    return [r for r in results if r]

CATEGORIES = {
    "crypto": ["bitcoin", "btc", "eth", "ethereum", "crypto", "usdc", "solana", "token", "blockchain", "web3", "defi", "nft", "megaeth"],
    "sports": ["nba", "nhl", "nfl", "mlb", "finals", "cup", "champion", "spurs", "thunder", "cavaliers", "avalanche", "hurricanes"],
    "politics": ["trump", "president", "election", "senate", "congress", "vote", "democrat", "republican", "biden", "war", "china", "taiwan"],
    "entertainment": ["gta", "rihanna", "carti", "album", "movie", "music", "celebrity", "kardashian"],
    "world": ["jesus", "christ", "religious", "invasion", "nuclear", "conflict", "peace"]
}

def get_category(question):
    q = question.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in q for kw in keywords):
            return cat
    return "other"

def get_category_emoji(cat):
    emojis = {
        "crypto": "₿",
        "sports": "🏆",
        "politics": "🏛️",
        "entertainment": "🎬",
        "world": "🌍",
        "other": "📊"
    }
    return emojis.get(cat, "📊")
