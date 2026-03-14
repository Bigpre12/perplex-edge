from database import engine
from sqlalchemy import inspect

def check():
    inspector = inspect(engine)
    print(inspector.get_table_names())

if __name__ == "__main__":
    check()
