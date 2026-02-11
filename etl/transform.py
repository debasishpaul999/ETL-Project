import pandas as pd

def transform_data(df):
    print("Starting transformation...")

    df["order_datetime"] = pd.to_datetime(df["order_datetime"])

    df = df.drop_duplicates(subset=["order_id"])

    df = df[df["quantity"] > 0]

    df["revenue"] = df["quantity"] * df["price"]
    df["total_cost"] = df["quantity"] * df["cost"]
    df["profit"] = df["revenue"] - df["total_cost"]

    print("Transformation complete.")
    return df
