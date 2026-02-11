import pandas as pd
import sqlite3
from config import DATA_SOURCE_TYPE, DATA_CONFIG

def extract_from_csv(config):
    print("Extracting from CSV...")
    return pd.read_csv(config["path"])

def extract_from_json(config):
    print("Extracting from JSON...")
    return pd.read_json(config["path"])

def extract_from_database(config):
    print("Extracting from Database...")
    conn = sqlite3.connect(config["db_name"])
    query = f"SELECT * FROM {config['table_name']}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def extract_data():
    print(f"Starting extraction from {DATA_SOURCE_TYPE}...")

    if DATA_SOURCE_TYPE == "csv":
        df = extract_from_csv(DATA_CONFIG["csv"])
    elif DATA_SOURCE_TYPE == "json":
        df = extract_from_json(DATA_CONFIG["json"])
    elif DATA_SOURCE_TYPE == "database":
        df = extract_from_database(DATA_CONFIG["database"])
    else:
        raise ValueError("Unsupported data source type")

    print(f"Extraction complete. Rows: {len(df)}")
    return df
