import sys
import io
import os
import traceback

# Force UTF-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import uvicorn
import logging

# Ensure src is in the path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("../../server_boot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("boot")

if __name__ == "__main__":
    try:
        logger.info("Starting API import...")
        from main import app
        logger.info("API imported successfully!")
        
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Running uvicorn on port {port}")
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
        
    except Exception:
        logger.error("API Run failed!")
        with open("../../server_boot.log", "a") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
        sys.exit(1)
