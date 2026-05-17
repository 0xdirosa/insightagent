import os
from dotenv import load_dotenv
load_dotenv()

from core.markets import get_markets, filter_interesting, get_signal, kelly_size
from core.news import analyze
from core.wallet import get_wallets
from core.betting import pick_best_market, place_bet
from core.reasoning import generate_reasoning
from core.paymaster import simulate_sponsored_tx, estimate_gas_savings
from core.anomaly import detect_anomalies, load_price_history, get_anomaly_score

def run():
    print("=" * 65)
    print("🤖 INSIGHTAGENT — Autonomous Bet Engine v4")
    print("=" * 65)

    print("\n📊 Fetching markets...")
    markets = get_markets(limit=50)
    interesting = filter_interesting(markets)
    print(f"✅ Found {len(interesting)} interesting markets")

    print("\n🔍 Detecting anomalies...")
    anomalies = detect_anomalies(interesting)
    if anomalies:
        print(f"🚨 {len(anomalies)} anomalies detected!")
        for a in anomalies:
            print(f"   {a['direction']} {a['market'][:50]} ({a['change']:+.1f}%)")
    else:
        print("   No significant price movements detected")

    print("\n🎯 Picking best market...")
    # Prioritaskan market dengan anomali
    history = load_price_history()
    if anomalies:
        # Pilih anomali market dengan volume tertinggi
        anomaly_ids = {a['market_id'] for a in anomalies}
        anomaly_markets = [m for m in interesting if m.get('id', m['question'][:30]) in anomaly_ids]
        best = anomaly_markets[0] if anomaly_markets else pick_best_market(interesting)
        print(f"   🚨 Anomaly-driven selection!")
    else:
        best = pick_best_market(interesting)

    if not best:
        print("❌ No suitable market found")
        return

    signal = get_signal(best['yes'])
    kelly = kelly_size(best['yes'])
    anomaly_score = get_anomaly_score(best, history)

    print(f"✅ {best['question']}")
    print(f"   Yes: {best['yes']}% | No: {best['no']}% | Vol: ${best['volume']:,.0f}")
    if anomaly_score > 0:
        print(f"   ⚡ Anomaly score: {anomaly_score:.1f}% price movement")

    print("\n📰 Analyzing news...")
    news = analyze(best['question'])
    print(f"   Sentiment: {news['sentiment']} ({news['count']} articles)")

    print("\n🧠 Generating reasoning...")
    reasoning = generate_reasoning(best, news, signal, kelly)
    print(f"   Confidence: {reasoning['confidence']}")
    print(f"   Position: {reasoning['position']}")
    for i, r in enumerate(reasoning['reasons'], 1):
        print(f"   {i}. {r}")

    print("\n🔑 Getting wallet...")
    wallets = get_wallets()
    if not wallets:
        print("❌ No wallet found")
        return
    wallet = wallets[1] if len(wallets) > 1 else wallets[0]
    print(f"✅ {wallet['short']} ({wallet['chain']})")

    print("\n⛽ Sponsoring gas via Paymaster...")
    sponsored = simulate_sponsored_tx(wallet['address'], "BET_PLACEMENT")
    print(f"   Gas: {sponsored['gas_amount']} — SPONSORED ✅")

    print("\n💸 Placing bet (1 USDC)...")
    tx = place_bet(best, wallet, amount_usdc=1.0)

    print(f"\n✅ BET PLACED!")
    print(f"   ID:         {tx['id']}")
    print(f"   Position:   {tx['position']} @ {tx['price']}%")
    print(f"   Amount:     ${tx['amount_usdc']} USDC")
    print(f"   Return:     ${tx['potential_return']} USDC (+${tx['profit']})")
    print(f"   Gas:        {sponsored['gas_amount']} (SPONSORED)")
    print(f"   Confidence: {reasoning['confidence']}")
    print(f"   Chain:      {tx['chain']}")

if __name__ == "__main__":
    run()
