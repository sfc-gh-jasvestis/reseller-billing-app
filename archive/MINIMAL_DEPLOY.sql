-- =============================================================================
-- MINIMAL DEPLOYMENT - Snowflake Reseller Billing Dashboard
-- =============================================================================
-- Use this script if your users ALREADY have access to SNOWFLAKE.BILLING
-- This creates ONLY the warehouse and Streamlit app, no roles or permissions
--
-- PREREQUISITES:
-- 1. Users already have SELECT access to SNOWFLAKE.BILLING views
-- 2. ACCOUNTADMIN role or CREATE STREAMLIT privilege
-- 3. Streamlit in Snowflake feature enabled
-- =============================================================================

-- =============================================================================
-- STEP 1: CREATE WAREHOUSE
-- =============================================================================

CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for Billing Dashboard Streamlit app';

-- =============================================================================
-- STEP 2: CREATE STREAMLIT APP
-- =============================================================================
-- IMPORTANT: Copy the ENTIRE contents of streamlit_app.py and paste between $$

CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
    COMMENT = 'Snowflake Credit Usage Dashboard for Reseller Customers'
AS
$$
-- ===== PASTE streamlit_app.py CONTENTS HERE =====
-- Replace this entire comment block with the Python code from streamlit_app.py
-- Make sure to include all code from the first import to the final if __name__ == "__main__" block
$$;

-- =============================================================================
-- STEP 3: GRANT ACCESS TO YOUR EXISTING ROLE
-- =============================================================================
-- Replace YOUR_EXISTING_ROLE with the role that already has BILLING schema access

GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE YOUR_EXISTING_ROLE;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE YOUR_EXISTING_ROLE;

-- Alternative: Grant to multiple roles
-- GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE ROLE1;
-- GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE ROLE2;
-- GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE ROLE1;
-- GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE ROLE2;

-- =============================================================================
-- STEP 4: VERIFICATION
-- =============================================================================

-- Verify Streamlit app was created
SHOW STREAMLIT APPS;

-- Verify your role has the necessary access
USE ROLE YOUR_EXISTING_ROLE;  -- Switch to the role you granted access to

-- Test that you can query BILLING views
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY LIMIT 1;

-- Test Streamlit access
DESC STREAMLIT billing_dashboard;

-- =============================================================================
-- DEPLOYMENT COMPLETE!
-- =============================================================================

SELECT 
    '✅ Minimal deployment completed!' AS STATUS,
    'Navigate to: Projects > Streamlit > billing_dashboard' AS ACCESS_APP;

-- =============================================================================
-- NOTES
-- =============================================================================
-- 
-- Why minimal deployment?
-- - The Streamlit app runs AS the viewing user (not as a service account)
-- - Users only need: BILLING schema access + Streamlit USAGE + Warehouse USAGE
-- - If users already have BILLING access, you just need to grant Streamlit/Warehouse
-- 
-- What if users DON'T have BILLING access yet?
-- - Use deploy.sql instead (creates BILLING_DASHBOARD_USER role with all permissions)
-- 
-- =============================================================================
