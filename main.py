from etl.extract import extract_data
from etl.transform import transform_data
from etl.validator import validate_data
from etl.load import load_data
from analytics.anomaly import detect_anomalies

def run_pipeline():
    df = extract_data()
    df = transform_data(df)
    df = validate_data(df)
    load_data(df)
    detect_anomalies()

if __name__ == "__main__":
    run_pipeline()
