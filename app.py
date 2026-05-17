from flask import Flask, render_template, jsonify, request
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from core.markets import get_markets, filter_interesting, analyze_markets_parallel, get_category, get_category_emoji, get_signal, kelly_size
from core.news import analyze
from core.wallet import get_wallets, get_balance, get_stats, get_onchain_transactions
from core.betting import load_transactions, place_bet, pick_best_market
from core.reasoning import load_log, generate_reasoning
from core.anomaly import load_anomalies
from core.paymaster import simulate_sponsored_tx

app = Flask(__name__)

WALLET_2_ID = "de34ea85-bf6a-532b-8b4c-b6db8db6ab63"

@app.route("/")
def index():
    markets = get_markets(limit=50)
    interesting = filter_interesting(markets)
    for m in interesting:
        m['category'] = get_category(m['question'])
        m['cat_emoji'] = get_category_emoji(m['category'])
    top = interesting[:15]
    result = analyze_markets_parallel(top, analyze, max_workers=5)
    categories = {}
    for m in result:
        cat = m.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(m)
    wallets = get_wallets()
    for w in wallets:
        w['balance'] = get_balance(w['id']) if w.get('id') else "N/A"
    transactions = load_transactions()
    onchain_txs = get_onchain_transactions(WALLET_2_ID, limit=5)
    reasoning_log = load_log()[:5]
    anomalies = load_anomalies()[:3]
    stats = get_stats()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html",
        markets=result,
        categories=categories,
        wallets=wallets,
        transactions=transactions,
        onchain_txs=onchain_txs,
        reasoning_log=reasoning_log,
        anomalies=anomalies,
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
        wallet = wallets[1] if len(wallets) > 1 else wallets[0]
        news = analyze(best['question'])
        signal = get_signal(best['yes'])
        kelly = kelly_size(best['yes'])
        reasoning = generate_reasoning(best, news, signal, kelly)
        sponsored = simulate_sponsored_tx(wallet['address'], "BET_PLACEMENT")
        tx = place_bet(best, wallet, amount_usdc=1.0)
        return jsonify({"success": True, "tx": tx, "reasoning": reasoning, "gas": sponsored})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/markets")
def api_markets():
    cat = request.args.get('category', None)
    markets = get_markets(limit=50)
    interesting = filter_interesting(markets)
    for m in interesting:
        m['category'] = get_category(m['question'])
        m['cat_emoji'] = get_category_emoji(m['category'])
    if cat:
        interesting = [m for m in interesting if m['category'] == cat]
    return jsonify(interesting[:20])

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/reasoning")
def api_reasoning():
    return jsonify(load_log()[:10])

@app.route("/api/anomalies")
def api_anomalies():
    return jsonify(load_anomalies()[:10])

@app.route("/api/onchain")
def api_onchain():
    return jsonify(get_onchain_transactions(WALLET_2_ID, limit=10))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
