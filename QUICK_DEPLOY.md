# Quick Deployment Guide - BILLING_USAGE Already Enabled

Since Snowflake Support has already enabled the BILLING_USAGE feature for your account, you can use this streamlined deployment process.

## 🚀 **3-Step Quick Deployment**

### **Step 1: Upload Files to Snowflake**

**Option A: Using SnowSQL (Recommended)**
```bash
# Navigate to your project directory
cd /path/to/reseller-billing-app

# Upload files to Snowflake stage
snowsql -c your_connection -q "CREATE OR REPLACE STAGE billing_dashboard_stage DIRECTORY = (ENABLE = TRUE);"
snowsql -c your_connection -q "PUT file://streamlit_app.py @billing_dashboard_stage;"
snowsql -c your_connection -q "PUT file://requirements.txt @billing_dashboard_stage;"
snowsql -c your_connection -q "PUT file://config/app_config.py @billing_dashboard_stage/config/;"
snowsql -c your_connection -q "PUT file://config/__init__.py @billing_dashboard_stage/config/;"
snowsql -c your_connection -q "PUT file://utils/data_utils.py @billing_dashboard_stage/utils/;"
snowsql -c your_connection -q "PUT file://utils/__init__.py @billing_dashboard_stage/utils/;"
```

**Option B: Using Snowflake Web UI**
1. Go to **Data** → **Databases** → Create or select a database/schema
2. Go to **Stages** → **Create Stage** → Name it `billing_dashboard_stage`
3. Upload all files using the web interface

### **Step 2: Run Minimal Deployment Script**

Execute the `deploy_minimal.sql` script in Snowflake:

```sql
-- Copy and paste the contents of deploy_minimal.sql into Snowflake worksheet
-- Or run via SnowSQL:
-- snowsql -c your_connection -f deploy_minimal.sql
```

### **Step 3: Access Your Dashboard**

1. Go to **Snowflake Web UI**
2. Navigate to **Projects** → **Streamlit**
3. Click on **billing_dashboard**
4. Start monitoring your reseller billing usage! 🎉

## ✅ **Verification Checklist**

- [ ] BILLING_USAGE access confirmed: `SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY;`
- [ ] Files uploaded to stage successfully
- [ ] Streamlit app created: `SHOW STREAMLIT APPS;`
- [ ] Dashboard accessible via Snowflake UI
- [ ] Data loads correctly in the dashboard

## 🔧 **What Gets Created**

- **Stage**: `billing_dashboard_stage` (for app files)
- **Warehouse**: `BILLING_DASHBOARD_WH` (XSMALL, auto-suspend 60s)
- **Streamlit App**: `billing_dashboard` (your main application)

## 📊 **Expected Dashboard Features**

Once deployed, your dashboard will provide:

- **Real-time Credit Monitoring** - Track consumption across customers
- **Interactive Visualizations** - Trends, heatmaps, waterfall charts
- **Smart Alerts** - High usage warnings and balance notifications
- **Advanced Filtering** - Date ranges, customers, usage types
- **Data Export** - Download usage and balance data as CSV
- **Balance Tracking** - Monitor capacity, free usage, and on-demand charges

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"Table doesn't exist" error**
   - Verify BILLING_USAGE is enabled: Contact Snowflake Support if needed

2. **"Permission denied" error**
   - Ensure you have ACCOUNTADMIN role or appropriate grants

3. **"Files not found" error**
   - Check file upload to stage: `LIST @billing_dashboard_stage;`

4. **Dashboard shows "No data"**
   - Verify date range selection
   - Check if you have recent billing data

### **Quick Fixes:**

```sql
-- Check stage contents
LIST @billing_dashboard_stage;

-- Verify BILLING_USAGE access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY;

-- Check Streamlit app status
SHOW STREAMLIT APPS;
DESC STREAMLIT billing_dashboard;
```

## 📞 **Support**

- **BILLING_USAGE Issues**: Contact Snowflake Support
- **App Issues**: Check error logs in Streamlit interface
- **Permissions**: Work with your Snowflake ACCOUNTADMIN

---

**Total Deployment Time**: ~10-15 minutes ⚡

**Ready to monitor your reseller billing usage!** 🎯
