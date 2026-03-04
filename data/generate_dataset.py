import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# -----------------------------
# CONFIG
# -----------------------------
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
OUTPUT_PATH = "data/raw_coffee_sales.csv"

np.random.seed(42)
random.seed(42)

# -----------------------------
# PRODUCTS
# -----------------------------
products = {
    "Caffe Latte": {"category": "Hot Coffee", "price_range": (210, 290)},
    "Cappuccino": {"category": "Hot Coffee", "price_range": (200, 280)},
    "Caffe Americano": {"category": "Hot Coffee", "price_range": (180, 250)},
    "Flat White": {"category": "Hot Coffee", "price_range": (220, 300)},
    "Caramel Macchiato": {"category": "Hot Coffee", "price_range": (240, 330)},
    "Caffe Mocha": {"category": "Hot Coffee", "price_range": (230, 320)},
    "White Chocolate Mocha": {"category": "Hot Coffee", "price_range": (250, 340)},
    "Espresso": {"category": "Hot Coffee", "price_range": (130, 190)},
    "Espresso Con Panna": {"category": "Hot Coffee", "price_range": (170, 230)},
    "Vanilla Sweet Cream Cold Brew": {"category": "Iced Coffee", "price_range": (230, 320)},
    "Salted Caramel Cream Cold Brew": {"category": "Iced Coffee", "price_range": (240, 330)},
    "Iced Caffe Latte": {"category": "Iced Coffee", "price_range": (210, 290)},
    "Iced Caffe Mocha": {"category": "Iced Coffee", "price_range": (230, 320)},
    "Iced Caramel Macchiato": {"category": "Iced Coffee", "price_range": (240, 330)},
    "Nitro Cold Brew": {"category": "Iced Coffee", "price_range": (250, 340)},
    "Iced Shaken Espresso": {"category": "Iced Coffee", "price_range": (220, 310)},
    "Matcha Tea Latte": {"category": "Tea", "price_range": (220, 300)},
    "Chai Tea Latte": {"category": "Tea", "price_range": (200, 280)},
    "English Breakfast Tea": {"category": "Tea", "price_range": (160, 230)},
    "Earl Grey Tea": {"category": "Tea", "price_range": (160, 230)},
    "Hibiscus Herbal Tea": {"category": "Tea", "price_range": (170, 240)},
    "Iced Black Tea Lemonade": {"category": "Tea", "price_range": (190, 270)},
    "Iced Peach Green Tea": {"category": "Tea", "price_range": (210, 290)},
    "Java Chip Frappuccino": {"category": "Frappuccino", "price_range": (260, 360)},
    "Caramel Frappuccino": {"category": "Frappuccino", "price_range": (250, 350)},
    "Mocha Frappuccino": {"category": "Frappuccino", "price_range": (250, 350)},
    "Matcha Frappuccino": {"category": "Frappuccino", "price_range": (250, 350)},
    "Vanilla Cream Frappuccino": {"category": "Frappuccino", "price_range": (240, 340)},
    "Chocolate Croissant": {"category": "Bakery", "price_range": (180, 250)},
    "Butter Croissant": {"category": "Bakery", "price_range": (160, 230)},
    "Blueberry Muffin": {"category": "Bakery", "price_range": (150, 220)},
    "Banana Bread": {"category": "Bakery", "price_range": (170, 240)},
    "New York Cheesecake": {"category": "Bakery", "price_range": (210, 300)},
    "Double Chocolate Brownie": {"category": "Bakery", "price_range": (150, 220)},
    "Paneer Tikka Sandwich": {"category": "Sandwich", "price_range": (230, 320)},
    "Smoked Chicken Sandwich": {"category": "Sandwich", "price_range": (250, 340)},
    "Veggie & Cheese Sandwich": {"category": "Sandwich", "price_range": (220, 310)},
    "Classic Potato Wedges": {"category": "Snack", "price_range": (140, 210)},
    "Masala Chips": {"category": "Snack", "price_range": (90, 150)},
    "Mixed Nuts Pack": {"category": "Snack", "price_range": (130, 210)},
    "House Blend Beans 250g": {"category": "Retail Beans", "price_range": (420, 620)},
    "Espresso Roast Beans 250g": {"category": "Retail Beans", "price_range": (440, 650)},
    "French Roast Beans 250g": {"category": "Retail Beans", "price_range": (430, 640)},
    "Reusable Tumbler": {"category": "Merchandise", "price_range": (300, 520)},
    "Ceramic Mug": {"category": "Merchandise", "price_range": (280, 480)},
}

COST_RATIO_BY_CATEGORY = {
    "Hot Coffee": (0.28, 0.4),
    "Iced Coffee": (0.3, 0.43),
    "Tea": (0.24, 0.36),
    "Frappuccino": (0.32, 0.45),
    "Bakery": (0.45, 0.62),
    "Sandwich": (0.52, 0.68),
    "Snack": (0.4, 0.58),
    "Retail Beans": (0.58, 0.74),
    "Merchandise": (0.55, 0.72),
}
DEFAULT_COST_RATIO = (0.4, 0.58)


def _sample_cost(price: float, category: str) -> float:
    """Sample realistic cost by category so margins vary by product type."""
    min_ratio, max_ratio = COST_RATIO_BY_CATEGORY.get(category, DEFAULT_COST_RATIO)
    return round(price * np.random.uniform(min_ratio, max_ratio), 2)

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
        cost = _sample_cost(price=price, category=product_info["category"])
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

# Keep order_id aligned with chronological order_datetime
# so higher IDs represent later orders.
df = df.sort_values("order_datetime").reset_index(drop=True)
df["order_id"] = range(1, len(df) + 1)

# Save to CSV
df.to_csv(OUTPUT_PATH, index=False)

print(f"Dataset generated successfully with {len(df)} rows.")
