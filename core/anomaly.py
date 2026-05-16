import json
import os
from datetime import datetime

ANOMALY_FILE = "anomaly_log.json"
PRICE_HISTORY_FILE = "price_history.json"

def load_price_history():
    try:
        with open(PRICE_HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_price_history(history):
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_anomalies():
    try:
        with open(ANOMALY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_anomaly(anomaly):
    anomalies = load_anomalies()
    anomalies.insert(0, anomaly)
    anomalies = anomalies[:50]
    with open(ANOMALY_FILE, "w") as f:
        json.dump(anomalies, f, indent=2)

def detect_anomalies(markets):
    history = load_price_history()
    anomalies = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for m in markets:
        market_id = m.get('id', m['question'][:30])
        current_yes = m['yes']

        if market_id in history:
            prev = history[market_id]
            prev_yes = prev.get('yes', current_yes)
            change = current_yes - prev_yes
            abs_change = abs(change)

            # Detect significant movement
            if abs_change >= 5:
                severity = "HIGH" if abs_change >= 10 else "MEDIUM"
                direction = "📈 SURGE" if change > 0 else "📉 DROP"

                anomaly = {
                    "timestamp": now,
                    "market": m['question'][:70],
                    "market_id": market_id,
                    "prev_yes": prev_yes,
                    "current_yes": current_yes,
                    "change": round(change, 1),
                    "abs_change": round(abs_change, 1),
                    "direction": direction,
                    "severity": severity,
                    "volume": m['volume'],
                    "signal": f"Price moved {change:+.1f}% — potential mispricing opportunity"
                }
                anomalies.append(anomaly)
                save_anomaly(anomaly)

        # Update history
        history[market_id] = {
            "yes": current_yes,
            "volume": m['volume'],
            "timestamp": now
        }

    save_price_history(history)
    return anomalies

def get_anomaly_score(market, history):
    """Score market berdasarkan anomali vs history"""
    market_id = market.get('id', market['question'][:30])
    if market_id not in history:
        return 0
    prev_yes = history[market_id].get('yes', market['yes'])
    return abs(market['yes'] - prev_yes)
