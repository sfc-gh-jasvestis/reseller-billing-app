-- =============================================================================
-- SNOWFLAKE RESELLER BILLING DASHBOARD - UNIFIED DEPLOYMENT SCRIPT
-- =============================================================================
-- This script deploys the complete Streamlit billing dashboard with all 
-- functionality, security, and infrastructure components.
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

-- Verify Streamlit support
-- SHOW STREAMLIT APPS;

-- =============================================================================
-- STEP 2: CREATE APPLICATION INFRASTRUCTURE
-- =============================================================================

-- Create database and schema for the application
CREATE DATABASE IF NOT EXISTS BILLING_APPS
    COMMENT = 'Database for Snowflake Reseller Billing Applications';

CREATE SCHEMA IF NOT EXISTS BILLING_APPS.STREAMLIT_APPS
    COMMENT = 'Schema for Streamlit billing applications';

-- Use the created schema
USE SCHEMA BILLING_APPS.STREAMLIT_APPS;

-- Create a stage to store the application files
CREATE OR REPLACE STAGE billing_dashboard_stage
    DIRECTORY = ( ENABLE = TRUE )
    COMMENT = 'Stage for Snowflake Reseller Billing Dashboard files';

-- Create warehouse for the application
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for Billing Dashboard Streamlit app';

-- =============================================================================
-- STEP 3: SECURITY AND PERMISSIONS SETUP
-- =============================================================================

-- Create dedicated role for billing dashboard users (recommended for production)
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER
    COMMENT = 'Role for users accessing the billing dashboard';

-- Create read-only role for view-only access
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_VIEWER
    COMMENT = 'Read-only role for billing dashboard viewers';

-- Grant necessary permissions for BILLING schema access to dashboard role
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;

-- Grant permissions to viewer role
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_VIEWER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_VIEWER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_VIEWER;

-- Grant warehouse and application database access to both roles
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_VIEWER;

GRANT USAGE ON DATABASE BILLING_APPS TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON DATABASE BILLING_APPS TO ROLE BILLING_DASHBOARD_VIEWER;

GRANT USAGE ON SCHEMA BILLING_APPS.STREAMLIT_APPS TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA BILLING_APPS.STREAMLIT_APPS TO ROLE BILLING_DASHBOARD_VIEWER;

-- Grant stage access for file management (admin only)
GRANT READ, WRITE ON STAGE billing_dashboard_stage TO ROLE BILLING_DASHBOARD_USER;
GRANT READ ON STAGE billing_dashboard_stage TO ROLE BILLING_DASHBOARD_VIEWER;

-- =============================================================================
-- STEP 4: OPTIONAL - GRANT TO PUBLIC (for broad access)
-- =============================================================================
-- Uncomment these lines if you want to grant access to all users via PUBLIC role
-- This is useful for development/testing environments

-- GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE PUBLIC;
-- GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE PUBLIC;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE PUBLIC;
-- GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE PUBLIC;
-- GRANT USAGE ON DATABASE BILLING_APPS TO ROLE PUBLIC;
-- GRANT USAGE ON SCHEMA BILLING_APPS.STREAMLIT_APPS TO ROLE PUBLIC;

-- =============================================================================
-- STEP 5: FILE UPLOAD INSTRUCTIONS
-- =============================================================================

/*
Upload your application files to the stage using one of these methods:

METHOD 1: SnowSQL (Recommended)
snowsql -c your_connection -q "PUT file://streamlit_app.py @BILLING_APPS.STREAMLIT_APPS.billing_dashboard_stage;"
snowsql -c your_connection -q "PUT file://requirements.txt @BILLING_APPS.STREAMLIT_APPS.billing_dashboard_stage;"

METHOD 2: Snowflake Web UI
1. Go to Data > Databases > BILLING_APPS > STREAMLIT_APPS > Stages
2. Click on billing_dashboard_stage
3. Upload files using the web interface

METHOD 3: Direct SQL Commands (adjust paths as needed)
PUT file:///path/to/streamlit_app.py @billing_dashboard_stage;
PUT file://requirements.txt @billing_dashboard_stage;

After uploading, verify files are present:
LIST @billing_dashboard_stage;
*/

