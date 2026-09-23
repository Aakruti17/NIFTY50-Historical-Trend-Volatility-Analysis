import os
import matplotlib.pyplot as plt
import seaborn as sns

from src import config

sns.set_theme(style="whitegrid")


def _save_fig(fig, filename: str):
    path = os.path.join(config.GRAPHS_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart -> {path}")


def plot_return_histogram(df):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(df["Daily_Return_Pct_Recomputed"], bins=60, kde=True, color="#1f77b4", ax=ax)
    ax.set_title("Distribution of NIFTY50 Daily Returns (%)")
    ax.set_xlabel("Daily Return (%)")
    ax.set_ylabel("Number of Trading Days")
    _save_fig(fig, "01_histogram_daily_returns.png")


def plot_yearly_return_bar(yearly_df):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#2ca02c" if v >= 0 else "#d62728" for v in yearly_df["Year_Return_Pct"]]
    ax.bar(yearly_df["Year"].astype(str), yearly_df["Year_Return_Pct"], color=colors)
    ax.set_title("NIFTY50 Yearly Return (%)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Year Return (%)")
    ax.axhline(0, color="black", linewidth=0.8)
    _save_fig(fig, "02_bar_yearly_return.png")


def plot_close_price_trend(df):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["Date"], df["Close"], label="Close Price", color="#1f77b4", linewidth=0.9)
    ax.plot(df["Date"], df["50_Day_MA"], label="50-Day MA", color="orange", linewidth=1.2)
    ax.plot(df["Date"], df["200_Day_MA"], label="200-Day MA", color="red", linewidth=1.2)
    ax.set_title("NIFTY50 Close Price with Moving Averages")
    ax.set_xlabel("Date")
    ax.set_ylabel("Index Level")
    ax.legend()
    _save_fig(fig, "03_line_close_price_trend.png")


def plot_sector_pie(sector_df, top_n: int = 8):
    top = sector_df.head(top_n)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        top["Days_As_Top_Sector"],
        labels=top["Top_Sector"],
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("Set2", len(top)),
    )
    ax.set_title(f"Top {top_n} Sectors by Days as Best Performer")
    _save_fig(fig, "04_pie_top_sectors.png")



def plot_vix_vs_return_scatter(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(
        data=df, x="India_VIX", y="Daily_Return_Pct_Recomputed",
        hue="Market_Sentiment", alpha=0.6, ax=ax, palette="Set1",
    )
    ax.set_title("India VIX vs Daily Return")
    ax.set_xlabel("India VIX (Fear Index)")
    ax.set_ylabel("Daily Return (%)")
    _save_fig(fig, "05_scatter_vix_vs_return.png")


def plot_return_boxplot_by_year(df):
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=df, x="Year", y="Daily_Return_Pct_Recomputed", hue="Year",
                ax=ax, palette="coolwarm", legend=False)
    ax.set_title("Daily Return Distribution by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Daily Return (%)")
    _save_fig(fig, "06_boxplot_return_by_year.png")


def plot_correlation_heatmap(corr_matrix):
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Between Key Market Indicators")
    _save_fig(fig, "07_heatmap_correlation.png")



def plot_pairplot(df):
    cols = ["Close", "Volume_Shares_Mn", "RSI_14", "India_VIX", "Daily_Return_Pct_Recomputed"]
    cols = [c for c in cols if c in df.columns]
    sample = df[cols].dropna()
    if len(sample) > 800:
        sample = sample.sample(800, random_state=config.RANDOM_SEED)
    grid = sns.pairplot(sample, corner=True, diag_kind="kde", plot_kws={"alpha": 0.5, "s": 15})
    grid.fig.suptitle("Pairwise Relationships Between Key Indicators", y=1.02)
    path = os.path.join(config.GRAPHS_DIR, "08_pairplot_key_indicators.png")
    grid.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(grid.fig)
    print(f"Saved chart -> {path}")


def generate_all_visualizations(df, analysis_results: dict):
    print("\n--- Generating visualizations ---")
    plot_return_histogram(df)
    plot_yearly_return_bar(analysis_results["yearly_performance"])
    plot_close_price_trend(df)
    plot_sector_pie(analysis_results["sector_frequency"])
    plot_vix_vs_return_scatter(df)
    plot_return_boxplot_by_year(df)
    plot_correlation_heatmap(analysis_results["correlation_matrix"])
    plot_pairplot(df)
    print("--- Visualizations complete ---\n")


if __name__ == "__main__":
    from src.data_loader import load_processed_csv
    from src.analysis import run_all_analysis

    featured_df = load_processed_csv(config.FEATURED_CSV_FILE)
    results = run_all_analysis(featured_df)
    generate_all_visualizations(featured_df, results)
