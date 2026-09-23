-- =====================================================================
-- 05_analysis_queries.sql
-- More advanced analytical queries: window functions, running totals,
-- and year-over-year comparisons -- good practice for real interview-
-- style SQL questions.
-- =====================================================================

USE nifty50_db;

-- 1. Running 7-day average Close price using a window function
SELECT
    Date,
    Close,
    ROUND(AVG(Close) OVER (
        ORDER BY Date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS Rolling_7Day_Avg_Close
FROM nifty50_prices
ORDER BY Date;

-- 2. Rank each year by its total return (best year to worst year)
SELECT
    Year,
    Year_Return_Pct,
    RANK() OVER (ORDER BY Year_Return_Pct DESC) AS Return_Rank
FROM (
    SELECT
        Year,
        ROUND(
            (MAX(CASE WHEN rn_last = 1 THEN Close END) -
             MAX(CASE WHEN rn_first = 1 THEN Close END))
            / MAX(CASE WHEN rn_first = 1 THEN Close END) * 100
        , 2) AS Year_Return_Pct
    FROM (
        SELECT
            Year, Date, Close,
            ROW_NUMBER() OVER (PARTITION BY Year ORDER BY Date ASC)  AS rn_first,
            ROW_NUMBER() OVER (PARTITION BY Year ORDER BY Date DESC) AS rn_last
        FROM nifty50_prices
    ) AS ranked_days
    GROUP BY Year
) AS yearly_returns
ORDER BY Return_Rank;

-- 3. Month-over-month change in average Close price
SELECT
    Year, Month_Num, Month_Name,
    ROUND(AVG(Close), 2) AS Avg_Close,
    ROUND(
        AVG(Close) - LAG(AVG(Close)) OVER (ORDER BY Year, Month_Num)
    , 2) AS Change_Vs_Prev_Month
FROM nifty50_prices
GROUP BY Year, Month_Num, Month_Name
ORDER BY Year, Month_Num;

-- 4. Longest streak of consecutive "Bullish" days
--    (classic SQL gaps-and-islands technique)
WITH flagged AS (
    SELECT
        Date, Market_Sentiment,
        ROW_NUMBER() OVER (ORDER BY Date) -
        ROW_NUMBER() OVER (PARTITION BY Market_Sentiment ORDER BY Date) AS grp
    FROM nifty50_prices
)
SELECT
    Market_Sentiment,
    MIN(Date) AS Streak_Start,
    MAX(Date) AS Streak_End,
    COUNT(*)  AS Streak_Length
FROM flagged
WHERE Market_Sentiment = 'Bullish'
GROUP BY Market_Sentiment, grp
ORDER BY Streak_Length DESC
LIMIT 5;

-- 5. Days where RSI signals "overbought" (>70) or "oversold" (<30)
SELECT
    Date, Close, RSI_14,
    CASE
        WHEN RSI_14 > 70 THEN 'Overbought'
        WHEN RSI_14 < 30 THEN 'Oversold'
        ELSE 'Normal'
    END AS RSI_Signal
FROM nifty50_prices
WHERE RSI_14 > 70 OR RSI_14 < 30
ORDER BY Date;
