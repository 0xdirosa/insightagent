import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

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
    """Bersihkan pertanyaan jadi search query yang relevan"""
    stopwords = ["will", "the", "a", "an", "before", "after", "by", "in", 
                 "on", "to", "be", "is", "are", "was", "win", "lose", "?"]
    words = question.lower().replace("?", "").split()
    cleaned = [w for w in words if w not in stopwords]
    return " ".join(cleaned[:4])

def get_news(query):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("status") != "ok":
        return []
    return data.get("articles", [])

def news_sentiment(articles):
    positive = ["win", "surge", "rally", "confirmed", "approved", "leads", "ahead", "likely"]
    negative = ["lose", "drop", "crash", "denied", "rejected", "trails", "unlikely", "fail"]
    score = 0
    for a in articles:
        text = (a.get("title","") + " " + a.get("description","")).lower()
        score += sum(1 for w in positive if w in text)
        score -= sum(1 for w in negative if w in text)
    if score > 2:
        return "🟢 BULLISH", score
    elif score < -2:
        return "🔴 BEARISH", score
    else:
        return "🟡 NEUTRAL", score

def run_agent():
    print("=" * 65)
    print("🏛️  INSIGHTAGENT — Polymarket Intelligence")
    print("=" * 65)
    
    print("\n🔍 Fetching markets...")
    markets = get_markets()
    
    # Filter interesting markets
    interesting = [
        m for m in markets
        if m['volume'] > 100000 and 20 <= m['yes'] <= 80
    ]
    interesting.sort(key=lambda x: x['volume'], reverse=True)
    interesting = interesting[:8]
    
    print(f"✅ Analyzing top {len(interesting)} markets\n")
    print("-" * 65)
    
    recommendations = []
    
    for m in interesting:
        query = clean_query(m['question'])
        articles = get_news(query)
        sentiment, score = news_sentiment(articles) if articles else ("🟡 NEUTRAL", 0)
        
        # Kelly sizing
        yes = m['yes'] / 100
        kelly = min(round((0.05 / (1 - yes)) * 100, 1), 10) if yes < 1 else 0
        
        # Combined signal
        if 45 <= m['yes'] <= 55:
            market_signal = "HIGH UNCERTAINTY"
        elif m['yes'] >= 65:
            market_signal = "LIKELY YES"
        elif m['yes'] <= 35:
            market_signal = "LIKELY NO"
        else:
            market_signal = "MONITOR"
        
        recommendations.append({
            **m,
            "sentiment": sentiment,
            "news_score": score,
            "signal": market_signal,
            "kelly": kelly,
            "news_count": len(articles)
        })
    
    # Display
    for i, r in enumerate(recommendations, 1):
        print(f"\n{i}. {r['question']}")
        print(f"   📊 Yes: {r['yes']}% | No: {r['no']}% | Vol: ${r['volume']:,.0f}")
        print(f"   📰 News: {r['sentiment']} ({r['news_count']} articles)")
        print(f"   🎯 Signal: {r['signal']} | Kelly: {r['kelly']}% bankroll")
    
    print("\n" + "=" * 65)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    run_agent()
