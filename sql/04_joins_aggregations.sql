-- =====================================================================
-- 04_joins_aggregations.sql
-- GROUP BY aggregations, and a JOIN example against the sector_lookup
-- dimension table created in 01_create_tables.sql.
-- =====================================================================

USE nifty50_db;

-- 1. Average close price and average daily return per year
SELECT
    Year,
    ROUND(AVG(Close), 2)               AS Avg_Close,
    ROUND(AVG(Daily_Return_Pct), 4)    AS Avg_Daily_Return_Pct,
    ROUND(AVG(India_VIX), 2)           AS Avg_VIX,
    COUNT(*)                           AS Trading_Days
FROM nifty50_prices
GROUP BY Year
ORDER BY Year;

-- 2. Average return and volume per month name (seasonality check)
SELECT
    Month_Name,
    ROUND(AVG(Daily_Return_Pct), 4)     AS Avg_Daily_Return_Pct,
    ROUND(AVG(Volume_Shares_Mn), 2)     AS Avg_Volume_Shares_Mn
FROM nifty50_prices
GROUP BY Month_Name
ORDER BY FIELD(Month_Name, 'January','February','March','April','May','June',
                            'July','August','September','October','November','December');

-- 3. Number of days per Market_Sentiment, and their average VIX
SELECT
    Market_Sentiment,
    COUNT(*)                    AS Num_Days,
    ROUND(AVG(India_VIX), 2)    AS Avg_VIX
FROM nifty50_prices
GROUP BY Market_Sentiment
ORDER BY Num_Days DESC;

-- 4. JOIN example: bring in each sector's broader industry "group"
--    from the sector_lookup dimension table, then aggregate.
SELECT
    sl.sector_group,
    COUNT(*)                              AS Days_As_Top_Sector,
    ROUND(AVG(np.Daily_Return_Pct), 4)    AS Avg_Return_On_Those_Days
FROM nifty50_prices AS np
INNER JOIN sector_lookup AS sl
    ON np.Top_Sector = sl.sector_name
GROUP BY sl.sector_group
ORDER BY Days_As_Top_Sector DESC;

-- 5. VIX risk bucket vs. average return (does higher fear mean bigger swings?)
SELECT
    VIX_Risk_Bucket,
    COUNT(*)                                  AS Num_Days,
    ROUND(AVG(ABS(Daily_Return_Pct)), 4)      AS Avg_Absolute_Return_Pct
FROM nifty50_prices
GROUP BY VIX_Risk_Bucket
ORDER BY Avg_Absolute_Return_Pct DESC;
