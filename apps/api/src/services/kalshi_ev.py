import logging
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

def american_to_implied_prob(odds: int) -> float:
    """Convert American odds to implied probability (0-1)"""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

def kalshi_to_implied_prob(yes_price: int) -> float:
    """Convert Kalshi YES price (0-100 cents) to implied probability (0-1)"""
    return yes_price / 100.0

def calculate_kalshi_ev(kalshi_yes_price: int, sportsbook_odds: int, prop_label: str) -> Dict[str, Any]:
    """
    Calculate Expected Value (EV) by comparing Kalshi probability with Sportsbook implied probability.
    
    recommendation = "BUY YES" if edge > 3%, "BUY NO" if edge < -3%, else "No Edge"
    """
    kalshi_prob = kalshi_to_implied_prob(kalshi_yes_price)
    book_prob = american_to_implied_prob(sportsbook_odds)
    
    # Edge is the difference in probabilities
    edge = kalshi_prob - book_prob
    
    recommendation = "No Edge"
    if edge > 0.03:
        recommendation = "BUY YES"
    elif edge < -0.03:
        recommendation = "BUY NO"
        
    return {
        "prop": prop_label,
        "kalshi_prob": round(kalshi_prob * 100, 2),
        "book_prob": round(book_prob * 100, 2),
        "edge": round(edge * 100, 2),
        "recommendation": recommendation
    }

def fuzzy_match_player(name1: str, name2: str) -> float:
    """Calculate fuzzy match score between two player names"""
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

def scan_all_ev_signals(markets: List[Dict[str, Any]], odds_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Match Kalshi markets to sportsbook props by fuzzy player name matching.
    Returns all signals sorted by edge descending.
    """
    signals = []
    
    for market in markets:
        # Expected market structure: { "ticker": "...", "title": "Will LeBron James score over 24.5 points?", "yes_bid": 54, ... }
        ticker = market.get("ticker", "")
        title = market.get("title", "").lower()
        yes_price = market.get("yes_bid") or market.get("last_price")
        
        if not yes_price:
            continue
            
        for book_prop in odds_data:
            # Expected book_prop: { "player": "LeBron James", "market": "points", "line": 24.5, "odds": -110, "bookmaker": "DraftKings" }
            player_name = book_prop.get("player", "")
            if not player_name:
                continue
                
            match_score = fuzzy_match_player(player_name, title)
            
            # If match exceeds threshold, calculate EV
            if match_score > 0.7: # Threshold for fuzzy match
                ev_result = calculate_kalshi_ev(yes_price, book_prop.get("odds", 0), book_prop.get("market", ""))
                
                signals.append({
                    "ticker": ticker,
                    "player_name": player_name,
                    "prop_label": f"{book_prop.get('market')} {book_prop.get('line')}",
                    "sport": market.get("series_ticker", ""),
                    "kalshi_prob": ev_result["kalshi_prob"],
                    "book_prob": ev_result["book_prob"],
                    "edge": ev_result["edge"],
                    "recommendation": ev_result["recommendation"],
                    "book_name": book_prop.get("bookmaker", "Unknown")
                })
                
    # Sort signals by absolute edge descending
    return sorted(signals, key=lambda x: abs(x["edge"]), reverse=True)
