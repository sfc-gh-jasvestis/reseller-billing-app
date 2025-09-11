-- Minimal Deployment Script for Streamlit Billing Dashboard
-- Use this when BILLING_USAGE schema is already enabled by Snowflake Support

-- =============================================================================
-- PREREQUISITES VERIFICATION
-- =============================================================================
-- Before running this script, verify BILLING_USAGE access:
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY;
-- If this query works, you're ready to proceed!
-- =============================================================================

-- Create a stage to store the application files
CREATE OR REPLACE STAGE billing_dashboard_stage
    DIRECTORY = ( ENABLE = TRUE )
    COMMENT = 'Stage for Snowflake Reseller Billing Dashboard files';

-- Create warehouse for the application (if you don't have one)
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for Billing Dashboard Streamlit app';

-- =============================================================================
-- FILE UPLOAD INSTRUCTIONS
-- =============================================================================
-- Upload your application files to the stage using one of these methods:
--
-- Method 1: SnowSQL (recommended)
-- PUT file://streamlit_app.py @billing_dashboard_stage;
-- PUT file://requirements.txt @billing_dashboard_stage;
-- PUT file://config/app_config.py @billing_dashboard_stage/config/;
-- PUT file://config/__init__.py @billing_dashboard_stage/config/;
-- PUT file://utils/data_utils.py @billing_dashboard_stage/utils/;
-- PUT file://utils/__init__.py @billing_dashboard_stage/utils/;
--
-- Method 2: Snowflake Web UI
-- 1. Go to Data > Databases > [Your Database] > [Your Schema] > Stages
-- 2. Click on billing_dashboard_stage
-- 3. Upload files using the web interface
-- =============================================================================

-- Create the Streamlit application
CREATE OR REPLACE STREAMLIT billing_dashboard
    ROOT_LOCATION = '@billing_dashboard_stage'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
    COMMENT = 'Snowflake Credit Usage Dashboard for Reseller Customers';

-- Grant usage on the Streamlit app to appropriate roles
-- Option 1: Grant to PUBLIC (broad access)
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE PUBLIC;

-- Option 2: Create specific role for dashboard users (recommended for production)
-- CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER;
-- GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;
-- GRANT ROLE BILLING_DASHBOARD_USER TO USER your_username;

-- =============================================================================
-- VERIFICATION STEPS
-- =============================================================================
-- 1. Verify Streamlit app was created:
-- SHOW STREAMLIT APPS;
-- 
-- 2. Test BILLING_USAGE access:
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY;
-- SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.REMAINING_BALANCE_DAILY;
-- 
-- 3. Access your app:
-- Go to Snowflake UI > Projects > Streamlit > billing_dashboard
-- =============================================================================

-- Display success message
SELECT 'Minimal Billing Dashboard deployment completed successfully!' AS status,
       'Access your app at: Projects > Streamlit > billing_dashboard' AS next_step;