-- =============================================================================
-- STEP 6: CREATE STREAMLIT APPLICATION
-- =============================================================================

-- Create the Streamlit application
CREATE OR REPLACE STREAMLIT billing_dashboard
    ROOT_LOCATION = '@billing_dashboard_stage'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
    COMMENT = 'Snowflake Credit Usage Dashboard for Reseller Customers - Full Featured';

-- Grant usage on the Streamlit app to roles
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_VIEWER;

-- =============================================================================
-- STEP 7: USER MANAGEMENT (CUSTOMIZE AS NEEDED)
-- =============================================================================

/*
Grant roles to specific users (replace 'username' with actual usernames):

-- For full access users (can modify settings, export data)
GRANT ROLE BILLING_DASHBOARD_USER TO USER username1;
GRANT ROLE BILLING_DASHBOARD_USER TO USER username2;

-- For view-only users
GRANT ROLE BILLING_DASHBOARD_VIEWER TO USER username3;
GRANT ROLE BILLING_DASHBOARD_VIEWER TO USER username4;

-- Grant roles to other roles if needed
GRANT ROLE BILLING_DASHBOARD_VIEWER TO ROLE BILLING_DASHBOARD_USER;
*/

-- =============================================================================
-- STEP 8: CREATE HELPFUL VIEWS (OPTIONAL ENHANCEMENTS)
-- =============================================================================

-- Create a view for easier access to current month usage
CREATE OR REPLACE VIEW current_month_usage AS
SELECT 
    SOLD_TO_ORGANIZATION_NAME,
    SOLD_TO_CUSTOMER_NAME,
    ACCOUNT_NAME,
    USAGE_DATE,
    USAGE_TYPE,
    USAGE as CREDITS_USED,
    USAGE_IN_CURRENCY,
    CURRENCY,
    BALANCE_SOURCE
FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY
WHERE USAGE_DATE >= DATE_TRUNC('MONTH', CURRENT_DATE())
ORDER BY USAGE_DATE DESC, SOLD_TO_CUSTOMER_NAME;

-- Create a view for latest balances
CREATE OR REPLACE VIEW latest_balances AS
SELECT 
    SOLD_TO_ORGANIZATION_NAME,
    SOLD_TO_CUSTOMER_NAME,
    DATE as BALANCE_DATE,
    CURRENCY,
    FREE_USAGE_BALANCE,
    CAPACITY_BALANCE,
    ON_DEMAND_CONSUMPTION_BALANCE,
    ROLLOVER_BALANCE,
    (FREE_USAGE_BALANCE + CAPACITY_BALANCE + ROLLOVER_BALANCE) as TOTAL_AVAILABLE_BALANCE
FROM SNOWFLAKE.BILLING.PARTNER_REMAINING_BALANCE_DAILY
WHERE DATE = (SELECT MAX(DATE) FROM SNOWFLAKE.BILLING.PARTNER_REMAINING_BALANCE_DAILY)
ORDER BY SOLD_TO_CUSTOMER_NAME;

-- Create a summary view for quick insights
CREATE OR REPLACE VIEW billing_summary AS
SELECT 
    CURRENT_DATE() as REPORT_DATE,
    COUNT(DISTINCT u.SOLD_TO_CUSTOMER_NAME) as TOTAL_CUSTOMERS,
    COUNT(DISTINCT u.ACCOUNT_NAME) as TOTAL_ACCOUNTS,
    SUM(u.USAGE) as TOTAL_CREDITS_USED_MTD,
    SUM(u.USAGE_IN_CURRENCY) as TOTAL_COST_MTD,
    AVG(u.USAGE_IN_CURRENCY) as AVG_DAILY_COST,
    SUM(b.TOTAL_AVAILABLE_BALANCE) as TOTAL_AVAILABLE_BALANCE
