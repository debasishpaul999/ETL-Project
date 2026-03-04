import random
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from utils.logger import get_logger

logger = get_logger()

DATASET_PATH = Path("data/raw_coffee_sales.csv")
PAYMENT_TYPES = ["UPI", "Card", "Cash"]
PRODUCTS = {
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

OUTPUT_COLUMNS = [
    "order_id",
    "order_datetime",
    "product_name",
    "category",
    "quantity",
    "price",
    "cost",
    "payment_type",
    "is_weekend",
]

def _sample_cost(price: float, category: str) -> float:
    """Sample realistic cost by category so margins vary by product type."""
    min_ratio, max_ratio = COST_RATIO_BY_CATEGORY.get(category, DEFAULT_COST_RATIO)
    return round(price * np.random.uniform(min_ratio, max_ratio), 2)

def _assign_order_ids_by_datetime(df: pd.DataFrame, start_order_id: int) -> pd.DataFrame:
    """Assign sequential order IDs after sorting rows by order_datetime."""
    df = df.sort_values("order_datetime").reset_index(drop=True)
    df["order_id"] = range(start_order_id, start_order_id + len(df))
    return df

def _build_daily_rows(target_date: date, start_order_id: int) -> pd.DataFrame:
    """Generate one day of synthetic coffee sales in the existing project style."""
    np.random.seed(int(target_date.strftime("%Y%m%d")))
    random.seed(int(target_date.strftime("%Y%m%d")))

    is_weekend = target_date.weekday() >= 5
    orders_per_day = np.random.randint(60, 120) if is_weekend else np.random.randint(150, 250)

    rows = []
    for offset in range(orders_per_day):
        product_name = random.choice(list(PRODUCTS.keys()))
        product_info = PRODUCTS[product_name]

        price = round(np.random.uniform(*product_info["price_range"]), 2)
        cost = _sample_cost(price=price, category=product_info["category"])
        quantity = np.random.randint(1, 4)

        order_time = pd.Timestamp(target_date) + pd.Timedelta(
            hours=np.random.randint(7, 20),
            minutes=np.random.randint(0, 60),
        )

        rows.append(
            {
                "order_id": start_order_id + offset,
                "order_datetime": order_time,
                "product_name": product_name,
                "category": product_info["category"],
                "quantity": quantity,
                "price": price,
                "cost": cost,
                "payment_type": random.choice(PAYMENT_TYPES),
                "is_weekend": is_weekend,
            }
        )

    day_df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    return _assign_order_ids_by_datetime(day_df, start_order_id=start_order_id)


def ensure_daily_data(dataset_path: Path = DATASET_PATH, target_date: date | None = None) -> pd.DataFrame:
    """Backfill missing full-day data from the dataset's last date through target_date."""
    target_date = target_date or date.today()

    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
    else:
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(columns=OUTPUT_COLUMNS)

    max_order_id = pd.to_numeric(df.get("order_id", pd.Series(dtype="float64")), errors="coerce").max()
    next_order_id = int(max_order_id) + 1 if pd.notna(max_order_id) else 1

    if df.empty:
        dates_to_generate = [target_date]
    else:
        existing_dates = pd.to_datetime(df["order_datetime"], errors="coerce").dt.date.dropna()
        if existing_dates.empty:
            dates_to_generate = [target_date]
        else:
            last_date = max(existing_dates)
            if last_date >= target_date:
                logger.info(
                    f"Daily generator skipped: dataset already up to date ({last_date} >= {target_date})"
                )
                return df

            dates_to_generate = [
                day.date()
                for day in pd.date_range(last_date + pd.Timedelta(days=1), target_date)
            ]

    generated_days = []
    new_frames = []
    for day in dates_to_generate:
        day_df = _build_daily_rows(target_date=day, start_order_id=next_order_id)
        next_order_id += len(day_df)
        new_frames.append(day_df)
        generated_days.append(day)

    full_df = pd.concat([df, *new_frames], ignore_index=True)
    full_df.to_csv(dataset_path, index=False)

    logger.info(
        f"Daily generator appended {sum(len(f) for f in new_frames)} rows "
        f"across {len(generated_days)} day(s): {generated_days[0]} -> {generated_days[-1]}"
    )

    return full_df
