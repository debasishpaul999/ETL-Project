# utils/db.py

from sqlalchemy import create_engine
from config import DATABASE_CONFIG
from urllib.parse import quote_plus


def get_engine():
    """
    Centralized database engine creator.
    Handles special characters in passwords safely.
    """

    if DATABASE_CONFIG["db_type"] == "mysql":

        encoded_password = quote_plus(DATABASE_CONFIG["password"])

        connection_string = (
            f"mysql+pymysql://{DATABASE_CONFIG['user']}:"
            f"{encoded_password}@"
            f"{DATABASE_CONFIG['host']}/"
            f"{DATABASE_CONFIG['database']}"
        )

    elif DATABASE_CONFIG["db_type"] == "sqlite":
        connection_string = f"sqlite:///{DATABASE_CONFIG['db_path']}"

    else:
        raise ValueError("Unsupported database type")

    return create_engine(connection_string)
