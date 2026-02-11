import json
from utils.logger import get_logger

logger = get_logger()

# ==============================
# REQUIRED RAW INPUT SCHEMA
# ==============================

REQUIRED_COLUMNS = [
    "order_id",
    "order_datetime",
    "product_name",
    "category",
    "quantity",
    "price",
    "cost",
    "payment_type"
]


# ==============================
# SCHEMA VALIDATION (BEFORE TRANSFORM)
# ==============================

def validate_schema(df):

    logger.info("Validating schema")

    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    extra = set(df.columns) - set(REQUIRED_COLUMNS)
    if extra:
        logger.warning(f"Extra columns detected (ignored later): {extra}")

    logger.info("Schema validation passed")
    return True


# ==============================
# DATA VALIDATION (AFTER TRANSFORM)
# ==============================

def validate_data(df):

    logger.info("Running data validation")

    report = {
        "row_count": int(len(df)),
        "null_counts": {
            col: int(df[col].isnull().sum())
            for col in df.columns
        }
    }

    with open("reports/validation_report.json", "w") as f:
        json.dump(report, f, indent=4)

    logger.info("Validation complete. Report saved.")
    return df
