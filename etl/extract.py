import pandas as pd
from config import DATA_SOURCE_TYPE, DATA_CONFIG
from utils.logger import get_logger

logger = get_logger()

def extract_data():
    logger.info(f"Starting extraction from {DATA_SOURCE_TYPE}")

    if DATA_SOURCE_TYPE == "csv":
        df = pd.read_csv(DATA_CONFIG["csv"]["path"])
    else:
        raise ValueError("Unsupported source type")

    logger.info(f"Extraction complete. Rows: {len(df)}")
    return df