FROM (
    SELECT * FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY 
    WHERE USAGE_DATE >= DATE_TRUNC('MONTH', CURRENT_DATE())
) u
LEFT JOIN latest_balances b ON u.SOLD_TO_CUSTOMER_NAME = b.SOLD_TO_CUSTOMER_NAME;

-- Grant access to views
GRANT SELECT ON VIEW current_month_usage TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON VIEW current_month_usage TO ROLE BILLING_DASHBOARD_VIEWER;
GRANT SELECT ON VIEW latest_balances TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON VIEW latest_balances TO ROLE BILLING_DASHBOARD_VIEWER;
GRANT SELECT ON VIEW billing_summary TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON VIEW billing_summary TO ROLE BILLING_DASHBOARD_VIEWER;

-- =============================================================================
-- STEP 9: VERIFICATION AND TESTING
-- =============================================================================

-- Verify Streamlit app was created
SHOW STREAMLIT APPS;

-- Test access to all BILLING views
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

-- Test helper views
SELECT * FROM current_month_usage LIMIT 5;
SELECT * FROM latest_balances LIMIT 5;
SELECT * FROM billing_summary;

-- Verify stage contents
LIST @billing_dashboard_stage;

-- =============================================================================
-- STEP 10: MAINTENANCE AND MANAGEMENT COMMANDS
-- =============================================================================

/*
USEFUL MAINTENANCE COMMANDS:

-- Update the application (after uploading new files)
ALTER STREAMLIT billing_dashboard SET ROOT_LOCATION = '@billing_dashboard_stage';

-- Check app details
DESC STREAMLIT billing_dashboard;

-- Monitor warehouse usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH' 
ORDER BY START_TIME DESC LIMIT 10;

-- Check user access
SHOW GRANTS TO ROLE BILLING_DASHBOARD_USER;
SHOW GRANTS TO ROLE BILLING_DASHBOARD_VIEWER;

-- Refresh views if needed
CREATE OR REPLACE VIEW current_month_usage AS ...;

-- Drop the application (if needed)
-- DROP STREAMLIT billing_dashboard;
-- DROP WAREHOUSE BILLING_DASHBOARD_WH;
-- DROP STAGE billing_dashboard_stage;
-- DROP SCHEMA BILLING_APPS.STREAMLIT_APPS;
-- DROP DATABASE BILLING_APPS;
*/

-- =============================================================================
-- DEPLOYMENT COMPLETE!
-- =============================================================================

SELECT 
    '✅ Billing Dashboard deployment completed successfully!' AS STATUS,
    'Next steps:' AS ACTION_REQUIRED,
    '1. Upload files to @billing_dashboard_stage' AS STEP_1,
    '2. Grant roles to users' AS STEP_2,
    '3. Access app at: Projects > Streamlit > billing_dashboard' AS STEP_3;

-- =============================================================================
-- POST-DEPLOYMENT NOTES
-- =============================================================================
/*
🎉 DEPLOYMENT SUMMARY:

CREATED INFRASTRUCTURE:
✅ Database: BILLING_APPS
✅ Schema: BILLING_APPS.STREAMLIT_APPS  
✅ Stage: billing_dashboard_stage
✅ Warehouse: BILLING_DASHBOARD_WH (XSMALL, auto-suspend 60s)
✅ Streamlit App: billing_dashboard

CREATED SECURITY:
✅ Role: BILLING_DASHBOARD_USER (full access)
✅ Role: BILLING_DASHBOARD_VIEWER (read-only)
✅ Proper permissions for BILLING schema access

CREATED HELPER VIEWS:
✅ current_month_usage - Current month usage data
✅ latest_balances - Most recent balance information  
✅ billing_summary - High-level summary metrics

NEXT STEPS:
1. Upload application files to the stage
2. Grant appropriate roles to users
3. Access the dashboard via Snowflake UI
4. Monitor usage and adjust warehouse size if needed

SUPPORT:
- For BILLING schema issues: Contact Snowflake Support
- For app issues: Check Streamlit logs in Snowflake UI
- For permissions: Work with your ACCOUNTADMIN

🚀 Your comprehensive billing dashboard is ready to use!
*/