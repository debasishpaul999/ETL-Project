import pandas as pd
from utils.logger import get_logger

logger = get_logger()


def transform_data(df):

    logger.info("Starting transformation")

    original_rows = len(df)

    # -----------------------------
    # Datetime parsing
    # -----------------------------
    df["order_datetime"] = pd.to_datetime(
        df["order_datetime"],
        errors="coerce"
    )

    invalid_dates = df["order_datetime"].isna().sum()

    if invalid_dates > 0:
        logger.warning(f"Dropping {invalid_dates} rows due to invalid dates")

    df = df.dropna(subset=["order_datetime"])

    # -----------------------------
    # Numeric coercion
    # -----------------------------
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    df = df.dropna(subset=["price", "cost", "quantity"])

    # Remove invalid business rows
    df = df[df["quantity"] > 0]

    # -----------------------------
    # Derived metrics
    # -----------------------------
    df["revenue"] = df["quantity"] * df["price"]
    df["total_cost"] = df["quantity"] * df["cost"]
    df["profit"] = df["revenue"] - df["total_cost"]

    df["is_weekend"] = df["order_datetime"].dt.weekday >= 5

    logger.info(f"Transformation complete. Rows: {len(df)} (from {original_rows})")

    return df
