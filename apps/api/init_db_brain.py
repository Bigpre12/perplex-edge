import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from database import engine, Base
import models.brain

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
