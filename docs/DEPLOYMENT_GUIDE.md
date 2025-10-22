# Deployment Guide: Snowflake Reseller Billing Dashboard

Complete deployment instructions for the **Streamlit in Snowflake** Credit Usage Dashboard.

## 📋 Prerequisites

### Required Access
- **Snowflake Account** with ACCOUNTADMIN role (or CREATE STREAMLIT privilege)
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

### Choose Your Deployment Method

**Option A: Minimal Setup** - Use if your users already have BILLING schema access  
**Option B: Complete Setup** - Creates dedicated role and grants all permissions

---

### Option A: Minimal Setup (Users Already Have Permissions)

**What This Does:**
- ✅ Creates warehouse for the app
- ✅ Creates the Streamlit app
- ✅ Grants Streamlit access to existing role
- ❌ Does NOT create new role or BILLING permissions

**When to Use:** Your users already have access to `SNOWFLAKE.BILLING` views through an existing role.

**Step 1: Prepare the Code**
1. Open `streamlit_app.py` in your editor
2. Select all code (Ctrl+A / Cmd+A)
3. Copy to clipboard (Ctrl+C / Cmd+C)

**Step 2: Deploy**
```sql
-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- Create Streamlit app (paste Python code between $$)
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS
$$
-- PASTE streamlit_app.py CONTENTS HERE (replace this comment)
$$;

-- Grant access to your existing role
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE YOUR_EXISTING_ROLE;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE YOUR_EXISTING_ROLE;
```

**Step 3: Done!**
Navigate to **Projects** → **Streamlit** → **billing_dashboard** 🎉

---

### Option B: Complete Setup (Create Role & Permissions)

**What This Does:**
- ✅ Creates warehouse for the app
- ✅ Creates dedicated `BILLING_DASHBOARD_USER` role
- ✅ Grants all BILLING schema permissions to the role
- ✅ Creates the Streamlit app
- ✅ Grants Streamlit access to the role

**When to Use:** You want a clean, dedicated role specifically for this dashboard.

**Step 1: Prepare the Code**
1. Open `streamlit_app.py` in your editor
2. Select all code (Ctrl+A / Cmd+A)
3. Copy to clipboard (Ctrl+C / Cmd+C)

**Step 2: Deploy with Full Setup**
```sql
-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- Create dedicated role
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER;

-- Grant BILLING schema permissions to the role
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_USER;

-- Create Streamlit app (paste Python code between $$)
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS
$$
-- PASTE streamlit_app.py CONTENTS HERE (replace this comment)
$$;

-- Grant Streamlit access to the role
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;
```

**Step 3: Assign Role to Users**
```sql
-- Grant to specific users
GRANT ROLE BILLING_DASHBOARD_USER TO USER username1;
GRANT ROLE BILLING_DASHBOARD_USER TO USER username2;

-- OR grant to PUBLIC for broad access (development only)
GRANT ROLE BILLING_DASHBOARD_USER TO ROLE PUBLIC;
```

**Step 4: Done!**
Navigate to **Projects** → **Streamlit** → **billing_dashboard** 🎉

---

## 🔑 Understanding Permissions

**Important:** The Streamlit app runs **as the viewing user**, not as a service account. This means:

- ✅ Each user needs access to `SNOWFLAKE.BILLING` views
- ✅ Each user needs access to the warehouse
- ✅ Each user needs USAGE permission on the Streamlit app itself

**What each option does:**
- **Option A**: Assumes users already have BILLING access via existing role
- **Option B**: Creates new role and grants everything needed

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