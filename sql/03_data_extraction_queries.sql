-- =====================================================================
-- 03_data_extraction_queries.sql
-- Simple SELECT / WHERE / ORDER BY queries to pull specific slices of
-- the data -- the kind of queries you'd use to answer quick questions
-- or feed a specific chart/report section.
-- =====================================================================

USE nifty50_db;

-- 1. All trading days in a specific year
SELECT *
FROM nifty50_prices
WHERE Year = 2023
ORDER BY Date;

-- 2. All days where the market was Bearish and highly volatile (VIX > 20)
SELECT Date, Close, Daily_Return_Pct, India_VIX, Market_Sentiment
FROM nifty50_prices
WHERE Market_Sentiment = 'Bearish' AND India_VIX > 20
ORDER BY India_VIX DESC;

-- 3. The 10 single best (highest return) trading days of all time
SELECT Date, Close, Daily_Return_Pct
FROM nifty50_prices
ORDER BY Daily_Return_Pct DESC
LIMIT 10;

-- 4. The 10 single worst (lowest return) trading days of all time
SELECT Date, Close, Daily_Return_Pct
FROM nifty50_prices
ORDER BY Daily_Return_Pct ASC
LIMIT 10;

-- 5. All days where Banking was the top sector
SELECT Date, Close, Top_Sector, Market_Sentiment
FROM nifty50_prices
WHERE Top_Sector = 'Banking'
ORDER BY Date;

-- 6. Days in an "Uptrend" (50-day MA above 200-day MA) during 2022
SELECT Date, Close, `50_Day_MA`, `200_Day_MA`, MA_Trend
FROM nifty50_prices
WHERE MA_Trend = 'Uptrend' AND Year = 2022
ORDER BY Date;
