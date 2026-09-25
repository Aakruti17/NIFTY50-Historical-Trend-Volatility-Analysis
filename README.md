# NIFTY50 Historical Trend & Volatility Analysis

A complete, beginner-friendly data analytics project: Python (Pandas/NumPy) for cleaning and
EDA, Matplotlib/Seaborn for visualization, MySQL for storage, SQL for querying, and a Power BI
dashboard for presentation.

---

## 1. What is NIFTY50, and why this dataset?

The **NIFTY 50** is India's benchmark stock market index, maintained by the **National Stock
Exchange (NSE)** of India. It tracks the performance of the 50 largest, most liquid companies
listed on the NSE across sectors like Banking, IT, Energy, FMCG, Auto, and Pharma. It plays a
role in the Indian market similar to the S&P 500 in the US -- a single number that gives a
quick read on "how the market is doing."

This project uses a synthetic-but-realistic NIFTY50 daily dataset because it's:
- **Time-series data** -- the same kind of data used in real trading, investing, and finance
  analytics roles.
- **Deliberately messy** -- it comes with intentional data-quality problems (see below), so
  cleaning it is real practice, not just a formality before the "fun part."
- **Multi-skill** -- one dataset touches date handling, text cleaning, outlier detection,
  feature engineering, correlation analysis, SQL querying, and several chart types, making it a
  strong, complete portfolio project.

## 2. Dataset columns explained

| Column | Meaning |
|---|---|
| `Date` | Trading date |
| `Day_of_Week` / `Month` / `Year` | Calendar breakdown of the date |
| `Open` / `High` / `Low` / `Close` | The index's opening, highest, lowest, and closing value that day |
| `Prev_Close` | Previous trading day's closing value |
| `Daily_Return_Pct` | % change vs. previous close: `(Close - Prev_Close) / Prev_Close * 100` |
| `Volume_Shares_Mn` | Shares traded that day, in millions |
| `Turnover_Cr` | Total value traded that day, in INR Crores (~ `Volume * Price / 100`) |
| `50_Day_MA` / `200_Day_MA` | 50-day / 200-day moving average of Close (smooths short-term noise to reveal the underlying trend) |
| `RSI_14` | 14-day Relative Strength Index, 0-100 (>70 ~ "overbought", <30 ~ "oversold") |
| `India_VIX` | India's volatility/"fear" index -- higher means bigger expected price swings |
| `Advance_Decline_Ratio` | Ratio of advancing to declining stocks that day |
| `Top_Sector` | Best-performing sector of the day |
| `Market_Sentiment` | Overall Bullish / Bearish / Neutral label for the day |
| `Is_Market_Holiday` | Whether the date was a market holiday |

### Data quality issues fixed during cleaning
1. Missing values scattered across many columns
2. Duplicate rows
3. Inconsistent date formats (`DD-MM-YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`, `DD Mon YYYY`)
4. Inconsistent text casing and stray whitespace
5. Spelling typos in `Top_Sector` (`Bankng`, `Pharam`, `Realety`, ...)
6. Numbers stored as text with thousand-separator commas
7. Outlier / data-entry-error values in price columns (decimal-shift and sign-flip errors)
8. Negative values in Volume/Turnover that should always be positive

## 3. Project structure

```
NIFTY50_Analysis_Project/
├── data/
│   ├── raw/                         # Original Excel file (never modified)
│   └── processed/                   # Cleaned + feature-engineered CSVs (generated)
├── outputs/
│   ├── analysis/                    # ONE file: business_insights.txt (generated)
│   ├── graphs/                      # All PNG charts (generated)
│   └── report/                      # ONE file: NIFTY50_Report.pdf (generated)
├── src/
│   ├── config.py                    # All file paths + DB settings in one place
│   ├── data_loader.py               # Load Excel / CSV / MySQL data
│   ├── data_cleaning.py             # Fixes every data-quality issue above
│   ├── data_transformation.py       # Feature engineering (calendar, volatility, trend labels)
│   ├── analysis.py                  # EDA calculations + writes business_insights.txt
│   ├── visualization.py             # All 8 chart types (Matplotlib + Seaborn)
│   ├── report.py                    # Builds the final PDF report (ReportLab)
│   └── db_connector.py              # MySQL connection script (SQLAlchemy + mysql-connector)
├── sql/
│   ├── 01_create_tables.sql         # Table creation (schema + a small sector lookup table)
│   ├── 02_load_data.sql             # Notes + LOAD DATA INFILE example
│   ├── 03_data_extraction_queries.sql  # SELECT / WHERE / ORDER BY examples
│   ├── 04_joins_aggregations.sql    # GROUP BY + JOIN examples
│   └── 05_analysis_queries.sql      # Window functions, rankings, streaks, RSI signals
├── nifty.pbix
├── main.py                          # Runs the entire pipeline end-to-end
├── requirements.txt
└── README.md
```

