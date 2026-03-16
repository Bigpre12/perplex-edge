from db.session import engine
from models.brain import Base, WhaleMove
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Initializing database tables...")
    try:
        # This will create all tables defined in Base (including WhaleMove)
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created/verified all tables.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
