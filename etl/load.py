import sqlite3
from config import DB_NAME, TABLE_NAME

def load_data(df):
    print("Loading data into database...")
    df['order_datetime'] = df['order_datetime'].astype(str)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            order_id INTEGER PRIMARY KEY,
            order_datetime TEXT,
            product_name TEXT,
            category TEXT,
            quantity INTEGER,
            price REAL,
            cost REAL,
            payment_type TEXT,
            is_weekend BOOLEAN,
            revenue REAL,
            total_cost REAL,
            profit REAL
        )
    """)

    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT OR REPLACE INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))

    conn.commit()
    conn.close()

    print("Data loaded successfully.")
