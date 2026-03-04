import logging
import os
from datetime import datetime


RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

def get_logger():
    logger = logging.getLogger("ETL")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler (same format for easier cross-reading with file logs)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handlers
        os.makedirs("logs", exist_ok=True)
        
        # Latest run (stable path)
        latest_file_handler = logging.FileHandler("logs/etl.log")
        latest_file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(latest_file_handler)

        logger.info("=" * 70)

    return logger
