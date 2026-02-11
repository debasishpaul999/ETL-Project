import pandas as pd
from sqlalchemy import text
from utils.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()

Z_THRESHOLD = 3


def z_score(series):
    return (series - series.mean()) / series.std()


def detect_anomalies():

    logger.info("Running anomaly detection")

    engine = get_engine()

    query = """
        SELECT order_datetime, revenue, profit, payment_type
        FROM sales_cleaned
    """

    df = pd.read_sql(text(query), engine)

    df["order_datetime"] = pd.to_datetime(df["order_datetime"])
    df["date"] = df["order_datetime"].dt.date

    # ---------------------------
    # DAILY METRICS
    # ---------------------------

    daily = df.groupby("date").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        transactions=("revenue", "count")
    )

    daily["profit_margin"] = daily["profit"] / daily["revenue"]

    # ---------------------------
    # Z-SCORE DETECTION
    # ---------------------------

    daily["rev_z"] = z_score(daily["revenue"])
    daily["profit_z"] = z_score(daily["profit"])
    daily["txn_z"] = z_score(daily["transactions"])
    daily["margin_z"] = z_score(daily["profit_margin"])

    anomaly_mask = (
        (abs(daily["rev_z"]) > Z_THRESHOLD) |
        (abs(daily["profit_z"]) > Z_THRESHOLD) |
        (abs(daily["txn_z"]) > Z_THRESHOLD) |
        (abs(daily["margin_z"]) > Z_THRESHOLD)
    )

    anomalies = daily[anomaly_mask]

    logger.info(f"Anomalies detected: {len(anomalies)}")

    daily = daily.reset_index()
    anomalies = anomalies.reset_index()

    return anomalies, daily
