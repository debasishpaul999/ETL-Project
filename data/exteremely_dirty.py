import pandas as pd
import numpy as np

df = pd.read_csv("data/raw_coffee_sales.csv")

n = len(df)

# Convert numeric columns to object so we can corrupt them
df["price"] = df["price"].astype(object)
df["quantity"] = df["quantity"].astype(object)
df["cost"] = df["cost"].astype(object)

# 10% invalid dates
df.loc[np.random.choice(n, int(n * 0.1), replace=False), "order_datetime"] = "bad_date"

# 10% corrupt numeric fields
df.loc[np.random.choice(n, int(n * 0.1), replace=False), "price"] = "corrupt"
df.loc[np.random.choice(n, int(n * 0.1), replace=False), "quantity"] = "invalid"

# 10% null product names
df.loc[np.random.choice(n, int(n * 0.1), replace=False), "product_name"] = None

# 10% null payment types
df.loc[np.random.choice(n, int(n * 0.1), replace=False), "payment_type"] = None

# 5% duplicate order_id
dup_indices = np.random.choice(n, int(n * 0.05), replace=False)
df.loc[dup_indices, "order_id"] = df.loc[dup_indices, "order_id"].iloc[0]

# Garbage payment types
garbage_types = ["???", "bitcoin", "unknown", "NULL"]
df.loc[np.random.choice(n, int(n * 0.05), replace=False), "payment_type"] = np.random.choice(garbage_types)

# Negative quantities
df.loc[np.random.choice(n, int(n * 0.05), replace=False), "quantity"] = -5

df.to_csv("data/test_extremely_dirty.csv", index=False)

print("Extremely dirty dataset generated.")
