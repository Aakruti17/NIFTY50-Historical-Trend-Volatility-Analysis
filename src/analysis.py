import os
import pandas as pd
from src import config

def overall_summary(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Open", "High", "Low", "Close", "Volume_Shares_Mn", "Turnover_Cr",
            "RSI_14", "India_VIX", "Daily_Return_Pct_Recomputed"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].describe().transpose().reset_index().rename(columns={"index": "Metric"})


def yearly_performance(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("Year").agg(
        Avg_Close=("Close", "mean"),
        Year_Start_Close=("Close", "first"),
        Year_End_Close=("Close", "last"),
        Avg_Daily_Return_Pct=("Daily_Return_Pct_Recomputed", "mean"),
        Avg_India_VIX=("India_VIX", "mean"),
        Trading_Days=("Close", "count"),
    ).reset_index()
    grouped["Year_Return_Pct"] = (
        (grouped["Year_End_Close"] - grouped["Year_Start_Close"]) / grouped["Year_Start_Close"] * 100
    )
    return grouped


def monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    
    grouped = df.groupby("Month_Name").agg(
        Avg_Daily_Return_Pct=("Daily_Return_Pct_Recomputed", "mean"),
        Avg_Volume_Shares_Mn=("Volume_Shares_Mn", "mean"),
    ).reset_index()
    month_order = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
    grouped["Month_Name"] = pd.Categorical(grouped["Month_Name"], categories=month_order, ordered=True)
    return grouped.sort_values("Month_Name")


def sector_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """How often each sector was the 'Top_Sector' of the day."""
    counts = df["Top_Sector"].value_counts().reset_index()
    counts.columns = ["Top_Sector", "Days_As_Top_Sector"]
    return counts


def sentiment_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    
    return df.groupby("Market_Sentiment").agg(
        Num_Days=("Date", "count"),
        Avg_India_VIX=("India_VIX", "mean"),
        Avg_Daily_Return_Pct=("Daily_Return_Pct_Recomputed", "mean"),
    ).reset_index()


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
   
    cols = ["Close", "Volume_Shares_Mn", "Turnover_Cr", "RSI_14",
            "India_VIX", "Advance_Decline_Ratio", "Daily_Return_Pct_Recomputed"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].corr()


def most_volatile_days(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
   
    top = df.reindex(df["Daily_Return_Pct_Recomputed"].abs().sort_values(ascending=False).index)
    return top[["Date", "Close", "Daily_Return_Pct_Recomputed", "India_VIX", "Market_Sentiment"]].head(top_n)


def run_all_analysis(df: pd.DataFrame) -> dict:
    
    print("\n--- Running EDA / analysis ---")
    results = {
        "overall_summary": overall_summary(df),
        "yearly_performance": yearly_performance(df),
        "monthly_seasonality": monthly_seasonality(df),
        "sector_frequency": sector_frequency(df),
        "sentiment_breakdown": sentiment_breakdown(df),
        "correlation_matrix": correlation_matrix(df),
        "most_volatile_days": most_volatile_days(df),
    }
    print("--- Analysis complete ---\n")
    return results



def _fmt(value, decimals=2):
    try:
        return f"{value:,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def build_business_insights_text(df: pd.DataFrame, results: dict) -> str:
    
    yearly = results["yearly_performance"]
    monthly = results["monthly_seasonality"]
    sectors = results["sector_frequency"]
    sentiment = results["sentiment_breakdown"]
    corr = results["correlation_matrix"]
    volatile_days = results["most_volatile_days"]
    overall = results["overall_summary"].set_index("Metric")

    df_sorted = df.sort_values("Date")
    start_date = df_sorted["Date"].min().strftime("%d %b %Y")
    end_date = df_sorted["Date"].max().strftime("%d %b %Y")
    start_close = df_sorted["Close"].iloc[0]
    end_close = df_sorted["Close"].iloc[-1]
    overall_growth = (end_close - start_close) / start_close * 100

    best_year = yearly.loc[yearly["Year_Return_Pct"].idxmax()]
    worst_year = yearly.loc[yearly["Year_Return_Pct"].idxmin()]
    best_month = monthly.loc[monthly["Avg_Daily_Return_Pct"].idxmax()]
    worst_month = monthly.loc[monthly["Avg_Daily_Return_Pct"].idxmin()]
    top_sector_row = sectors.iloc[0]
    top_sector_share_pct = top_sector_row["Days_As_Top_Sector"] / sectors["Days_As_Top_Sector"].sum() * 100

    vix_return_corr = corr.loc["India_VIX", "Daily_Return_Pct_Recomputed"] if "India_VIX" in corr.index else None
    close_turnover_corr = corr.loc["Close", "Turnover_Cr"] if "Close" in corr.index and "Turnover_Cr" in corr.columns else None

    biggest_day = volatile_days.iloc[0]
    biggest_day_date = biggest_day["Date"]
    if hasattr(biggest_day_date, "strftime"):
        biggest_day_date = biggest_day_date.strftime("%d %b %Y")

    lines = []
    sep = "=" * 78

    lines.append(sep)
    lines.append("NIFTY50 HISTORICAL TREND & VOLATILITY -- BUSINESS INSIGHTS")
    lines.append(sep)
    lines.append(f"Analysis period: {start_date} to {end_date}  ({len(df):,} trading days)")
    lines.append("")

    lines.append("1. OVERALL PERFORMANCE")
    lines.append("-" * 78)
    lines.append(
        f"- NIFTY50 moved from {_fmt(start_close)} to {_fmt(end_close)} over the period, "
        f"an overall change of {_fmt(overall_growth)}%."
    )
    lines.append(
        f"- The index averaged a daily return of {_fmt(overall.loc['Daily_Return_Pct_Recomputed', 'mean'], 4)}% "
        f"per trading day, with daily moves ranging from "
        f"{_fmt(overall.loc['Daily_Return_Pct_Recomputed', 'min'], 2)}% to "
        f"{_fmt(overall.loc['Daily_Return_Pct_Recomputed', 'max'], 2)}%."
    )
    lines.append(
        f"- Average daily traded volume was {_fmt(overall.loc['Volume_Shares_Mn', 'mean'], 1)} million shares, "
        f"worth an average turnover of {_fmt(overall.loc['Turnover_Cr', 'mean'], 1)} INR Crores."
    )
    lines.append("")

    lines.append("2. YEARLY PERFORMANCE")
    lines.append("-" * 78)
    lines.append(
        f"- Best year: {int(best_year['Year'])} with a return of {_fmt(best_year['Year_Return_Pct'])}% "
        f"(average VIX {_fmt(best_year['Avg_India_VIX'])})."
    )
    lines.append(
        f"- Worst year: {int(worst_year['Year'])} with a return of {_fmt(worst_year['Year_Return_Pct'])}% "
        f"(average VIX {_fmt(worst_year['Avg_India_VIX'])})."
    )
    lines.append(
        "- Year-by-year returns: "
        + ", ".join(f"{int(r.Year)}: {_fmt(r.Year_Return_Pct)}%" for r in yearly.itertuples())
    )
    lines.append("")

    lines.append("3. SEASONALITY (BY CALENDAR MONTH)")
    lines.append("-" * 78)
    lines.append(
        f"- {best_month['Month_Name']} has historically been the strongest month, "
        f"averaging {_fmt(best_month['Avg_Daily_Return_Pct'], 4)}% per day."
    )
    lines.append(
        f"- {worst_month['Month_Name']} has historically been the weakest month, "
        f"averaging {_fmt(worst_month['Avg_Daily_Return_Pct'], 4)}% per day."
    )
    lines.append("")

    lines.append("4. VOLATILITY & MARKET SENTIMENT")
    lines.append("-" * 78)
    for _, row in sentiment.iterrows():
        lines.append(
            f"- {row['Market_Sentiment']} days: {int(row['Num_Days'])} days "
            f"(avg VIX {_fmt(row['Avg_India_VIX'])}, avg return {_fmt(row['Avg_Daily_Return_Pct'], 4)}%)."
        )
    if vix_return_corr is not None:
        direction = "inversely" if vix_return_corr < 0 else "positively"
        meaning = ("higher fear tends to line up with weaker/negative returns" if vix_return_corr < 0
                   else "higher fear tends to line up with stronger returns")
        lines.append(
            f"- India VIX and daily returns are {direction} correlated "
            f"(correlation = {_fmt(vix_return_corr, 2)}), meaning {meaning}."
        )
    lines.append(
        f"- The single most volatile trading day was {biggest_day_date}, with a "
        f"{_fmt(biggest_day['Daily_Return_Pct_Recomputed'])}% move and an India VIX of {_fmt(biggest_day['India_VIX'])}."
    )
    lines.append("")

    lines.append("5. SECTOR TRENDS")
    lines.append("-" * 78)
    lines.append(
        f"- {top_sector_row['Top_Sector']} was the most frequent top-performing sector, "
        f"leading on {int(top_sector_row['Days_As_Top_Sector'])} days ({_fmt(top_sector_share_pct, 1)}% of all days)."
    )
    if len(sectors) > 1:
        runner_up = sectors.iloc[1]
        lines.append(
            f"- {runner_up['Top_Sector']} was the second most frequent top sector, "
            f"leading on {int(runner_up['Days_As_Top_Sector'])} days."
        )
    lines.append("")

    lines.append("6. RELATIONSHIPS BETWEEN INDICATORS")
    lines.append("-" * 78)
    if close_turnover_corr is not None:
        relationship = ("trading value tends to rise alongside the index level" if close_turnover_corr > 0
                        else "little consistent relationship between index level and trading value")
        lines.append(
            f"- Close price and Turnover are correlated at {_fmt(close_turnover_corr, 2)}, "
            f"suggesting {relationship}."
        )
    lines.append(
        "- Full correlation figures between Close, Volume, Turnover, RSI, India VIX, "
        "Advance/Decline Ratio and Daily Return are visualized in the correlation heatmap "
        "(see outputs/graphs/07_heatmap_correlation.png and the PDF report)."
    )
    lines.append("")

    lines.append("7. TOP 5 MOST VOLATILE TRADING DAYS")
    lines.append("-" * 78)
    for _, row in volatile_days.head(5).iterrows():
        d = row["Date"]
        d = d.strftime("%d %b %Y") if hasattr(d, "strftime") else d
        lines.append(
            f"- {d}: Close {_fmt(row['Close'])}, return {_fmt(row['Daily_Return_Pct_Recomputed'])}%, "
            f"VIX {_fmt(row['India_VIX'])}, sentiment {row['Market_Sentiment']}."
        )
    lines.append("")

    lines.append("8. KEY TAKEAWAYS")
    lines.append("-" * 78)
    lines.append(f"- Overall index change across the full period: {_fmt(overall_growth)}%.")
    lines.append(f"- Strongest year: {int(best_year['Year'])} ({_fmt(best_year['Year_Return_Pct'])}%). "
                  f"Weakest year: {int(worst_year['Year'])} ({_fmt(worst_year['Year_Return_Pct'])}%).")
    lines.append(f"- {top_sector_row['Top_Sector']} led the market most often.")
    lines.append("- Elevated India VIX levels line up with larger daily price swings, "
                  "which is consistent with VIX's role as a volatility/fear gauge.")
    lines.append("")
    lines.append(sep)

    return "\n".join(lines)


def save_business_insights(text: str, filename: str = "business_insights.txt") -> str:
    path = os.path.join(config.ANALYSIS_DIR, filename)
    with open(path, "w") as f:
        f.write(text)
    print(f"Saved business insights -> {path}")
    return path


def generate_business_insights(df: pd.DataFrame, results: dict) -> str:
    text = build_business_insights_text(df, results)
    return save_business_insights(text)


if __name__ == "__main__":
    from src.data_loader import load_processed_csv

    featured_df = load_processed_csv(config.FEATURED_CSV_FILE)
    analysis_results = run_all_analysis(featured_df)
    generate_business_insights(featured_df, analysis_results)
