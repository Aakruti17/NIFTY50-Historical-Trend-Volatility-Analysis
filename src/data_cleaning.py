import numpy as np
import pandas as pd
from src import config

def fix_dates(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed", errors="coerce")
    n_bad = df["Date"].isna().sum()
    if n_bad:
        print(f"[fix_dates] Could not parse {n_bad} date value(s); they are now NaT and will be dropped.")
    df = df.dropna(subset=["Date"])
    return df



def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in config.TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})

   
    for col in ["Day_of_Week", "Month"]:
        if col in df.columns:
            df[col] = df[col].str.title()

  
    if "Is_Market_Holiday" in df.columns:
        df["Is_Market_Holiday"] = df["Is_Market_Holiday"].str.title()
        df["Is_Market_Holiday"] = df["Is_Market_Holiday"].replace(
            {"Y": "Yes", "N": "No", "True": "Yes", "False": "No"}
        )

  
    if "Market_Sentiment" in df.columns:
        df["Market_Sentiment"] = df["Market_Sentiment"].str.title()

    return df


def fix_sector_typos(df: pd.DataFrame) -> pd.DataFrame:
    """Map known misspellings of Top_Sector to their correct name."""
    df = df.copy()
    if "Top_Sector" not in df.columns:
        return df

    def _clean_one(value):
        if pd.isna(value):
            return value
        key = str(value).strip().lower()
        return config.SECTOR_TYPO_MAP.get(key, str(value).strip().title())

    df["Top_Sector"] = df["Top_Sector"].apply(_clean_one)
    return df


def fix_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in config.NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        if df[col].dtype == object:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

   
    for col in ["Volume_Shares_Mn", "Turnover_Cr"]:
        if col in df.columns:
            df[col] = df[col].abs()

    return df


def treat_price_outliers(df: pd.DataFrame, deviation_threshold: float = 0.25) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values("Date").reset_index(drop=True)
    price_cols = ["Open", "High", "Low", "Close", "Prev_Close", "50_Day_MA", "200_Day_MA"]

    for col in price_cols:
        if col not in df.columns:
            continue

        # Sign-flip fix: an index price is never negative
        df[col] = df[col].abs()

        rolling_median = df[col].rolling(window=15, center=True, min_periods=5).median()
        pct_deviation = (df[col] - rolling_median).abs() / rolling_median

        is_outlier = pct_deviation > deviation_threshold
        n_outliers = is_outlier.sum()
        if n_outliers:
            print(f"[treat_price_outliers] {col}: replacing {n_outliers} outlier value(s) "
                  f"(>{deviation_threshold:.0%} off their local 15-day median) with that median.")
        df.loc[is_outlier, col] = rolling_median[is_outlier]

    return df


def validate_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    row_max = df[["Open", "Close", "Low"]].max(axis=1)
    row_min = df[["Open", "Close", "High"]].min(axis=1)

    bad_high = df["High"] < row_max
    bad_low = df["Low"] > row_min

    if bad_high.sum():
        print(f"[validate_ohlc] Fixing {bad_high.sum()} row(s) where High was too low.")
        df.loc[bad_high, "High"] = df.loc[bad_high, ["Open", "Close", "Low"]].max(axis=1)

    if bad_low.sum():
        print(f"[validate_ohlc] Fixing {bad_low.sum()} row(s) where Low was too high.")
        df.loc[bad_low, "Low"] = df.loc[bad_low, ["Open", "Close", "High"]].min(axis=1)

    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()
    df = df.sort_values("Date")

    price_cols = ["Open", "High", "Low", "Close", "Prev_Close"]
    for col in price_cols:
        if col in df.columns:
            df[col] = df[col].ffill().bfill()

    other_numeric = [c for c in config.NUMERIC_COLUMNS if c not in price_cols and c in df.columns]
    for col in other_numeric:
        df[col] = df[col].fillna(df[col].median())

    for col in config.TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully duplicated rows and duplicated trading dates (keep first)."""
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["Date"], keep="first")
    removed = before - len(df)
    if removed:
        print(f"[remove_duplicates] Removed {removed} duplicate row(s).")
    return df


def recompute_daily_return(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values("Date").reset_index(drop=True)

    # Recompute Prev_Close from the cleaned Close series itself, since
    # the original Prev_Close values may also contain errors.
    df["Prev_Close_Recomputed"] = df["Close"].shift(1)
    df["Daily_Return_Pct_Recomputed"] = (
        (df["Close"] - df["Prev_Close_Recomputed"]) / df["Prev_Close_Recomputed"] * 100
    )
    df["Daily_Return_Pct_Recomputed"] = df["Daily_Return_Pct_Recomputed"].fillna(0)
    return df

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    print("\n--- Starting data cleaning pipeline ---")
    df = fix_dates(df)
    df = clean_text_columns(df)
    df = fix_sector_typos(df)
    df = fix_numeric_columns(df)
    df = remove_duplicates(df)
    df = treat_price_outliers(df)
    df = validate_ohlc(df)
    df = handle_missing_values(df)
    df = recompute_daily_return(df)
    df = df.sort_values("Date").reset_index(drop=True)
    print(f"--- Cleaning complete: {len(df)} rows remain ---\n")
    return df


if __name__ == "__main__":
    from src.data_loader import load_raw_excel, save_processed_csv

    raw_df = load_raw_excel()
    cleaned_df = clean_dataset(raw_df)
    save_processed_csv(cleaned_df, config.CLEANED_CSV_FILE)
