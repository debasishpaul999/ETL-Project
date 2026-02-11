import pandas as pd
import numpy as np

df = pd.read_csv("data/raw_coffee_sales.csv")

n = len(df)

# 1% null product_name
df.loc[np.random.choice(n, int(n * 0.01), replace=False), "product_name"] = None

# 1% negative price (will impact revenue later)
df.loc[np.random.choice(n, int(n * 0.01), replace=False), "price"] *= -1

# 1% missing payment_type
df.loc[np.random.choice(n, int(n * 0.01), replace=False), "payment_type"] = None

# 1% zero quantity
df.loc[np.random.choice(n, int(n * 0.01), replace=False), "quantity"] = 0

# One invalid date
df.loc[0, "order_datetime"] = "invalid_date"

df.to_csv("data/test_slightly_dirty.csv", index=False)

print("Slightly dirty dataset generated successfully.")

# --------------------------------------
# BUSINESS ANOMALIES
# --------------------------------------

# Revenue spike day (choose one date)
spike_date = "2024-06-15"
df.loc[df["order_datetime"].str.contains("2024-06-15", na=False), "price"] = 5000

# Revenue crash day
crash_date = "2024-09-01"
df.loc[df["order_datetime"].str.contains("2024-09-01", na=False), "price"] = 5

# Negative profit injection
df.loc[np.random.choice(n, int(n * 0.02), replace=False), "cost"] = 10000

# Payment fraud pattern
fraud_date = "2024-07-20"
df.loc[df["order_datetime"].str.contains(fraud_date, na=False), "payment_type"] = "bitcoin"
