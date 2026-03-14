import logging
from typing import List, Dict, Any
from services.kalshi_ev import american_to_implied_prob, kalshi_to_implied_prob

logger = logging.getLogger(__name__)

def detect_arb_opportunities(kalshi_markets: List[Dict[str, Any]], sportsbook_odds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect arbitrage opportunities where:
    kalshi_yes_price + best_book_no_implied < 100 (guaranteed profit exists)
    """
    opportunities = []
    
    for market in kalshi_markets:
        ticker = market.get("ticker", "")
        # Kalshi YES price in cents (0-100)
        kalshi_yes = market.get("yes_ask") # We buy at the ask
        if not kalshi_yes:
            continue
            
        for book_prop in sportsbook_odds:
            # We need the "NO" side from the sportsbook to arb against Kalshi "YES"
            # Or "UNDER" vs "YES" (Over)
            if book_prop.get("side") not in ["no", "under"]:
                continue
                
            book_no_prob = american_to_implied_prob(book_prop.get("odds", 0)) * 100
            
            # Arb condition: Sum of implied probabilities < 100%
            # In cents: kalshi_yes + book_no_prob < 100
            if kalshi_yes + book_no_prob < 98: # 2% buffer for execution risk
                profit_margin = 100 - (kalshi_yes + book_no_prob)
                
                opportunities.append({
                    "ticker": ticker,
                    "player_name": book_prop.get("player"),
                    "market": book_prop.get("market"),
                    "kalshi_yes": kalshi_yes,
                    "book_no_implied": round(book_no_prob, 2),
                    "profit_margin": round(profit_margin, 2),
                    "bookmaker": book_prop.get("bookmaker")
                })
                
    return sorted(opportunities, key=lambda x: x["profit_margin"], reverse=True)

def calculate_arb_stakes(bankroll: float, profit_margin: float) -> Dict[str, float]:
    """
    Calculate optimal YES and NO stake sizes using Kelly-adjacent sizing.
    Simple proportional sizing for now.
    """
    # Assuming we want to risk a small percentage of bankroll based on profit margin
    risk_pct = min(profit_margin / 100, 0.05) # Cap at 5% of bankroll
    total_to_risk = bankroll * risk_pct
    
    # In a perfect arb, stakes are proportional to the other side's implied probability
    # to guarantee same payout regardless of outcome.
    # We'll return recommended dollar amounts.
    return {
        "yes_stake": round(total_to_risk * 0.5, 2),
        "no_stake": round(total_to_risk * 0.5, 2)
    }
