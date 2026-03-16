import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from database import engine, Base
import models
from sqlalchemy import inspect

def verify():
    print(f"DB Path: {engine.url}")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns(table_name)]
        print(f"Table: {table_name}, Columns: {columns}")

if __name__ == "__main__":
    verify()
