import matplotlib.pyplot as plt
from utils.logger import get_logger
import os

logger = get_logger()

def generate_dashboard(daily_df, anomalies):

    logger.info("Generating dashboard image")

    os.makedirs("reports", exist_ok=True)

    plt.figure(figsize=(12, 6))

    # Plot revenue
    plt.plot(daily_df["date"], daily_df["revenue"], label="Daily Revenue")

    # Highlight anomalies
    if not anomalies.empty:
        plt.scatter(
            anomalies["date"],
            anomalies["revenue"],
            color="red",
            label="Anomalies",
            zorder=5
        )

    plt.title("Daily Revenue with Anomaly Detection")
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.legend()
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig("reports/dashboard_latest.png")
    plt.close()

    logger.info("Dashboard saved to: reports/dashboard_latest.png")
