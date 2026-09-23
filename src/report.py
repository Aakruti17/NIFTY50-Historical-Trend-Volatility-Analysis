import os

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether,
)

from src import config

_styles = getSampleStyleSheet()
_styles.add(ParagraphStyle(
    name="ReportTitle", parent=_styles["Title"], fontSize=22, spaceAfter=6,
))
_styles.add(ParagraphStyle(
    name="ReportSubtitle", parent=_styles["Normal"], fontSize=11,
    textColor=colors.grey, spaceAfter=18,
))
_styles.add(ParagraphStyle(
    name="SectionHeading", parent=_styles["Heading1"], fontSize=15,
    spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#1f3864"),
))
_styles.add(ParagraphStyle(
    name="Body", parent=_styles["Normal"], fontSize=10.5, leading=15, spaceAfter=6,
))
_styles.add(ParagraphStyle(
    name="Caption", parent=_styles["Normal"], fontSize=8.5,
    textColor=colors.grey, spaceBefore=2, spaceAfter=12, alignment=1,  # centered
))

_TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B7C3D0")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F7")]),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
])


def _fmt(value, decimals=2):
    try:
        return f"{value:,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def _df_to_table(df: pd.DataFrame, col_widths=None) -> Table:
    data = [list(df.columns)] + df.astype(str).values.tolist()
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(_TABLE_STYLE)
    return table


def _chart_image(filename: str, width_cm: float = 16) -> Image:
    path = os.path.join(config.GRAPHS_DIR, filename)
    img = Image(path)
    aspect = img.imageHeight / float(img.imageWidth)
    img.drawWidth = width_cm * cm
    img.drawHeight = width_cm * cm * aspect
    return img


def _chart_with_caption(filename: str, caption_text: str, width_cm: float = 16) -> KeepTogether:
    img = _chart_image(filename, width_cm=width_cm)
    caption = Paragraph(caption_text, _styles["Caption"])
    return KeepTogether([img, caption])

