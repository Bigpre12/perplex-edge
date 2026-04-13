import os
from sqlalchemy import create_engine, text

def main():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not set")
        return
    # Use standard psycopg2 for synchronous connection
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    with engine.connect() as conn:
        for t in ['props_live', 'props_history', 'unified_odds', 'ev_signals', 'steam_events', 'whale_moves']:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {t}"))
                print(f"{t}: {res.scalar()}")
            except Exception as e:
                print(f"{t}: Error {e}")

if __name__ == "__main__":
    main()
