from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import SessionLocal
from models.props import PropLine, PropOdds
from typing import Dict, Any, List

router = APIRouter(prefix="/best-book", tags=["best-book"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{player_name}/{prop_type}/{pick}")
def best_book(player_name: str, prop_type: str, pick: str, db: Session = Depends(get_db)):
    """Return which book has the best price for this prop/pick right now."""
    # Fetch active odds for this specific prop
    stmt = (
        select(PropLine, PropOdds)
        .join(PropOdds, PropLine.id == PropOdds.prop_line_id)
        .where(
            PropLine.player_name == player_name,
            PropLine.stat_type == prop_type,
            PropLine.is_active == True
        )
    )
    
    results = db.execute(stmt).all()
    if not results:
        return {"best_book": None, "best_price": None, "all_books": []}

    # Determine best price based on the 'pick' (over or under)
    # Higher price (more positive / less negative) is always better for the bettor
    book_prices = []
    for prop, odds in results:
        price = odds.over_odds if pick.lower() == "over" else odds.under_odds
        book_prices.append({"book": odds.sportsbook, "price": price})

    if not book_prices:
        return {"best_book": None, "best_price": None, "all_books": []}

    # Sort by price descending (best first)
    sorted_books = sorted(book_prices, key=lambda x: x["price"], reverse=True)
    best = sorted_books[0]

    return {
        "best_book": best["book"],
        "best_price": best["price"],
        "all_books": sorted_books[:5] # Return top 5 options
    }
