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
        cost = round(price * np.random.uniform(0.4, 0.6), 2)
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

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


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
