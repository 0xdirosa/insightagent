import json
from datetime import datetime

REASONING_FILE = "reasoning_log.json"

def load_log():
    try:
        with open(REASONING_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_log(entry):
    log = load_log()
    log.insert(0, entry)
    log = log[:50]
    with open(REASONING_FILE, "w") as f:
        json.dump(log, f, indent=2)

def generate_reasoning(market, news, signal, kelly):
    reasons = []
    confidence = "MEDIUM"

    # Volume analysis
    if market['volume'] > 10000000:
        reasons.append(f"High liquidity market (${market['volume']:,.0f} volume) — low slippage risk")
        confidence = "HIGH"
    elif market['volume'] > 1000000:
        reasons.append(f"Good liquidity (${market['volume']:,.0f} volume)")
    else:
        reasons.append(f"Lower liquidity (${market['volume']:,.0f}) — higher risk")
        confidence = "LOW"

    # Price analysis
    yes = market['yes']
    if 45 <= yes <= 55:
        reasons.append(f"Market is near 50/50 ({yes}% Yes) — high uncertainty, potential mispricing")
    elif yes >= 65:
        reasons.append(f"Strong Yes probability ({yes}%) — market favors YES outcome")
    elif yes <= 35:
        reasons.append(f"Strong No probability ({market['no']}%) — market favors NO outcome")
    else:
        reasons.append(f"Moderate probability ({yes}% Yes) — monitor for movement")

    # News sentiment
    score = news.get('score', 0)
    count = news.get('count', 0)
    sentiment = news.get('sentiment', '🟡 NEUTRAL')

    if count == 0:
        reasons.append("No recent news found — price may not reflect latest information")
    elif '🟢' in sentiment:
        reasons.append(f"Bullish news sentiment (score: +{score}, {count} articles) — supports YES position")
    elif '🔴' in sentiment:
        reasons.append(f"Bearish news sentiment (score: {score}, {count} articles) — supports NO position")
    else:
        reasons.append(f"Neutral news sentiment ({count} articles) — no strong directional signal")

    # Kelly sizing
    reasons.append(f"Kelly Criterion recommends {kelly}% bankroll allocation — {'conservative' if kelly <= 5 else 'moderate'} position size")

    # Signal
    if signal == "HIGH UNCERTAINTY":
        reasons.append("HIGH UNCERTAINTY signal — contrarian opportunity if news diverges from price")
    elif signal == "LIKELY NO":
        reasons.append("LIKELY NO signal — market consensus leans bearish")
    elif signal == "LIKELY YES":
        reasons.append("LIKELY YES signal — market consensus leans bullish")

    # Determine position
    if yes >= 50:
        position = "YES"
        edge = f"Buying YES at {yes}¢ — implied probability may be undervalued"
    else:
        position = "NO"
        edge = f"Buying NO at {market['no']}¢ — implied probability may be overvalued"

    reasons.append(edge)

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market": market['question'][:70],
        "signal": signal,
        "position": position,
        "confidence": confidence,
        "yes_price": yes,
        "no_price": market['no'],
        "volume": market['volume'],
        "sentiment": sentiment,
        "kelly": kelly,
        "reasons": reasons,
        "news_count": count
    }

    save_log(entry)
    return entry
