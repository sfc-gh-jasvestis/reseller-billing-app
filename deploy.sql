-- =============================================================================
-- COMPLETE DEPLOYMENT - Snowflake Reseller Billing Dashboard
-- =============================================================================
-- This script creates EVERYTHING: warehouse, role, permissions, and Streamlit app
-- Use this if you need to set up a dedicated role with BILLING schema access
--
-- For minimal deployment (if users already have BILLING access), see MINIMAL_DEPLOY.sql
--
-- PREREQUISITES:
-- 1. ACCOUNTADMIN role or equivalent permissions
-- 2. Access to SNOWFLAKE.BILLING schema (enabled by Snowflake Support)
-- 3. Streamlit in Snowflake feature enabled
-- =============================================================================

-- =============================================================================
-- STEP 1: VERIFY PREREQUISITES
-- =============================================================================

-- Test BILLING schema access (uncomment to verify before deployment)
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY LIMIT 1;
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_REMAINING_BALANCE_DAILY LIMIT 1;
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS LIMIT 1;
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_RATE_SHEET_DAILY LIMIT 1;

-- =============================================================================
-- STEP 2: CREATE INFRASTRUCTURE
-- =============================================================================

-- Create warehouse for the application
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for Billing Dashboard Streamlit app';

-- =============================================================================
-- STEP 3: SECURITY SETUP
-- =============================================================================
-- NOTE: The Streamlit app runs AS the viewing user (not as a service account)
-- These permissions are granted to the BILLING_DASHBOARD_USER role so that
-- users with this role can query the BILLING schema when viewing the dashboard

-- Create dedicated role for billing dashboard users
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER
    COMMENT = 'Role for users accessing the billing dashboard';

-- Grant necessary permissions for BILLING schema access
-- (Required because the app queries BILLING views as the logged-in user)
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;

-- Grant warehouse access
-- (Required for the app to execute queries)
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_USER;

-- =============================================================================
-- STEP 4: CREATE STREAMLIT APPLICATION
-- =============================================================================

-- Create the Streamlit application with embedded Python code
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
    COMMENT = 'Snowflake Credit Usage Dashboard for Reseller Customers'
AS
$$
-- COPY THE ENTIRE CONTENTS OF streamlit_app.py HERE --
-- The Python code will be embedded directly in this SQL statement
-- No need for file uploads or stages!
$$;

-- Grant usage on the Streamlit app
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;

-- =============================================================================
-- STEP 5: USER MANAGEMENT
-- =============================================================================

/*
Grant the role to specific users (replace 'username' with actual usernames):

GRANT ROLE BILLING_DASHBOARD_USER TO USER username1;
GRANT ROLE BILLING_DASHBOARD_USER TO USER username2;

Or grant to PUBLIC for broad access (development/testing):
GRANT ROLE BILLING_DASHBOARD_USER TO ROLE PUBLIC;
*/

-- =============================================================================
-- STEP 6: VERIFICATION
-- =============================================================================

-- Verify Streamlit app was created
SHOW STREAMLIT APPS;

-- Test access to BILLING views
SELECT 'PARTNER_USAGE_IN_CURRENCY_DAILY' as view_name, COUNT(*) as row_count 
FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY
UNION ALL
SELECT 'PARTNER_REMAINING_BALANCE_DAILY' as view_name, COUNT(*) as row_count 
FROM SNOWFLAKE.BILLING.PARTNER_REMAINING_BALANCE_DAILY
UNION ALL
SELECT 'PARTNER_CONTRACT_ITEMS' as view_name, COUNT(*) as row_count 
FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS
UNION ALL
SELECT 'PARTNER_RATE_SHEET_DAILY' as view_name, COUNT(*) as row_count 
FROM SNOWFLAKE.BILLING.PARTNER_RATE_SHEET_DAILY;

-- =============================================================================
-- DEPLOYMENT COMPLETE!
-- =============================================================================

SELECT 
    '✅ Simple Billing Dashboard deployment completed!' AS STATUS,
    'Next steps:' AS ACTION_REQUIRED,
    '1. Copy streamlit_app.py code into the CREATE STREAMLIT statement above' AS STEP_1,
    '2. Grant BILLING_DASHBOARD_USER role to users' AS STEP_2,
    '3. Access app at: Projects > Streamlit > billing_dashboard' AS STEP_3;

-- =============================================================================
-- MAINTENANCE COMMANDS
-- =============================================================================

/*
USEFUL COMMANDS:

-- Update the application code
ALTER STREAMLIT billing_dashboard SET MAIN_FILE = 'updated_code_here';

-- Check app details
DESC STREAMLIT billing_dashboard;

-- Monitor warehouse usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH' 
ORDER BY START_TIME DESC LIMIT 10;

-- Drop the application (if needed)
DROP STREAMLIT billing_dashboard;
DROP WAREHOUSE BILLING_DASHBOARD_WH;
*/