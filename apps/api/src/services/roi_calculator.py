import random

def calculate_user_roi(user_id: str):
    """
    Simulates the calculation of a user's Return on Investment.
    In a production system, this would query the 'picks' table, 
    filter by settled results, and calculate: (Total Profit / Total Staked) * 100.
    """
    # Mocking data for the Community Beta
    # Deterministic-ish random based on user_id to keep it consistent for one session
    random.seed(user_id)
    
    total_bets = random.randint(50, 500)
    win_rate = random.uniform(52.0, 58.5) # Standard sharp win rates
    
    # Calculate a realistic ROI based on win rate and average odds of -110 (1.91)
    # ROI = (Probability * Odds) - 1
    roi_percent = (win_rate / 100.0 * 1.91) - 1
    roi_percent *= 100 # Convert to percentage
    
    return {
        "user_id": user_id,
        "total_bets": total_bets,
        "win_rate": round(win_rate, 2),
        "verified_roi": round(roi_percent, 2),
        "sharp_rating": "ELITE" if roi_percent > 4 else "PRO" if roi_percent > 2 else "GRINDER"
    }
