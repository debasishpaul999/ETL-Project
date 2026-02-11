import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# -----------------------------
# CONFIG
# -----------------------------
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"
OUTPUT_PATH = "data/raw_coffee_sales.csv"

np.random.seed(42)
random.seed(42)

# -----------------------------
# PRODUCTS
# -----------------------------
products = {
    "Latte": {"category": "Beverage", "price_range": (180, 250)},
    "Cappuccino": {"category": "Beverage", "price_range": (170, 240)},
    "Americano": {"category": "Beverage", "price_range": (150, 220)},
    "Cold Brew": {"category": "Beverage", "price_range": (200, 280)},
    "Mocha": {"category": "Beverage", "price_range": (190, 260)},
    "Espresso": {"category": "Beverage", "price_range": (120, 180)},
    "Croissant": {"category": "Food", "price_range": (120, 200)},
    "Muffin": {"category": "Food", "price_range": (100, 180)},
    "Sandwich": {"category": "Food", "price_range": (150, 250)},
    "Brownie": {"category": "Food", "price_range": (90, 160)},
}

payment_types = ["UPI", "Card", "Cash"]

# -----------------------------
# DATE RANGE
# -----------------------------
date_range = pd.date_range(start=START_DATE, end=END_DATE)

data = []
order_id = 1

# -----------------------------
# DATA GENERATION
# -----------------------------
for single_date in date_range:
    
    is_weekend = single_date.weekday() >= 5
    
    # Normal traffic logic
    if is_weekend:
        orders_per_day = np.random.randint(60, 120)
    else:
        orders_per_day = np.random.randint(150, 250)
    
    # Inject anomaly days
    if single_date.month == 3 and single_date.day == 15:
        orders_per_day = 500  # Corporate event spike
    
    if single_date.month == 7 and single_date.day == 10:
        orders_per_day = 20  # Machine breakdown
    
    for _ in range(orders_per_day):
        
        product_name = random.choice(list(products.keys()))
        product_info = products[product_name]
        
        price = round(np.random.uniform(*product_info["price_range"]), 2)
        cost = round(price * np.random.uniform(0.4, 0.6), 2)
        quantity = np.random.randint(1, 4)
        
        # Random time between 7 AM and 8 PM
        hour = np.random.randint(7, 20)
        minute = np.random.randint(0, 60)
        order_datetime = single_date + timedelta(hours=hour, minutes=minute)
        
        data.append([
            order_id,
            order_datetime,
            product_name,
            product_info["category"],
            quantity,
            price,
            cost,
            random.choice(payment_types),
            is_weekend
        ])
        
        order_id += 1

# -----------------------------
# CREATE DATAFRAME
# -----------------------------
columns = [
    "order_id",
    "order_datetime",
    "product_name",
    "category",
    "quantity",
    "price",
    "cost",
    "payment_type",
    "is_weekend"
]

df = pd.DataFrame(data, columns=columns)

# Save to CSV
df.to_csv(OUTPUT_PATH, index=False)

print(f"Dataset generated successfully with {len(df)} rows.")
