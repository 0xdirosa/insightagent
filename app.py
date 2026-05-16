from flask import Flask, render_template
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY")
BASE_URL = "https://api.circle.com/v1/w3s"

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

def clean_query(question):
    stopwords = ["will", "the", "a", "an", "before", "after", "by", "in",
                 "on", "to", "be", "is", "are", "was", "win", "lose", "?"]
    words = question.lower().replace("?", "").split()
    cleaned = [w for w in words if w not in stopwords]
    return " ".join(cleaned[:4])

def get_news(query):
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        return data.get("articles", [])
    except:
        return []

def news_sentiment(articles):
    positive = ["win", "surge", "rally", "confirmed", "approved", "leads", "ahead", "likely"]
    negative = ["lose", "drop", "crash", "denied", "rejected", "trails", "unlikely", "fail"]
    score = 0
    for a in articles:
        text = (a.get("title","") + " " + a.get("description","")).lower()
        score += sum(1 for w in positive if w in text)
        score -= sum(1 for w in negative if w in text)
    if score > 2:
        return "🟢 BULLISH"
    elif score < -2:
        return "🔴 BEARISH"
    else:
        return "🟡 NEUTRAL"

def get_wallets():
    try:
        headers = {
            "Authorization": f"Bearer {CIRCLE_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/wallets", headers=headers, timeout=5)
        data = response.json()
        wallets = data.get("data", {}).get("wallets", [])
        return [{"address": w.get("address","N/A"), "chain": w.get("blockchain","N/A"), "state": w.get("state","N/A")} for w in wallets]
    except:
        return []

@app.route("/")
def index():
    markets = get_markets()
    interesting = [m for m in markets if m['volume'] > 100000 and 20 <= m['yes'] <= 80]
    interesting.sort(key=lambda x: x['volume'], reverse=True)
    
    result = []
    for m in interesting[:10]:
        query = clean_query(m['question'])
        articles = get_news(query)
        sentiment = news_sentiment(articles) if articles else "🟡 NEUTRAL"
        yes = m['yes'] / 100
        kelly = min(round((0.05 / (1 - yes)) * 100, 1), 10) if yes < 1 else 0
        if 45 <= m['yes'] <= 55:
            signal = "HIGH UNCERTAINTY"
        elif m['yes'] >= 65:
            signal = "LIKELY YES"
        elif m['yes'] <= 35:
            signal = "LIKELY NO"
        else:
            signal = "MONITOR"
        result.append({**m, "sentiment": sentiment, "signal": signal, "kelly": kelly})
    
    wallets = get_wallets()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template("index.html", markets=result, wallets=wallets, timestamp=timestamp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
