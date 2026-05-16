import requests
import os

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

POSITIVE = ["win", "surge", "rally", "confirmed", "approved", "leads", "ahead", "likely", "bullish", "beats"]
NEGATIVE = ["lose", "drop", "crash", "denied", "rejected", "trails", "unlikely", "fail", "bearish", "miss"]

def clean_query(question):
    stopwords = ["will", "the", "a", "an", "before", "after", "by", "in",
                 "on", "to", "be", "is", "are", "was", "win", "lose", "?",
                 "new", "for", "its", "this", "that"]
    words = question.lower().replace("?", "").split()
    cleaned = [w for w in words if w not in stopwords]
    return " ".join(cleaned[:4])

def get_news(query, max_articles=5):
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": max_articles
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("status") != "ok":
            return []
        return data.get("articles", [])
    except:
        return []

def sentiment_score(articles):
    score = 0
    for a in articles:
        text = (a.get("title", "") + " " + a.get("description", "")).lower()
        score += sum(1 for w in POSITIVE if w in text)
        score -= sum(1 for w in NEGATIVE if w in text)
    return score

def sentiment_label(score):
    if score > 2:
        return "🟢 BULLISH"
    elif score < -2:
        return "🔴 BEARISH"
    else:
        return "🟡 NEUTRAL"

def analyze(question):
    query = clean_query(question)
    articles = get_news(query)
    score = sentiment_score(articles)
    label = sentiment_label(score)
    headlines = [a.get("title", "")[:80] for a in articles[:3]]
    return {
        "sentiment": label,
        "score": score,
        "count": len(articles),
        "headlines": headlines
    }
