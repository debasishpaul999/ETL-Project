import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ===============================
# CONFIGURE YOUR TEST TYPE HERE
# ===============================

TEST_TYPE = "missing_column"
# Options:
# "extra_column"
# "missing_column"
# "renamed_column"
# "datatype_drift"

ROWS = 50000


# ===============================
# DATA GENERATION
# ===============================

def generate_base_dataset(rows):

    start_date = datetime(2024, 1, 1)

    products = [
        ("Espresso", "Beverage"),
        ("Latte", "Beverage"),
        ("Cappuccino", "Beverage"),
        ("Mocha", "Beverage"),
        ("Cold Brew", "Beverage"),
        ("Sandwich", "Food"),
        ("Brownie", "Food"),
        ("Muffin", "Food")
    ]

    payment_types = ["Cash", "Card", "UPI"]

    data = []

    for i in range(1, rows + 1):

        product, category = random.choice(products)

        quantity = random.randint(1, 5)
        price = round(random.uniform(100, 300), 2)
        cost = round(price * random.uniform(0.4, 0.7), 2)

        order_datetime = start_date + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59)
        )

        data.append([
            i,
            order_datetime,
            product,
            category,
            quantity,
            price,
            cost,
            random.choice(payment_types)
        ])

    columns = [
        "order_id",
        "order_datetime",
        "product_name",
        "category",
        "quantity",
        "price",
        "cost",
        "payment_type"
    ]

    return pd.DataFrame(data, columns=columns)


# ===============================
# APPLY SCHEMA CHANGE
# ===============================

def apply_schema_change(df):

    if TEST_TYPE == "extra_column":
        print("🔵 Adding extra column: discount_percentage")
        df["discount_percentage"] = np.random.randint(0, 30, size=len(df))

    elif TEST_TYPE == "missing_column":
        print("🔴 Removing required column: price")
        df = df.drop(columns=["price"])

    elif TEST_TYPE == "renamed_column":
        print("🟠 Renaming column: order_datetime → timestamp")
        df = df.rename(columns={"order_datetime": "timestamp"})

    elif TEST_TYPE == "datatype_drift":
        print("🟣 Injecting datatype drift into price column")
        idx = np.random.choice(len(df), int(len(df) * 0.1), replace=False)
        df.loc[idx, "price"] = "corrupt_value"

    else:
        print("No schema change applied.")

    return df


# ===============================
# MAIN
# ===============================

if __name__ == "__main__":

    df = generate_base_dataset(ROWS)
    df = apply_schema_change(df)

    filename = f"schema_test_{TEST_TYPE}.csv"
    df.to_csv(filename, index=False)

    print(f"\n✅ Dataset generated: {filename}")
    print(f"Rows: {len(df)}")
