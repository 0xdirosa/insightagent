import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_news(query, max_articles=5):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("status") != "ok":
        return []
    
    articles = []
    for a in data.get("articles", []):
        articles.append({
            "title": a["title"],
            "source": a["source"]["name"],
            "published": a["publishedAt"][:10],
            "description": a.get("description", "")
        })
    
    return articles

def news_sentiment(articles):
    """Simple keyword-based sentiment"""
    positive = ["win", "surge", "rally", "confirmed", "yes", "approved", "leads"]
    negative = ["lose", "drop", "crash", "denied", "no", "rejected", "trails"]
    
    score = 0
    for a in articles:
        text = (a["title"] + " " + a["description"]).lower()
        score += sum(1 for w in positive if w in text)
        score -= sum(1 for w in negative if w in text)
    
    if score > 2:
        return "🟢 BULLISH", score
    elif score < -2:
        return "🔴 BEARISH", score
    else:
        return "🟡 NEUTRAL", score

def analyze_market_with_news(market_question):
    # Ambil keywords dari pertanyaan
    keywords = market_question.replace("?", "").replace("Will", "").strip()
    keywords = " ".join(keywords.split()[:5])  # 5 kata pertama
    
    print(f"\n🔍 Searching news: '{keywords}'")
    articles = get_news(keywords)
    
    if not articles:
        print("   No news found")
        return "🟡 NEUTRAL", 0
    
    for a in articles:
        print(f"   📰 [{a['published']}] {a['title'][:70]}...")
    
    sentiment, score = news_sentiment(articles)
    print(f"   Sentiment: {sentiment} (score: {score})")
    
    return sentiment, score

if __name__ == "__main__":
    # Test dengan beberapa market
    test_markets = [
        "Will the Oklahoma City Thunder win the 2026 NBA Finals?",
        "Will bitcoin hit $1m before GTA VI?",
        "Will China invades Taiwan before GTA VI?"
    ]
    
    print("=" * 60)
    print("📡 INSIGHTAGENT — NEWS ANALYSIS")
    print("=" * 60)
    
    for market in test_markets:
        print(f"\n📊 {market}")
        analyze_market_with_news(market)
