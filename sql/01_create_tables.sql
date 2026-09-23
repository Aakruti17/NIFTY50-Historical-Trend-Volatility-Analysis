-- =====================================================================
-- 01_create_tables.sql
-- Creates the database and the main table that will hold the cleaned
-- NIFTY50 data. If you use db_connector.py's push_dataframe_to_mysql()
-- with if_exists='replace', pandas will actually create this table for
-- you automatically -- this script is provided so you also have full,
-- explicit control over column types (useful for learning SQL, and for
-- Power BI which prefers well-typed columns).
-- =====================================================================

CREATE DATABASE IF NOT EXISTS nifty50_db;
USE nifty50_db;

DROP TABLE IF EXISTS nifty50_prices;

CREATE TABLE nifty50_prices (
    Date                        DATE,
    Day_of_Week                 VARCHAR(15),
    Month                       VARCHAR(15),
    Year                        INT,
    Open                        DECIMAL(12, 2),
    High                        DECIMAL(12, 2),
    Low                         DECIMAL(12, 2),
    Close                       DECIMAL(12, 2),
    Prev_Close                  DECIMAL(12, 2),
    Daily_Return_Pct            DECIMAL(8, 4),
    Volume_Shares_Mn            DECIMAL(14, 2),
    Turnover_Cr                 DECIMAL(14, 2),
    `50_Day_MA`                 DECIMAL(12, 2),
    `200_Day_MA`                DECIMAL(12, 2),
    RSI_14                      DECIMAL(6, 2),
    India_VIX                   DECIMAL(6, 2),
    Advance_Decline_Ratio       DECIMAL(6, 3),
    Top_Sector                  VARCHAR(50),
    Market_Sentiment            VARCHAR(20),
    Is_Market_Holiday           VARCHAR(5),
    Month_Num                   INT,
    Month_Name                  VARCHAR(15),
    Quarter                     INT,
    Daily_Range                 DECIMAL(12, 2),
    Daily_Range_Pct             DECIMAL(8, 4),
    Rolling_Volatility_20D      DECIMAL(8, 4),
    Cumulative_Return_Pct       DECIMAL(10, 4),
    MA_Trend                    VARCHAR(15),
    VIX_Risk_Bucket             VARCHAR(20),
    PRIMARY KEY (Date)
);

-- A small lookup/dimension table for sectors -- used to demonstrate a
-- JOIN in 04_joins_aggregations.sql. Feel free to expand this with real
-- sector metadata (index name, number of listed companies, etc.).
DROP TABLE IF EXISTS sector_lookup;

CREATE TABLE sector_lookup (
    sector_name   VARCHAR(50) PRIMARY KEY,
    sector_group  VARCHAR(30)
);

INSERT INTO sector_lookup (sector_name, sector_group) VALUES
    ('Banking', 'Financials'),
    ('Financial Services', 'Financials'),
    ('Finance', 'Financials'),
    ('IT', 'Technology'),
    ('Pharma', 'Healthcare'),
    ('Auto', 'Consumer'),
    ('FMCG', 'Consumer'),
    ('Realty', 'Real Estate'),
    ('Metal', 'Materials'),
    ('Energy', 'Energy');
