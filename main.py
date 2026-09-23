import argparse

from src import config
from src.data_loader import load_raw_excel, save_processed_csv
from src.data_cleaning import clean_dataset
from src.data_transformation import transform_dataset
from src.analysis import run_all_analysis, generate_business_insights
from src.visualization import generate_all_visualizations
from src.report import generate_pdf_report


def run_pipeline(push_to_db: bool = False) -> None:
    print("=" * 60)
    print(" NIFTY50 HISTORICAL TREND & VOLATILITY ANALYSIS PIPELINE")
    print("=" * 60)

    # 1. Load
    raw_df = load_raw_excel()

    # 2. Clean
    cleaned_df = clean_dataset(raw_df)
    save_processed_csv(cleaned_df, config.CLEANED_CSV_FILE)

    # 3. Transform 
    featured_df = transform_dataset(cleaned_df)
    save_processed_csv(featured_df, config.FEATURED_CSV_FILE)

    # 4. Analyze
    results = run_all_analysis(featured_df)

    # 5. Visualize
    generate_all_visualizations(featured_df, results)

    # 6. Business insights (single text file) + PDF report (uses the charts above)
    generate_business_insights(featured_df, results)
    generate_pdf_report(featured_df, results)

    # 7. Optional: push to MySQL
    if push_to_db:
        from src.db_connector import push_dataframe_to_mysql
        push_dataframe_to_mysql(featured_df)

    print("\nPipeline finished successfully!")
    print(f"  - Cleaned data:   {config.CLEANED_CSV_FILE}")
    print(f"  - Featured data:  {config.FEATURED_CSV_FILE}")
    print(f"  - Analysis file:  {config.ANALYSIS_DIR}/business_insights.txt")
    print(f"  - Charts:         {config.GRAPHS_DIR}")
    print(f"  - Report (PDF):   {config.REPORT_DIR}/NIFTY50_Report.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the NIFTY50 analysis pipeline.")
    parser.add_argument("--with-db", action="store_true",
                         help="Also push the final cleaned data into the MySQL database.")
    args = parser.parse_args()

    run_pipeline(push_to_db=args.with_db)
