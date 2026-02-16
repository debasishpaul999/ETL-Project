import time
from tqdm import tqdm
from sqlalchemy import text

from utils.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()

TABLE_NAME = "sales_cleaned"
BATCH_SIZE = 5000


# ==============================
# TABLE CREATION FUNCTION
# ==============================
def create_table_if_not_exists(engine):

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        order_id INT PRIMARY KEY,
        order_datetime DATETIME,
        product_name VARCHAR(100),
        category VARCHAR(50),
        quantity INT,
        price FLOAT,
        cost FLOAT,
        payment_type VARCHAR(50),
        is_weekend BOOLEAN,
        revenue FLOAT,
        total_cost FLOAT,
        profit FLOAT
    )
    """

    with engine.begin() as conn:
        conn.execute(text(create_sql))

    logger.info("Table ensured: sales_cleaned")


# ==============================
# LOAD FUNCTION
# ==============================
def load_data(df):

    logger.info("Loading data using production UPSERT")

    engine = get_engine()

    # 🔴 NEW: ensure table exists
    create_table_if_not_exists(engine)

    start_time = time.time()

    logger.info(f"Starting load into '{TABLE_NAME}'")

    columns = df.columns.tolist()

    insert_stmt = f"""
    INSERT INTO {TABLE_NAME} ({', '.join(columns)})
    VALUES ({', '.join([f':{col}' for col in columns])})
    AS new
    ON DUPLICATE KEY UPDATE
    {', '.join([f"{col} = new.{col}" for col in columns])}
    """

    total_batches = (len(df) // BATCH_SIZE) + 1

    with engine.begin() as connection:

        for i in tqdm(
            range(0, len(df), BATCH_SIZE),
            desc="Loading (mysql)",
            unit="batch"
        ):

            batch = df.iloc[i:i + BATCH_SIZE]
            data = batch.to_dict(orient="records")

            connection.execute(text(insert_stmt), data)

    elapsed = round(time.time() - start_time, 2)
    throughput = round(len(df) / elapsed, 2)

    logger.info(f"Load completed in {elapsed} sec | {throughput} rows/sec")
