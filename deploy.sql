-- =============================================================================
-- DEPLOYMENT - Snowflake Reseller Billing Dashboard (Streamlit in Snowflake)
-- =============================================================================
-- PREREQUISITES
-- 1. Run in the reseller/distributor organization account (or an account with
--    the ORGADMIN role enabled). The SNOWFLAKE.BILLING PARTNER_* views do not
--    exist in other accounts; there the app automatically shows demo data.
-- 2. ACCOUNTADMIN. Only ACCOUNTADMIN can read the BILLING views, and a
--    Streamlit app runs with its OWNER's rights, so ACCOUNTADMIN must own it.
--    Viewers only need USAGE on the app; no BILLING grants to viewers are
--    needed (and none would work).
-- 3. Snowflake CLI (`snow`) or SnowSQL to upload the app files with PUT.
-- =============================================================================

USE ROLE ACCOUNTADMIN;

-- STEP 1: Verify the BILLING views exist in this account (should return rows)
SHOW VIEWS LIKE 'PARTNER_%' IN SCHEMA SNOWFLAKE.BILLING;

-- STEP 2: Infrastructure
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for Billing Dashboard Streamlit app';

CREATE DATABASE IF NOT EXISTS BILLING_DASHBOARD;
CREATE SCHEMA IF NOT EXISTS BILLING_DASHBOARD.APP;
CREATE STAGE IF NOT EXISTS BILLING_DASHBOARD.APP.APP_STAGE;

-- STEP 3: Upload app files (run from the repository root with snow/SnowSQL)
-- PUT file://streamlit_app.py @BILLING_DASHBOARD.APP.APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- PUT file://environment.yml  @BILLING_DASHBOARD.APP.APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- STEP 4: Create the app (owned by ACCOUNTADMIN)
CREATE OR REPLACE STREAMLIT BILLING_DASHBOARD.APP.BILLING_DASHBOARD
    FROM @BILLING_DASHBOARD.APP.APP_STAGE
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = BILLING_DASHBOARD_WH
    TITLE = 'Reseller Billing Dashboard'
    COMMENT = 'Snowflake Credit Usage Dashboard for Reseller Customers';

-- STEP 5: Viewer access
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER
    COMMENT = 'Role for users viewing the billing dashboard';
GRANT USAGE ON DATABASE BILLING_DASHBOARD TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA BILLING_DASHBOARD.APP TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON STREAMLIT BILLING_DASHBOARD.APP.BILLING_DASHBOARD TO ROLE BILLING_DASHBOARD_USER;
-- GRANT ROLE BILLING_DASHBOARD_USER TO USER <username>;

-- STEP 6: Verify
SHOW STREAMLITS LIKE 'BILLING_DASHBOARD' IN SCHEMA BILLING_DASHBOARD.APP;

/*
UPDATE THE APP CODE: re-run the STEP 3 PUT commands; the app picks up the new
files on next load.

REMOVE:
DROP STREAMLIT BILLING_DASHBOARD.APP.BILLING_DASHBOARD;
DROP DATABASE BILLING_DASHBOARD;
DROP WAREHOUSE BILLING_DASHBOARD_WH;
DROP ROLE BILLING_DASHBOARD_USER;
*/
