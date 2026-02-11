import time
import argparse

from etl.extract import extract_data
from etl.transform import transform_data
from etl.validator import validate_schema, validate_data
from etl.load import load_data
from analytics.anomaly import detect_anomalies
from analytics.dashboard import generate_dashboard
from analytics.generate_report import generate_pdf_report

from utils.logger import get_logger
from utils.cli import print_header, print_step, print_success, print_failure

logger = get_logger()


def run_pipeline(show_dashboard=False):

    start_time = time.time()

    print_header()

    try:
        # =============================
        # EXTRACT
        # =============================
        print_step("Extracting Data...")
        df = extract_data()
        print_success(f"Extracted {len(df):,} rows")

        # =============================
        # SCHEMA VALIDATION (NEW ORDER)
        # =============================
        print_step("Validating Schema...")
        validate_schema(df)
        print_success("Schema validation passed")

        # =============================
        # TRANSFORM
        # =============================
        print_step("Transforming Data...")
        df = transform_data(df)
        print_success("Transformation complete")

        # =============================
        # DATA VALIDATION
        # =============================
        print_step("Validating Data...")
        validate_data(df)
        print_success("Validation passed")

        # =============================
        # LOAD
        # =============================
        print_step("Loading to Database...")
        load_data(df)
        print_success("Database load complete")

        # ANOMALY DETECTION
        print_step("Running Anomaly Detection...")
        anomalies, daily = detect_anomalies()
        print_success(f"{len(anomalies)} anomaly days detected")

        # DASHBOARD
        print_step("Generating Dashboard Image...")
        generate_dashboard(daily, anomalies)
        print_success("Dashboard updated")


        # =============================
        # EXECUTIVE REPORT
        # =============================
        print_step("Generating Executive PDF Report...")
        generate_pdf_report()
        print_success("Executive report generated")

        elapsed = round(time.time() - start_time, 2)

        print_success(f"Pipeline Completed Successfully | Execution Time: {elapsed} sec")

    except Exception as e:
        print_failure(str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()

    run_pipeline(show_dashboard=args.dashboard)
