# Deployment Guide: Snowflake Credit Usage Dashboard

This guide provides step-by-step instructions to deploy the Snowflake Credit Usage Dashboard for reseller customers.

## 📋 Prerequisites

### 1. Snowflake Account Requirements
- Snowflake account with **ACCOUNTADMIN** role access
- Access to **BILLING_USAGE** schema (Private Preview feature)
- Streamlit in Snowflake enabled
- Active warehouse for running queries

### 2. Feature Access
- **BILLING_USAGE** schema access (contact Snowflake support if not available)
- Streamlit in Snowflake feature enabled
- Appropriate user permissions

## 🚀 Step-by-Step Deployment

### Step 1: Verify Prerequisites

First, verify you have access to the required features:

```sql
-- Test BILLING_USAGE schema access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY;

-- Check Streamlit support
SHOW STREAMLIT APPS;
```

### Step 2: Create Application Structure

1. **Create a local directory** for your application files:
```bash
mkdir snowflake-billing-dashboard
cd snowflake-billing-dashboard
```

2. **Download all application files** to this directory:
   - `streamlit_app.py` (main application)
   - `requirements.txt`
   - `config/app_config.py`
   - `config/__init__.py`
   - `utils/data_utils.py`
   - `utils/__init__.py`

### Step 3: Set Up Snowflake Environment

1. **Connect to Snowflake** using SnowSQL, Snowflake Web UI, or your preferred client.

2. **Run the deployment script**:
```sql
-- Execute the contents of deploy.sql
-- This creates database, schema, warehouse, and necessary permissions
```

3. **Create the stage and upload files**:
```sql
-- Create stage
CREATE OR REPLACE STAGE billing_dashboard_stage
    DIRECTORY = ( ENABLE = TRUE )
    COMMENT = 'Stage for Snowflake Reseller Billing Dashboard files';
```

### Step 4: Upload Application Files

**Option A: Using SnowSQL**
```bash
# Upload main files
snowsql -c myconnection -q "PUT file://streamlit_app.py @billing_dashboard_stage"
snowsql -c myconnection -q "PUT file://requirements.txt @billing_dashboard_stage"

# Upload config files
snowsql -c myconnection -q "PUT file://config/app_config.py @billing_dashboard_stage/config/"
snowsql -c myconnection -q "PUT file://config/__init__.py @billing_dashboard_stage/config/"

# Upload utils files
snowsql -c myconnection -q "PUT file://utils/data_utils.py @billing_dashboard_stage/utils/"
snowsql -c myconnection -q "PUT file://utils/__init__.py @billing_dashboard_stage/utils/"
```

**Option B: Using Snowflake Web UI**
1. Navigate to Databases → BILLING_APPS → STREAMLIT_APPS → Stages
2. Click on `billing_dashboard_stage`
3. Upload files using the web interface

### Step 5: Create Streamlit Application

Create the Streamlit application with the following SQL command:

```sql
CREATE OR REPLACE STREAMLIT billing_dashboard
    ROOT_LOCATION = '@billing_dashboard_stage'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
    COMMENT = 'Snowflake Credit Usage Dashboard for Reseller Customers';
```

### Step 6: Configure Permissions

**Grant basic access:**
```sql
-- Grant to PUBLIC role (broad access)
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE PUBLIC;

-- Grant access to BILLING_USAGE schema
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE PUBLIC;
```

**Create specific role (recommended):**
```sql
-- Create role for dashboard users
CREATE ROLE IF NOT EXISTS BILLING_DASHBOARD_USER;

-- Grant necessary permissions
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;

-- Grant role to specific users
GRANT ROLE BILLING_DASHBOARD_USER TO USER your_username;
```

### Step 7: Test the Application

1. **Navigate to your Streamlit app**:
   - Go to Snowflake Web UI
   - Navigate to Projects → Streamlit
   - Click on your application

2. **Verify functionality**:
   - Check data loads correctly
   - Test different date ranges
   - Verify visualizations appear
   - Test export functionality

## 🔧 Configuration Options

### Customizing the Application

Edit `config/app_config.py` to customize:

```python
# Modify default settings
DEFAULT_DATE_RANGE_DAYS = 30  # Change default date range
CACHE_TTL_SECONDS = 3600      # Adjust cache duration

# Enable/disable features
FEATURES = {
    "export_enabled": True,
    "advanced_filters": True,
    "real_time_refresh": False,
    "email_reports": False
}
```

### Warehouse Sizing

Adjust warehouse size based on usage:

