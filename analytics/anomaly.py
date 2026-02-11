import pandas as pd
import sqlite3
from config import DB_NAME, TABLE_NAME

def detect_anomalies():
    print("Running anomaly detection...")

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(f"""
        SELECT DATE(order_datetime) as date,
               SUM(revenue) as daily_revenue
        FROM {TABLE_NAME}
        GROUP BY DATE(order_datetime)
    """, conn)

    conn.close()

    mean = df["daily_revenue"].mean()
    std = df["daily_revenue"].std()

    df["rolling_mean"] = df["daily_revenue"].rolling(window=7).mean()
    df["rolling_std"] = df["daily_revenue"].rolling(window=7).std()

    df["rolling_z"] = (
        df["daily_revenue"] - df["rolling_mean"]
    ) / df["rolling_std"]

    anomalies = df[abs(df["rolling_z"]) > 2]

    print("Anomalies detected:")
    print(anomalies)

    return anomalies
