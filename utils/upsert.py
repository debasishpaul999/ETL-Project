import time
from sqlalchemy import Table, MetaData
from sqlalchemy.dialects.mysql import insert as mysql_insert
from tqdm import tqdm
from utils.logger import get_logger
from config import DATABASE_CONFIG

logger = get_logger()

def upsert_dataframe(engine, table_name, df, chunk_size=5000):
    logger.info(f"Starting load into '{table_name}'")

    start_time = time.time()

    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = Table(table_name, metadata, autoload_with=engine)

    records = df.to_dict(orient="records")
    total_rows = len(records)

    chunks = [
        records[i:i + chunk_size]
        for i in range(0, total_rows, chunk_size)
    ]

    engine_type = DATABASE_CONFIG["engine"]

    with engine.begin() as conn:
        for chunk in tqdm(
            chunks,
            desc=f"Loading ({engine_type})",
            unit="batch",
            colour="green",
            dynamic_ncols=True
        ):
            if engine_type == "mysql":
                stmt = mysql_insert(table)
                stmt = stmt.on_duplicate_key_update(
                    {c.name: stmt.inserted[c.name] for c in table.columns}
                )
                conn.execute(stmt, chunk)

            else:
                # SQLite fallback (append only)
                conn.execute(table.insert(), chunk)

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    throughput = round(total_rows / duration, 2) if duration > 0 else total_rows

    logger.info(f"Load completed in {duration} sec | {throughput} rows/sec")
