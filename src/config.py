
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

RAW_EXCEL_FILE = os.path.join(RAW_DATA_DIR, "NIFTY50_Historical_Trend_Volatility_Dataset.xlsx")
RAW_SHEET_NAME = "Nifty50_Raw_Data"

CLEANED_CSV_FILE = os.path.join(PROCESSED_DATA_DIR, "nifty50_cleaned.csv")
FEATURED_CSV_FILE = os.path.join(PROCESSED_DATA_DIR, "nifty50_features.csv")


OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
ANALYSIS_DIR = os.path.join(OUTPUTS_DIR, "analysis")
GRAPHS_DIR = os.path.join(OUTPUTS_DIR, "graphs")
REPORT_DIR = os.path.join(OUTPUTS_DIR, "report")

SQL_DIR = os.path.join(BASE_DIR, "sql")


DB_CONFIG = {
    "host": os.getenv("NIFTY_DB_HOST", "localhost"),
    "port": int(os.getenv("NIFTY_DB_PORT", "3306")),
    "user": os.getenv("NIFTY_DB_USER", "root"),
    "password": os.getenv("NIFTY_DB_PASSWORD", "password"),
    "database": os.getenv("NIFTY_DB_NAME", "nifty50_db"),
}

TABLE_NAME = "nifty50_prices"


NUMERIC_COLUMNS = [
    "Open", "High", "Low", "Close", "Prev_Close", "Daily_Return_Pct",
    "Volume_Shares_Mn", "Turnover_Cr", "50_Day_MA", "200_Day_MA",
    "RSI_14", "India_VIX", "Advance_Decline_Ratio",
]


TEXT_COLUMNS = ["Day_of_Week", "Month", "Top_Sector", "Market_Sentiment", "Is_Market_Holiday"]


SECTOR_TYPO_MAP = {
    "bankng": "Banking",
    "bank": "Banking",
    "banking": "Banking",
    "it ": "IT",
    "it": "IT",
    "pharam": "Pharma",
    "pharma": "Pharma",
    "realety": "Realty",
    "realty": "Realty",
    "auto": "Auto",
    "fmcg": "FMCG",
    "metal": "Metal",
    "energy": "Energy",
    "finance": "Finance",
    "financial services": "Financial Services",
}

RANDOM_SEED = 42
