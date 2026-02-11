import os
from sqlalchemy.engine import URL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_SOURCE_TYPE = "csv"

DATA_CONFIG = {
    "csv": {
        "path": os.path.join(BASE_DIR, "data", "raw_coffee_sales.csv")
    }
}

DATABASE_CONFIG = {
    "db_type": "mysql",
    "host": "127.0.0.1",
    "user": "debasish",
    "password": "debasish@999",
    "database": "coffee_etl_db"
}

TABLE_NAME = "sales_cleaned"

ANOMALY_CONFIG = {
    "window_size": 7,
    "z_threshold": 2
}
