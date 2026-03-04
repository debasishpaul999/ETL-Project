import pandas as pd
from sqlalchemy import text
from utils.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()

Z_THRESHOLD = 2.5
MAD_THRESHOLD = 3.0
IQR_MULTIPLIER = 1.5
SCORE_PERCENTILE = 0.95
METRICS = ["revenue", "profit", "transactions", "profit_margin"]


def _safe_z_score(series: pd.Series) -> pd.Series:
    std = series.std()
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    return (series - series.mean()) / std

def _safe_mad_score(series: pd.Series) -> pd.Series:
    median = series.median()
    mad = (series - median).abs().median()
    if mad == 0 or pd.isna(mad):
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0 or pd.isna(iqr):
            return pd.Series(0.0, index=series.index)
        robust_std = iqr / 1.349
        return (series - median) / robust_std
    return 0.6745 * (series - median) / mad

def _iqr_outlier_flag(series: pd.Series, multiplier: float = IQR_MULTIPLIER) -> pd.Series:
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr == 0 or pd.isna(iqr):
        return pd.Series(False, index=series.index)
    
    lower = q1 - (multiplier * iqr)
    upper = q3 + (multiplier * iqr)
    return (series < lower) | (series > upper)

def detect_anomalies():

    logger.info("Running anomaly detection")

    engine = get_engine()
    query = """
        SELECT
            DATE(order_datetime) AS date,
            SUM(revenue) AS revenue,
            SUM(profit) AS profit,
            COUNT(*) AS transactions
        FROM sales_cleaned
        GROUP BY DATE(order_datetime)
        ORDER BY DATE(order_datetime)
    """

    daily = pd.read_sql(text(query), engine)

    if daily.empty:
        logger.warning("No records found for anomaly detection")
        daily = pd.DataFrame(columns=["date", *METRICS, "anomaly_score"])
        anomalies = daily.copy()
        return anomalies, daily

    daily["date"] = pd.to_datetime(daily["date"], errors="coerce").dt.date
    daily = daily.dropna(subset=["date"]).copy()

    daily["revenue"] = pd.to_numeric(daily["revenue"], errors="coerce").fillna(0.0)
    daily["profit"] = pd.to_numeric(daily["profit"], errors="coerce").fillna(0.0)
    daily["transactions"] = pd.to_numeric(daily["transactions"], errors="coerce").fillna(0.0)

    daily["profit_margin"] = (daily["profit"] / daily["revenue"]).where(daily["revenue"] != 0, 0.0)

    flag_columns = []
    for metric in METRICS:
        z_col = f"{metric}_z"
        mad_col = f"{metric}_mad"
        iqr_col = f"{metric}_iqr_anomaly"
        flag_col = f"{metric}_anomaly"

        daily[z_col] = _safe_z_score(daily[metric])
        daily[mad_col] = _safe_mad_score(daily[metric])
        daily[iqr_col] = _iqr_outlier_flag(daily[metric])
        daily[flag_col] = (
            (daily[z_col].abs() > Z_THRESHOLD)
            | (daily[mad_col].abs() > MAD_THRESHOLD)
            | daily[iqr_col]
        )
        flag_columns.append(flag_col)

    daily["anomaly_score"] = daily[[f"{metric}_z" for metric in METRICS]].abs().max(axis=1)
    daily["anomaly_reasons"] = daily.apply(
        lambda row: ", ".join(col.replace("_anomaly", "") for col in flag_columns if row[col]),
        axis=1,)

    percentile_cutoff = daily["anomaly_score"].quantile(SCORE_PERCENTILE)
    anomaly_mask = daily[flag_columns].any(axis=1) | (daily["anomaly_score"] >= percentile_cutoff)
    anomalies = daily[anomaly_mask].copy()

    if anomalies.empty and not daily.empty:
        anomalies = daily.nlargest(1, "anomaly_score").copy()

    logger.info(f"Anomalies detected: {len(anomalies)}")

    daily = daily.sort_values("date").reset_index(drop=True)
    anomalies = anomalies.sort_values("date").reset_index(drop=True)

    return anomalies, daily
