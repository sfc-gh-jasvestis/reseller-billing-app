-- Snowflake Deployment Script for Reseller Billing Dashboard
-- Run this script in your Snowflake account to deploy the Streamlit app

-- =============================================================================
-- SETUP INSTRUCTIONS
-- =============================================================================
-- 1. Upload all application files to a Snowflake stage
-- 2. Run this script as ACCOUNTADMIN or a role with appropriate privileges
-- 3. Grant necessary permissions to users who will access the dashboard
-- =============================================================================

-- Create database and schema for the application (optional)
CREATE DATABASE IF NOT EXISTS BILLING_APPS;
CREATE SCHEMA IF NOT EXISTS BILLING_APPS.STREAMLIT_APPS;

-- Use the created schema
USE SCHEMA BILLING_APPS.STREAMLIT_APPS;

-- Create a stage to store the application files
CREATE OR REPLACE STAGE billing_dashboard_stage
    DIRECTORY = ( ENABLE = TRUE )
    COMMENT = 'Stage for Snowflake Reseller Billing Dashboard files';

-- Create warehouse for the application (if needed)
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for Billing Dashboard Streamlit app';

-- Grant necessary permissions for BILLING_USAGE schema access
-- Note: These grants need to be executed by ACCOUNTADMIN
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE PUBLIC;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE PUBLIC;

-- Upload files to stage (example commands - adjust paths as needed)
-- PUT file:///path/to/streamlit_app.py @billing_dashboard_stage;
-- PUT file:///path/to/requirements.txt @billing_dashboard_stage;
-- PUT file:///path/to/config/app_config.py @billing_dashboard_stage/config/;
-- PUT file:///path/to/utils/data_utils.py @billing_dashboard_stage/utils/;

-- Create the Streamlit application
CREATE OR REPLACE STREAMLIT billing_dashboard
    ROOT_LOCATION = '@billing_dashboard_stage'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
    COMMENT = 'Snowflake Credit Usage Dashboard for Reseller Customers';

-- Grant usage on the Streamlit app
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE PUBLIC;

-- =============================================================================
-- SECURITY SETUP (Optional - for more granular access control)
-- =============================================================================

-- Create role specifically for billing dashboard users
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER;

-- Grant necessary permissions to the role
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE BILLING_DASHBOARD_USER;

-- Grant warehouse and database access
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON DATABASE BILLING_APPS TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA BILLING_APPS.STREAMLIT_APPS TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON STREAMLIT BILLING_APPS.STREAMLIT_APPS.billing_dashboard TO ROLE BILLING_DASHBOARD_USER;

-- Grant role to users (replace 'username' with actual usernames)
-- GRANT ROLE BILLING_DASHBOARD_USER TO USER username;

-- =============================================================================
-- MAINTENANCE COMMANDS
-- =============================================================================

-- View Streamlit app details
-- SHOW STREAMLIT APPS;
-- DESC STREAMLIT billing_dashboard;

-- Update the application (after uploading new files)
-- ALTER STREAMLIT billing_dashboard SET ROOT_LOCATION = '@billing_dashboard_stage';

-- Drop the application (if needed)
-- DROP STREAMLIT billing_dashboard;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Test access to BILLING_USAGE views
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY;
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.REMAINING_BALANCE_DAILY;
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.CONTRACT_ITEMS;

-- =============================================================================
-- POST-DEPLOYMENT NOTES
-- =============================================================================
-- 1. The application will be available at the Snowflake Streamlit URL
-- 2. Users need appropriate permissions to access BILLING_USAGE schema
-- 3. Ensure the warehouse has sufficient size based on expected usage
-- 4. Monitor usage and adjust warehouse auto-suspend settings as needed
-- 5. Regularly update the application files as needed
-- =============================================================================

-- Display success message
SELECT 'Billing Dashboard deployment script completed successfully!' AS status; 