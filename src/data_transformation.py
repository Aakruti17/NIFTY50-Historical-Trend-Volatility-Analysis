import numpy as np
import pandas as pd

from src import config


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Year"] = df["Date"].dt.year
    df["Month_Num"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%B")
    df["Quarter"] = df["Date"].dt.quarter
    df["Day_of_Week_Clean"] = df["Date"].dt.day_name()
    return df


def add_return_and_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values("Date").reset_index(drop=True)

    df["Daily_Range"] = df["High"] - df["Low"]
    df["Daily_Range_Pct"] = (df["Daily_Range"] / df["Open"]) * 100

    df["Rolling_Volatility_20D"] = (
        df["Daily_Return_Pct_Recomputed"].rolling(window=20, min_periods=5).std()
    )

    df["Cumulative_Return_Pct"] = (
        (1 + df["Daily_Return_Pct_Recomputed"] / 100).cumprod() - 1
    ) * 100

    return df


def add_trend_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    conditions = [
        df["50_Day_MA"] > df["200_Day_MA"],
        df["50_Day_MA"] < df["200_Day_MA"],
    ]
    choices = ["Uptrend", "Downtrend"]
    df["MA_Trend"] = np.select(conditions, choices, default="Sideways")
    return df


def add_vix_risk_bucket(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bins = [-np.inf, 15, 20, 30, np.inf]
    labels = ["Low Volatility", "Normal", "Elevated", "High Volatility"]
    df["VIX_Risk_Bucket"] = pd.cut(df["India_VIX"], bins=bins, labels=labels)
    return df


def transform_dataset(df: pd.DataFrame) -> pd.DataFrame:
    print("\n--- Starting feature transformation ---")
    df = add_calendar_features(df)
    df = add_return_and_volatility_features(df)
    df = add_trend_labels(df)
    df = add_vix_risk_bucket(df)
    print(f"--- Transformation complete: {df.shape[1]} total columns ---\n")
    return df


if __name__ == "__main__":
    from src.data_loader import load_processed_csv, save_processed_csv

    cleaned_df = load_processed_csv(config.CLEANED_CSV_FILE)
    featured_df = transform_dataset(cleaned_df)
    save_processed_csv(featured_df, config.FEATURED_CSV_FILE)