```sql
-- For light usage (few users, small datasets)
ALTER WAREHOUSE BILLING_DASHBOARD_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- For moderate usage (multiple users, larger datasets)
ALTER WAREHOUSE BILLING_DASHBOARD_WH SET WAREHOUSE_SIZE = 'SMALL';

-- For heavy usage (many concurrent users)
ALTER WAREHOUSE BILLING_DASHBOARD_WH SET WAREHOUSE_SIZE = 'MEDIUM';
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. "Access Denied" Errors
**Problem**: Users cannot access BILLING_USAGE views
**Solution**:
```sql
-- Verify permissions
SHOW GRANTS TO ROLE your_role;

-- Re-grant if necessary
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING_USAGE TO ROLE your_role;
```

#### 2. "No Data Found" Messages
**Problem**: Dashboard shows no usage data
**Solutions**:
- Verify you have recent billing data
- Check date range selection
- Confirm customer filter settings
- Ensure data exists in BILLING_USAGE views

#### 3. Slow Performance
**Problem**: Dashboard loads slowly
**Solutions**:
- Increase warehouse size
- Adjust cache TTL settings
- Limit date ranges for large datasets
- Monitor query performance

#### 4. Import Errors
**Problem**: Python import errors in Streamlit
**Solutions**:
- Verify all files uploaded correctly
- Check file paths in stage
- Ensure `__init__.py` files exist
- Validate Python syntax

### Validation Queries

```sql
-- Check data availability
SELECT 
    MIN(USAGE_DATE) as earliest_date,
    MAX(USAGE_DATE) as latest_date,
    COUNT(*) as total_records
FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY;

-- Verify customer data
SELECT DISTINCT SOLD_TO_CUSTOMER_NAME 
FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY 
WHERE USAGE_DATE >= CURRENT_DATE - 30;

-- Check balance data
SELECT COUNT(*) 
FROM SNOWFLAKE.BILLING_USAGE.REMAINING_BALANCE_DAILY
WHERE DATE >= CURRENT_DATE - 30;
```

## 📊 Usage Guidelines

### Best Practices

1. **Date Range Selection**:
   - Start with shorter ranges (7-30 days) for testing
   - Longer ranges may impact performance
   - Consider data latency (24-72 hours)

2. **User Management**:
   - Create specific roles for different user groups
   - Grant minimal required permissions
   - Regular review of user access

3. **Performance Optimization**:
   - Monitor warehouse usage
   - Adjust auto-suspend settings
   - Use appropriate warehouse sizes

4. **Data Refresh**:
   - Data updates every 24-72 hours
   - Cache refreshes every hour
   - Manual refresh by reloading page

## 🛠️ Maintenance

### Regular Maintenance Tasks

1. **Update Application**:
```sql
-- Upload new files to stage
-- Then update the app
ALTER STREAMLIT billing_dashboard SET ROOT_LOCATION = '@billing_dashboard_stage';
```

2. **Monitor Usage**:
```sql
-- Check warehouse usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH'
AND START_TIME >= CURRENT_DATE - 7;
```

3. **Clean Up**:
```sql
-- Remove old files from stage if needed
REMOVE @billing_dashboard_stage pattern='old_file.py';
```

### Backup and Recovery

1. **Export Configuration**:
   - Save all SQL scripts
   - Backup application files
   - Document custom configurations

2. **Application Backup**:
```sql
-- Create backup of Streamlit app
CREATE OR REPLACE STREAMLIT billing_dashboard_backup
    CLONE billing_dashboard;
```

## 📞 Support

### Getting Help

1. **Snowflake Documentation**:
   - [BILLING_USAGE Documentation](https://docs.snowflake.com/en/LIMITEDACCESS/billing-usage-resellers)
   - [Streamlit in Snowflake Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

2. **Common Resources**:
   - Snowflake Community
   - Support tickets for feature access
   - Internal IT/Admin team

3. **Contact Information**:
   - For BILLING_USAGE access: Contact Snowflake Support
   - For application issues: Check error logs in Streamlit
   - For permissions: Work with Snowflake ACCOUNTADMIN

---

## 🎉 Completion Checklist

- [ ] Verified BILLING_USAGE schema access
- [ ] Created database and schema structure
- [ ] Uploaded all application files
- [ ] Created Streamlit application
- [ ] Configured user permissions
- [ ] Tested application functionality
- [ ] Documented custom configurations
- [ ] Trained end users

**Congratulations!** Your Snowflake Credit Usage Dashboard is now ready for use by reseller customers to monitor their credit consumption.

---

*For questions or issues, refer to the troubleshooting section or contact your Snowflake administrator.* 