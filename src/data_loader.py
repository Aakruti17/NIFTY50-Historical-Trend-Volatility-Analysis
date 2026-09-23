import pandas as pd
from src import config


def load_raw_excel(file_path: str = config.RAW_EXCEL_FILE,
                    sheet_name: str = config.RAW_SHEET_NAME) -> pd.DataFrame:
    print(f"Loading raw data from: {file_path}  (sheet: {sheet_name})")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")
    return df


def save_processed_csv(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path, index=False)
    print(f"Saved cleaned data -> {file_path}")


def load_processed_csv(file_path: str = config.CLEANED_CSV_FILE) -> pd.DataFrame:
    df = pd.read_csv(file_path, parse_dates=["Date"])
    print(f"Loaded processed data from {file_path}: {df.shape[0]} rows.")
    return df


def load_from_mysql(query: str = None) -> pd.DataFrame:
    from src.db_connector import get_sqlalchemy_engine 

    if query is None:
        query = f"SELECT * FROM {config.TABLE_NAME};"

    engine = get_sqlalchemy_engine()
    df = pd.read_sql(query, con=engine)
    print(f"Loaded {len(df)} rows from MySQL table '{config.TABLE_NAME}'.")
    return df


if __name__ == "__main__":
    raw_df = load_raw_excel()
    print(raw_df.head())
    print(raw_df.dtypes)
