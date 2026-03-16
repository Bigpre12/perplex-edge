import asyncio
from db.session import engine, Base
import models # imports all models so they register with Base

def init_db():
    print("Creating all tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("Done!")

if __name__ == "__main__":
    init_db()
