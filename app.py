from flask import Flask, render_template, jsonify
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from core.markets import get_markets, filter_interesting, get_signal, kelly_size
from core.news import analyze
from core.wallet import get_wallets, get_balance, get_stats
from core.betting import load_transactions, place_bet, pick_best_market
from core.reasoning import load_log, generate_reasoning

app = Flask(__name__)

@app.route("/")
def index():
    markets = get_markets(limit=30)
    interesting = filter_interesting(markets)[:10]
    result = []
    for m in interesting:
        news = analyze(m['question'])
        signal = get_signal(m['yes'])
        kelly = kelly_size(m['yes'])
        result.append({**m, "news": news, "signal": signal, "kelly": kelly})
    wallets = get_wallets()
    for w in wallets:
        w['balance'] = get_balance(w['id']) if w.get('id') else "N/A"
    transactions = load_transactions()
    reasoning_log = load_log()[:5]
    stats = get_stats()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html",
        markets=result,
        wallets=wallets,
        transactions=transactions,
        reasoning_log=reasoning_log,
        stats=stats,
        timestamp=timestamp
    )

@app.route("/api/bet", methods=["POST"])
def api_bet():
    try:
        markets = get_markets(limit=50)
        interesting = filter_interesting(markets)
        best = pick_best_market(interesting)
        if not best:
            return jsonify({"error": "No suitable market"}), 400
        wallets = get_wallets()
        if not wallets:
            return jsonify({"error": "No wallet"}), 400
        news = analyze(best['question'])
        signal = get_signal(best['yes'])
        kelly = kelly_size(best['yes'])
        reasoning = generate_reasoning(best, news, signal, kelly)
        tx = place_bet(best, wallets[0], amount_usdc=1.0)
        return jsonify({"success": True, "tx": tx, "reasoning": reasoning})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/markets")
def api_markets():
    markets = get_markets(limit=30)
    return jsonify(filter_interesting(markets)[:10])

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/reasoning")
def api_reasoning():
    return jsonify(load_log()[:10])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
