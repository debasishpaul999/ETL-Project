from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

username = "debasish"
password = quote_plus("debasish@999")   # encode special characters
host = "127.0.0.1"
port = 3306
database = "coffee_etl_db"

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT VERSION();"))
        version = result.fetchone()
        print("✅ Connected successfully!")
        print("MySQL version:", version[0])
except Exception as e:
    print("❌ Connection failed:", e)