## 4. How to run this project

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the whole pipeline
```bash
python main.py
```
This loads the raw Excel file, cleans it, engineers features, runs the analysis, generates every
chart, and writes the final report -- all in one command. You'll find the results in:
- `data/processed/` -- cleaned + feature-engineered CSVs
- `outputs/analysis/business_insights.txt` -- one plain-English business insights file
- `outputs/graphs/` -- all 8 charts as PNGs
- `outputs/report/NIFTY50_Report.pdf` -- the final polished PDF report (built with ReportLab)

### Step 3 (optional): Push the cleaned data into MySQL
1. Install and start MySQL Server locally.
2. Create the database and table:
   ```bash
   mysql -u root -p < sql/01_create_tables.sql
   ```
3. Set your credentials as environment variables (see `src/config.py` for names), then run:
   ```bash
   python main.py --with-db
   ```
   This uploads the final cleaned dataset straight into the `nifty50_prices` table.
4. Try the queries in `sql/03_data_extraction_queries.sql`, `sql/04_joins_aggregations.sql`, and
   `sql/05_analysis_queries.sql` in MySQL Workbench or the `mysql` CLI.

### Step 4 (optional): Explore interactively in Jupyter
```bash
jupyter notebook notebooks/NIFTY50_EDA.ipynb
```
The notebook mirrors `main.py`'s pipeline step by step, with explanations for every decision, so
it's the best place to actually *learn* from this project rather than just run it.

### Step 5 (optional): Build the Power BI dashboard
Follow `powerbi/PowerBI_Dashboard_Guide.md` -- it walks through importing
`data/processed/nifty50_features.csv` (or the MySQL table), fixing data types, and building four
dashboard pages (Overview, Returns & Volatility, Sectors & Sentiment, Correlations).

## 5. Tech stack

| Purpose | Tool |
|---|---|
| Data cleaning & EDA | Python, Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Notebook environment | Jupyter |
| Database | MySQL (via `mysql-connector-python` + SQLAlchemy) |
| Querying | SQL (joins, aggregations, window functions) |
| Dashboard | Power BI |

## 6. Notes for beginners

- **Why separate `src/` files instead of one big script?** Each file has one job (loading,
  cleaning, analyzing, visualizing...). This is called *separation of concerns* -- it makes the
  project much easier to read, test, and reuse pieces of later.
- **Why keep `data/raw/` untouched?** So you can always re-run the pipeline from scratch and get
  the same result, and so you never accidentally lose the original data.
- **Why one `.txt` file for insights instead of several CSVs?** A folder full of separate
  spreadsheets forces a reader to open and cross-reference many files. `business_insights.txt`
  turns the same numbers into short, plain-English sentences a business reader can scan in a
  couple of minutes -- while the underlying tables still live in memory during the pipeline run
  and feed both the charts and the PDF report.
- **Why ReportLab for the PDF?** ReportLab (`src/report.py`) builds the report as a list of
  "flowables" (paragraphs, tables, images) and lays them out onto A4 pages automatically --
  no manual coordinates needed -- producing a polished, presentation-ready PDF with the same
  tables and charts referenced in the insights file.
- **A note on the analysis itself:** this project is for learning data-analytics skills. It is
  not investment advice, and NIFTY50 trend patterns from this (partly synthetic) dataset should
  not be used to make real financial decisions.
