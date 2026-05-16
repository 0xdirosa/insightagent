import os
from dotenv import load_dotenv
load_dotenv()

from core.markets import get_markets, filter_interesting, get_signal, kelly_size
from core.news import analyze
from core.wallet import get_wallets
from core.betting import pick_best_market, place_bet

def run():
    print("=" * 60)
    print("🤖 INSIGHTAGENT — Auto Bet Engine")
    print("=" * 60)

    print("\n📊 Fetching markets...")
    markets = get_markets(limit=50)
    interesting = filter_interesting(markets)
    print(f"✅ Found {len(interesting)} interesting markets")

    print("\n🎯 Picking best market...")
    best = pick_best_market(interesting)
    if not best:
        print("❌ No suitable market found")
        return

    print(f"✅ {best['question']}")
    print(f"   Yes: {best['yes']}% | No: {best['no']}% | Vol: ${best['volume']:,.0f}")

    print("\n📰 Analyzing news...")
    news = analyze(best['question'])
    print(f"   Sentiment: {news['sentiment']} ({news['count']} articles)")

    print("\n🔑 Getting wallet...")
    wallets = get_wallets()
    if not wallets:
        print("❌ No wallet found")
        return
    wallet = wallets[0]
    print(f"✅ {wallet['short']} ({wallet['chain']})")

    print("\n💸 Placing bet (1 USDC)...")
    tx = place_bet(best, wallet, amount_usdc=1.0)

    print(f"\n✅ BET PLACED!")
    print(f"   ID:       {tx['id']}")
    print(f"   Position: {tx['position']} @ {tx['price']}%")
    print(f"   Amount:   ${tx['amount_usdc']} USDC")
    print(f"   Return:   ${tx['potential_return']} USDC (+${tx['profit']})")
    print(f"   Chain:    {tx['chain']}")
    print(f"   News:     {news['sentiment']}")

if __name__ == "__main__":
    run()
