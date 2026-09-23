-- =====================================================================
-- 02_load_data.sql
-- Loading the cleaned data into MySQL.
--
-- In this project, loading is normally done from Python with:
--     src/db_connector.py -> push_dataframe_to_mysql()
-- (this uses pandas' to_sql, which is far less error-prone than
-- hand-writing thousands of INSERT statements for a time-series file).
--
-- If you would rather load the CSV file directly inside MySQL, you can
-- use LOAD DATA INFILE, as shown below. Update the file path for your
-- own machine, and make sure secure_file_priv allows it (run
-- `SHOW VARIABLES LIKE 'secure_file_priv';` to check).
-- =====================================================================

USE nifty50_db;

-- Example only -- adjust the path to where you exported the cleaned CSV
-- (data/processed/nifty50_features.csv), and make sure the CSV's column
-- order matches the table's column order exactly.

-- LOAD DATA INFILE '/path/to/data/processed/nifty50_features.csv'
-- INTO TABLE nifty50_prices
-- FIELDS TERMINATED BY ','
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (Date, Day_of_Week, Month, Year, Open, High, Low, Close, Prev_Close,
--  Daily_Return_Pct, Volume_Shares_Mn, Turnover_Cr, `50_Day_MA`, `200_Day_MA`,
--  RSI_14, India_VIX, Advance_Decline_Ratio, Top_Sector, Market_Sentiment,
--  Is_Market_Holiday, Month_Num, Month_Name, Quarter, Daily_Range,
--  Daily_Range_Pct, Rolling_Volatility_20D, Cumulative_Return_Pct,
--  MA_Trend, VIX_Risk_Bucket);

-- Quick sanity check after loading (from Python or MySQL Workbench):
SELECT COUNT(*) AS total_rows FROM nifty50_prices;
SELECT * FROM nifty50_prices ORDER BY Date LIMIT 5;
