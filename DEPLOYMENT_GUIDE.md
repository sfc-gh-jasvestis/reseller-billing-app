# Deployment Guide: Snowflake Reseller Billing Dashboard

Complete deployment instructions for the **Streamlit in Snowflake** Credit Usage Dashboard.

## 📋 Prerequisites

### Required Access
- **Snowflake Account** with ACCOUNTADMIN role
- **Streamlit in Snowflake** feature enabled  
- **BILLING Schema** access (available for resellers/distributors)
- **Active Warehouse** for running queries

### Verify Prerequisites
```sql
-- Test BILLING schema access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;

-- Check Streamlit support  
SHOW STREAMLIT APPS;
```

## 🚀 Deployment Process

### Method 1: Quick Deploy (Recommended)

**Step 1: Prepare the Code**
1. Open `streamlit_app.py` in your editor
2. Select all code (Ctrl+A / Cmd+A)
3. Copy to clipboard (Ctrl+C / Cmd+C)

**Step 2: Deploy in Snowflake**
1. Open Snowflake Web UI
2. Create new worksheet
3. Copy the contents of `deploy.sql`
4. **IMPORTANT**: Replace the placeholder in the `CREATE STREAMLIT` statement:
   ```sql
   CREATE OR REPLACE STREAMLIT billing_dashboard
       QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
   AS
   $$
   -- PASTE YOUR PYTHON CODE HERE (replace this comment)
   $$;
   ```
5. Paste your Python code between the `$$` markers
6. Execute the entire script

**Step 3: Grant Access**
```sql
-- Grant to specific users
GRANT ROLE BILLING_DASHBOARD_USER TO USER username1;
GRANT ROLE BILLING_DASHBOARD_USER TO USER username2;

-- OR grant to PUBLIC for broad access (development)
GRANT ROLE BILLING_DASHBOARD_USER TO ROLE PUBLIC;
```

### Method 2: Manual Setup

If you prefer step-by-step manual setup:

**1. Create Infrastructure**
```sql
-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- Create role
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER;

-- Grant permissions
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_USER;
```

**2. Create Streamlit App**
```sql
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS
$$
-- Paste your entire streamlit_app.py content here
$$;

-- Grant access
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;
```

## ✅ Verification & Testing

### Verify Deployment
```sql
-- Check Streamlit app
SHOW STREAMLIT APPS;
DESC STREAMLIT billing_dashboard;

-- Test data access
SELECT 'PARTNER_USAGE_IN_CURRENCY_DAILY' as view_name, COUNT(*) as row_count 
FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY
UNION ALL
SELECT 'PARTNER_REMAINING_BALANCE_DAILY' as view_name, COUNT(*) as row_count 
FROM SNOWFLAKE.BILLING.PARTNER_REMAINING_BALANCE_DAILY;
```

### Access Your Dashboard
1. Go to **Snowflake Web UI**
2. Navigate to **Projects** → **Streamlit**  
3. Click on **billing_dashboard**
4. Start monitoring! 🎉

## 🔧 Configuration Options

### Warehouse Sizing
```sql
-- For heavy usage, consider larger warehouse
ALTER WAREHOUSE BILLING_DASHBOARD_WH SET WAREHOUSE_SIZE = 'SMALL';

-- For cost optimization
ALTER WAREHOUSE BILLING_DASHBOARD_WH SET AUTO_SUSPEND = 30;
```

### Security Options
```sql
-- Create read-only role
CREATE ROLE BILLING_DASHBOARD_VIEWER;
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_VIEWER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_VIEWER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_VIEWER;
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_VIEWER;
```

## 🆘 Troubleshooting

### Common Issues

**❌ "Table doesn't exist" Error**
```sql
-- Verify BILLING schema access
SELECT CURRENT_ROLE();
SHOW GRANTS TO ROLE CURRENT_ROLE();
```
*Solution*: Contact Snowflake Support for BILLING schema access

**❌ "Permission denied" Error**  
*Solution*: Ensure you have ACCOUNTADMIN role or ask admin to run deployment

**❌ "Streamlit app not found" Error**
```sql
-- Check if app exists
SHOW STREAMLIT APPS;
-- Recreate if needed
CREATE OR REPLACE STREAMLIT billing_dashboard...
```

**❌ Dashboard Shows "No Data"**
- Check date range selection (try "Last 30 days")
- Verify customer filter settings
- Confirm you have recent billing data:
  ```sql
  SELECT MAX(USAGE_DATE) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;
  ```

### Performance Issues

**Slow Loading**
- Increase warehouse size temporarily
- Check data volume for selected date range
- Consider shorter date ranges for better performance

**High Costs**
- Monitor warehouse usage:
  ```sql
  SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
  WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH' 
  ORDER BY START_TIME DESC LIMIT 10;
  ```
- Adjust auto-suspend settings

## 🔄 Updates & Maintenance

### Updating the Application
```sql
-- Update Streamlit code
ALTER STREAMLIT billing_dashboard SET MAIN_FILE = 'updated_python_code_here';
```

### Monitoring Usage
```sql
-- Check app usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.STREAMLIT_EVENTS 
WHERE STREAMLIT_NAME = 'BILLING_DASHBOARD';

-- Monitor costs
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH';
```

### Backup & Recovery
```sql
-- Backup current app definition
DESC STREAMLIT billing_dashboard;

-- Export role grants
SHOW GRANTS TO ROLE BILLING_DASHBOARD_USER;
```

## 📞 Support Resources

### Snowflake Support
- **BILLING Schema Issues**: Contact Snowflake Support
- **Streamlit Issues**: Check Snowflake documentation
- **Performance**: Snowflake Support or Solutions Architecture

### Application Support  
- **Dashboard Errors**: Check Streamlit logs in Snowflake UI
- **Data Issues**: Verify BILLING schema access and data availability
- **Permissions**: Work with your Snowflake ACCOUNTADMIN

## 📋 Deployment Checklist

- [ ] ✅ Verified BILLING schema access
- [ ] ✅ Copied Python code from streamlit_app.py
- [ ] ✅ Executed deploy.sql with embedded Python code
- [ ] ✅ Granted BILLING_DASHBOARD_USER role to users
- [ ] ✅ Verified Streamlit app creation
- [ ] ✅ Tested dashboard access and functionality
- [ ] ✅ Confirmed data loads correctly
- [ ] ✅ Set up monitoring (optional)

## 🎉 Success!

Your Snowflake Reseller Billing Dashboard is now deployed and ready to use!

**Access URL**: Snowflake UI → Projects → Streamlit → billing_dashboard

---

*For quick deployment, see `QUICK_DEPLOY.md`*  
*For basic information, see `README.md`*