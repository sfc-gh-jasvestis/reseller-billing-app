-- =============================================================================
-- SCHEMA VERIFICATION SCRIPT
-- =============================================================================
-- Run this script to verify the exact columns available in PARTNER_CONTRACT_ITEMS
-- and validate the calculations used in the Contract Usage Report
-- =============================================================================

-- Step 1: Show all columns in PARTNER_CONTRACT_ITEMS view
-- This will list all available columns and their data types
SELECT 
    '1. PARTNER_CONTRACT_ITEMS Schema' AS step,
    'Checking available columns...' AS description;

SHOW COLUMNS IN VIEW SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS;

-- Alternative method using INFORMATION_SCHEMA
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION
FROM SNOWFLAKE.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'BILLING'
  AND TABLE_NAME = 'PARTNER_CONTRACT_ITEMS'
ORDER BY ORDINAL_POSITION;

-- =============================================================================
-- Step 2: Check if CAPACITY_TYPE_NAME specifically exists
-- =============================================================================
SELECT 
    '2. Check CAPACITY_TYPE_NAME' AS step,
    'Verifying if CAPACITY_TYPE_NAME column exists...' AS description;

SELECT COUNT(*) as column_exists
FROM SNOWFLAKE.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'BILLING'
  AND TABLE_NAME = 'PARTNER_CONTRACT_ITEMS'
  AND COLUMN_NAME = 'CAPACITY_TYPE_NAME';
-- If this returns 0, the column does not exist

-- =============================================================================
-- Step 3: Sample data from PARTNER_CONTRACT_ITEMS
-- =============================================================================
SELECT 
    '3. Sample Contract Data' AS step,
    'Viewing actual data to understand structure...' AS description;

-- Get sample data (limited to 5 rows)
SELECT *
FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS
LIMIT 5;

-- =============================================================================
-- Step 4: Check related columns that might be used instead
-- =============================================================================
SELECT 
    '4. Search for CAPACITY-related columns' AS step,
    'Looking for alternative column names...' AS description;

SELECT COLUMN_NAME
FROM SNOWFLAKE.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'BILLING'
  AND TABLE_NAME = 'PARTNER_CONTRACT_ITEMS'
  AND (COLUMN_NAME LIKE '%CAPACITY%' OR COLUMN_NAME LIKE '%TYPE%')
ORDER BY COLUMN_NAME;

-- =============================================================================
-- Step 5: Verify calculation columns used in the app
-- =============================================================================
SELECT 
    '5. Verify Calculation Columns' AS step,
    'Checking columns used in Contract Usage Report...' AS description;

-- Check if all required columns exist for the calculation
SELECT 
    SOLD_TO_CUSTOMER_NAME,
    SOLD_TO_CONTRACT_NUMBER,
    CONTRACT_ITEM_START_DATE,
    CONTRACT_ITEM_END_DATE,
    CONTRACTED_AMOUNT,
    CURRENCY,
    ROLLOVER_AMOUNT,
    FREE_USAGE_AMOUNT,
    CONTRACT_ITEM_ID,
    -- Calculate total capacity as used in the app
    (CONTRACTED_AMOUNT + COALESCE(ROLLOVER_AMOUNT, 0) + COALESCE(FREE_USAGE_AMOUNT, 0)) AS TOTAL_CAPACITY
FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS
WHERE CONTRACT_ITEM_END_DATE >= CURRENT_DATE
ORDER BY SOLD_TO_CUSTOMER_NAME, CONTRACT_ITEM_START_DATE DESC
LIMIT 10;

-- =============================================================================
-- Step 6: Verify the calculation logic
-- =============================================================================
SELECT 
    '6. Validate Calculation Logic' AS step,
    'Testing the capacity calculation formula...' AS description;

-- Verify that the calculation used in calculate_contract_usage_metrics is correct
-- Formula: capacity_purchased = CONTRACTED_AMOUNT + ROLLOVER_AMOUNT + FREE_USAGE_AMOUNT
SELECT 
    SOLD_TO_CUSTOMER_NAME,
    CONTRACT_ITEM_ID,
    CONTRACT_ITEM_START_DATE,
    CONTRACT_ITEM_END_DATE,
    CONTRACTED_AMOUNT,
    COALESCE(ROLLOVER_AMOUNT, 0) AS ROLLOVER_AMOUNT,
    COALESCE(FREE_USAGE_AMOUNT, 0) AS FREE_USAGE_AMOUNT,
    (CONTRACTED_AMOUNT + COALESCE(ROLLOVER_AMOUNT, 0) + COALESCE(FREE_USAGE_AMOUNT, 0)) AS TOTAL_CAPACITY_PURCHASED,
    CURRENCY,
    DATEDIFF('day', CONTRACT_ITEM_START_DATE, CONTRACT_ITEM_END_DATE) AS CONTRACT_DURATION_DAYS
FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS
WHERE CONTRACT_ITEM_END_DATE >= CURRENT_DATE
ORDER BY SOLD_TO_CUSTOMER_NAME;

-- =============================================================================
-- Step 7: Check for any NULL values that might affect calculations
-- =============================================================================
SELECT 
    '7. NULL Value Check' AS step,
    'Checking for NULL values in key columns...' AS description;

SELECT 
    COUNT(*) AS total_contracts,
    COUNT(CONTRACTED_AMOUNT) AS has_contracted_amount,
    COUNT(ROLLOVER_AMOUNT) AS has_rollover_amount,
    COUNT(FREE_USAGE_AMOUNT) AS has_free_usage_amount,
    COUNT(CURRENCY) AS has_currency,
    SUM(CASE WHEN CONTRACTED_AMOUNT IS NULL THEN 1 ELSE 0 END) AS null_contracted_amount,
    SUM(CASE WHEN ROLLOVER_AMOUNT IS NULL THEN 1 ELSE 0 END) AS null_rollover_amount,
    SUM(CASE WHEN FREE_USAGE_AMOUNT IS NULL THEN 1 ELSE 0 END) AS null_free_usage_amount
FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS
WHERE CONTRACT_ITEM_END_DATE >= CURRENT_DATE;

-- =============================================================================
-- RESULTS INTERPRETATION
-- =============================================================================
/*
WHAT TO LOOK FOR:

Step 1-2: 
  - If CAPACITY_TYPE_NAME doesn't appear in the column list, it confirms the column doesn't exist
  - Look for any similar column names that might be the correct alternative

Step 3-4:
  - Review sample data to understand what information is available
  - Identify if there's a different column that provides capacity type information

Step 5-6:
  - Verify that all required columns for the calculation are present and contain data
  - Confirm the formula: TOTAL_CAPACITY = CONTRACTED_AMOUNT + ROLLOVER_AMOUNT + FREE_USAGE_AMOUNT
  - This is used in line 449 of streamlit_app.py

Step 7:
  - Check for NULL values that might cause calculation issues
  - The app uses COALESCE to handle NULLs (lines 806-808), which is correct

NEXT STEPS:
  - If CAPACITY_TYPE_NAME is truly missing, we can safely remove it (already done)
  - If you need capacity type information, we'll need to identify an alternative column
  - Verify the calculation formula matches your business requirements
*/

