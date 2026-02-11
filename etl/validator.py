def validate_data(df):
    print("Running data validation...")

    if df["order_id"].isnull().any():
        raise ValueError("Null values found in order_id")

    if (df["quantity"] <= 0).any():
        raise ValueError("Invalid quantity values detected")

    if (df["revenue"] < 0).any():
        raise ValueError("Negative revenue detected")

    print("Validation passed.")
    return df