def build_story(df: pd.DataFrame, results: dict) -> list:
    yearly = results["yearly_performance"]
    sentiment = results["sentiment_breakdown"]
    sectors = results["sector_frequency"]
    volatile_days = results["most_volatile_days"]

    df_sorted = df.sort_values("Date")
    start_date = df_sorted["Date"].min().strftime("%d %b %Y")
    end_date = df_sorted["Date"].max().strftime("%d %b %Y")
    start_close = df_sorted["Close"].iloc[0]
    end_close = df_sorted["Close"].iloc[-1]
    overall_growth = (end_close - start_close) / start_close * 100
    avg_vix = df["India_VIX"].mean()
    top_sector_name = sectors.iloc[0]["Top_Sector"]

    story = []

    # --- Title ---
    story.append(Paragraph("NIFTY50 Historical Trend &amp; Volatility Analysis", _styles["ReportTitle"]))
    story.append(Paragraph(f"Analysis period: {start_date} &ndash; {end_date}", _styles["ReportSubtitle"]))

    story.append(Paragraph("1. Overview", _styles["SectionHeading"]))
    story.append(Paragraph(
        f"This report analyzes NIFTY50 index data from <b>{start_date}</b> to <b>{end_date}</b> "
        f"({len(df):,} trading days). Over this period, the index moved from "
        f"<b>{_fmt(start_close)}</b> to <b>{_fmt(end_close)}</b>, an overall change of "
        f"<b>{_fmt(overall_growth)}%</b>. The average India VIX (volatility/fear index) "
        f"over the period was <b>{_fmt(avg_vix)}</b>.",
        _styles["Body"],
    ))

    # --- Yearly performance ---
    story.append(Paragraph("2. Yearly Performance", _styles["SectionHeading"]))
    yearly_table_df = yearly[["Year", "Avg_Close", "Year_Return_Pct", "Avg_India_VIX", "Trading_Days"]].copy()
    yearly_table_df["Year"] = yearly_table_df["Year"].astype(int)
    yearly_table_df["Avg_Close"] = yearly_table_df["Avg_Close"].map(lambda v: _fmt(v))
    yearly_table_df["Year_Return_Pct"] = yearly_table_df["Year_Return_Pct"].map(lambda v: f"{_fmt(v)}%")
    yearly_table_df["Avg_India_VIX"] = yearly_table_df["Avg_India_VIX"].map(lambda v: _fmt(v))
    yearly_table_df.columns = ["Year", "Avg Close", "Year Return %", "Avg VIX", "Trading Days"]
    story.append(_df_to_table(yearly_table_df, col_widths=[2.5 * cm, 3.5 * cm, 3.5 * cm, 3 * cm, 3.5 * cm]))
    story.append(Spacer(1, 10))
    story.append(_chart_with_caption("02_bar_yearly_return.png", "Figure 1: NIFTY50 yearly return (%).", width_cm=15))
    story.append(Spacer(1, 10))

    # --- Price trend ---
    story.append(Paragraph("3. Price Trend", _styles["SectionHeading"]))
    story.append(Paragraph(
        "The chart below shows the Close price alongside its 50-day and 200-day moving "
        "averages, which are commonly used to identify longer-term uptrends and downtrends.",
        _styles["Body"],
    ))
    story.append(_chart_with_caption(
        "03_line_close_price_trend.png",
        "Figure 2: Close price with 50-day and 200-day moving averages.",
        width_cm=15,
    ))

    # --- Volatility & sentiment ---
    story.append(Paragraph("4. Volatility &amp; Sentiment", _styles["SectionHeading"]))
    sentiment_table_df = sentiment.copy()
    sentiment_table_df["Num_Days"] = sentiment_table_df["Num_Days"].astype(int)
    sentiment_table_df["Avg_India_VIX"] = sentiment_table_df["Avg_India_VIX"].map(lambda v: _fmt(v))
    sentiment_table_df["Avg_Daily_Return_Pct"] = sentiment_table_df["Avg_Daily_Return_Pct"].map(lambda v: f"{_fmt(v, 4)}%")
    sentiment_table_df.columns = ["Sentiment", "Num Days", "Avg VIX", "Avg Daily Return %"]
    story.append(_df_to_table(sentiment_table_df, col_widths=[4 * cm, 3 * cm, 3 * cm, 4.5 * cm]))
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    story.append(_chart_with_caption(
        "01_histogram_daily_returns.png", "Figure 3: Distribution of daily returns.", width_cm=13,
    ))
    story.append(Spacer(1, 8))
    story.append(_chart_with_caption(
        "05_scatter_vix_vs_return.png",
        "Figure 4: India VIX vs daily return, colored by sentiment.",
        width_cm=13,
    ))
    story.append(Spacer(1, 8))

    story.append(_chart_with_caption(
        "06_boxplot_return_by_year.png", "Figure 5: Daily return distribution by year.", width_cm=15,
    ))
    story.append(Spacer(1, 10))

    # --- Sector trends ---
    story.append(Paragraph("5. Sector Trends", _styles["SectionHeading"]))
    story.append(Paragraph(
        f"<b>{top_sector_name}</b> was the most frequent top-performing sector over the "
        f"analysis period.",
        _styles["Body"],
    ))
    story.append(_chart_with_caption(
        "04_pie_top_sectors.png", "Figure 6: Share of days each sector was the top performer.", width_cm=10,
    ))
    story.append(Spacer(1, 10))

    # --- Correlations ---
    story.append(Paragraph("6. Relationships Between Indicators", _styles["SectionHeading"]))
    story.append(Paragraph(
        "The heatmap and pairplot below show how Close price, Volume, RSI, India VIX and "
        "Daily Return relate to one another.",
        _styles["Body"],
    ))
    story.append(_chart_with_caption(
        "07_heatmap_correlation.png", "Figure 7: Correlation heatmap between key indicators.", width_cm=13,
    ))

    story.append(PageBreak())

    story.append(_chart_with_caption(
        "08_pairplot_key_indicators.png",
        "Figure 8: Pairwise relationships between key indicators.",
        width_cm=15,
    ))

    # --- Most volatile days ---
    story.append(Paragraph("7. Most Volatile Trading Days", _styles["SectionHeading"]))
    volatile_table_df = volatile_days.copy()
    volatile_table_df["Date"] = volatile_table_df["Date"].apply(
        lambda d: d.strftime("%d %b %Y") if hasattr(d, "strftime") else d
    )
    volatile_table_df["Close"] = volatile_table_df["Close"].map(lambda v: _fmt(v))
    volatile_table_df["Daily_Return_Pct_Recomputed"] = volatile_table_df["Daily_Return_Pct_Recomputed"].map(lambda v: f"{_fmt(v)}%")
    volatile_table_df["India_VIX"] = volatile_table_df["India_VIX"].map(lambda v: _fmt(v))
    volatile_table_df.columns = ["Date", "Close", "Daily Return %", "India VIX", "Sentiment"]
    story.append(_df_to_table(volatile_table_df, col_widths=[3 * cm, 2.7 * cm, 3.3 * cm, 2.5 * cm, 3 * cm]))

    # --- Key takeaways ---
    story.append(Paragraph("8. Key Takeaways", _styles["SectionHeading"]))
    takeaways = [
        f"Over the full period, NIFTY50 changed by <b>{_fmt(overall_growth)}%</b>.",
        f"Average volatility (India VIX) stayed around <b>{_fmt(avg_vix)}</b>.",
        f"<b>{top_sector_name}</b> led as the top sector most often.",
        "Volatility (return swings) tends to cluster around days with high India VIX, "
        "visible in the scatter plot above.",
        "See outputs/analysis/business_insights.txt for the full plain-language summary "
        "behind every figure in this report.",
    ]
    for point in takeaways:
        story.append(Paragraph(f"&bull; {point}", _styles["Body"]))

    return story


def generate_pdf_report(df: pd.DataFrame, results: dict, filename: str = "NIFTY50_Report.pdf") -> str:
    path = os.path.join(config.REPORT_DIR, filename)
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title="NIFTY50 Historical Trend & Volatility Analysis",
    )
    story = build_story(df, results)
    doc.build(story)
    print(f"Saved PDF report -> {path}")
    return path


# Keep the old function name available too, in case other code calls it.
def generate_report(df: pd.DataFrame, results: dict) -> str:
    return generate_pdf_report(df, results)


if __name__ == "__main__":
    from src.data_loader import load_processed_csv
    from src.analysis import run_all_analysis

    featured_df = load_processed_csv(config.FEATURED_CSV_FILE)
    analysis_results = run_all_analysis(featured_df)
    generate_pdf_report(featured_df, analysis_results)
