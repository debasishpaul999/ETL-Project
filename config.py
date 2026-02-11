DATA_SOURCE_TYPE = "csv"  # csv | json | database

DATA_CONFIG = {
    "csv": {
        "path": "data/raw_coffee_sales.csv"
    },
    "json": {
        "path": "data/raw_coffee_sales.json"
    },
    "database": {
        "db_name": "coffee_sales.db",
        "table_name": "raw_sales"
    }
}

DB_NAME = "coffee_sales.db"
TABLE_NAME = "sales_cleaned"
