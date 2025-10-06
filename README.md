# Snowflake Credit Usage Dashboard for Resellers

A comprehensive **Streamlit in Snowflake** application that enables Snowflake reseller customers to view their credit consumption, billing usage, and account balances using Snowflake's BILLING schema.

## 🌟 Features

### 📊 Key Metrics Dashboard
- **Total Credits Used**: Aggregate credit consumption across all accounts
- **Total Cost**: Monetary value of usage in contract currency
- **Active Customers**: Number of customers with usage in the selected period
- **Average Daily Credits**: Daily credit consumption trends

### 📈 Interactive Visualizations
- **Usage Trend Chart**: Daily credit usage by usage type (compute, storage, data transfer, etc.)
- **Usage Breakdown**: Pie chart showing distribution of credits by usage type
- **Balance Overview**: Waterfall chart showing current balances by customer
- **Usage Heatmap**: Weekly usage patterns visualization

### 🔍 Data Views
- **Usage Details**: Comprehensive view of daily usage by account and service
- **Balance Details**: Current balance information including free usage, capacity, and rollover
- **Smart Alerts**: Automated alerts for high usage, low balances, and growth trends

### 📥 Export Capabilities
- Download usage data as CSV
- Download balance data as CSV  
- Formatted reports with proper currency and credit formatting

### 🎛️ Advanced Filtering
- Date range selection with quick presets
- Customer-specific filtering
- Usage type filtering
- Real-time data refresh capabilities

## 🛠️ Technical Implementation

### Data Sources
The application leverages Snowflake's BILLING schema views:

1. **PARTNER_USAGE_IN_CURRENCY_DAILY**: Daily credit and currency usage
2. **PARTNER_REMAINING_BALANCE_DAILY**: Daily balance information
3. **PARTNER_CONTRACT_ITEMS**: Contract terms and capacity information
4. **PARTNER_RATE_SHEET_DAILY**: Effective rates for usage calculation

### Key Features
- **Native Streamlit in Snowflake**: No external hosting required
- **Embedded Configuration**: All settings built into the Python code
- **Smart Caching**: 1-hour data caching for optimal performance
- **Responsive Design**: Modern UI with enhanced styling
- **Error Handling**: Comprehensive error handling and user feedback

## 🚀 Simple Deployment

### Prerequisites
- Snowflake account with **Streamlit in Snowflake** enabled
- Access to **BILLING** schema (available for resellers and distributors)
- **ACCOUNTADMIN** role or appropriate permissions

### Choose Your Deployment Method

**Option A: Minimal Setup** (`MINIMAL_DEPLOY.sql`)
- ✅ Use if your users **already have** BILLING schema access
- Only creates: warehouse + Streamlit app
- Fastest deployment

**Option B: Complete Setup** (`deploy.sql`)
- ✅ Use if you need to **create permissions** for users
- Creates: warehouse + role + permissions + Streamlit app
- Recommended for new setups

### Quick Setup (3 Steps!)

#### 1. **Copy the Python Code**
- Copy the entire contents of `streamlit_app.py`

#### 2. **Run the Deployment Script**
- Open `MINIMAL_DEPLOY.sql` OR `deploy.sql` in Snowflake
- Paste the Python code into the `CREATE STREAMLIT` statement
- Execute the script

#### 3. **Grant Access & Launch**
```sql
-- For MINIMAL setup: Grant to existing role
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE YOUR_EXISTING_ROLE;

-- For COMPLETE setup: Grant new role to users
GRANT ROLE BILLING_DASHBOARD_USER TO USER your_username;

-- Access your app at: Projects > Streamlit > billing_dashboard
```

### Example Deployment
```sql
-- Simple deployment - just embed the Python code!
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS
$$
# Paste the entire streamlit_app.py content here
import streamlit as st
import pandas as pd
# ... rest of your Python code
$$;
```

## 📁 Project Structure
```
reseller-billing/
├── streamlit_app.py          # Complete application (copy this into Snowflake)
├── MINIMAL_DEPLOY.sql       # Minimal deployment (users already have BILLING access)
├── deploy.sql               # Complete deployment (creates role + permissions)
├── README.md                # This documentation
├── DEPLOYMENT_GUIDE.md      # Detailed deployment instructions
└── QUICK_DEPLOY.md         # Quick start guide
```

## 🔐 Security & Permissions

**Important:** The Streamlit app runs **as the viewing user**, not as a service account.

Users need:
- ✅ SELECT access to `SNOWFLAKE.BILLING` views
- ✅ USAGE on the warehouse
- ✅ USAGE on the Streamlit app

The **complete deployment** (`deploy.sql`) creates:
- **BILLING_DASHBOARD_USER** role with appropriate BILLING schema access
- **Warehouse**: `BILLING_DASHBOARD_WH` (XSMALL, auto-suspend)
- **Proper grants** for secure access to billing data

The **minimal deployment** (`MINIMAL_DEPLOY.sql`) assumes users already have BILLING access.

## 📊 Dashboard Capabilities

### Real-time Monitoring
- **Credit Consumption**: Track usage across all customer accounts
- **Cost Analysis**: Monitor spending in contract currencies
- **Balance Tracking**: View available credits and on-demand usage
- **Growth Trends**: Automated calculation of usage growth rates

### Advanced Analytics
- **Usage Heatmaps**: Identify usage patterns by day/week
- **Customer Rankings**: Top customers by credit consumption
- **Alert System**: Automated warnings for high usage or low balances
- **Trend Analysis**: Historical usage and cost trends

### Export & Reporting
- **CSV Downloads**: Export filtered data for external analysis
- **Formatted Reports**: Properly formatted currency and credit values
- **Date Range Flexibility**: Custom date ranges up to 1 year

## 🆘 Troubleshooting

### Common Issues

**"Table doesn't exist" error**
- Verify BILLING schema access: Contact Snowflake Support if needed

**"Permission denied" error**  
- Ensure you have ACCOUNTADMIN role or appropriate grants

**Dashboard shows "No data"**
- Verify date range selection
- Check if you have recent billing data
- Confirm customer filter settings

### Quick Verification
```sql
-- Test BILLING schema access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;

-- Check Streamlit app status
SHOW STREAMLIT APPS;
DESC STREAMLIT billing_dashboard;
```

## 📞 Support

- **BILLING Schema Issues**: Contact Snowflake Support
- **App Issues**: Check error logs in Streamlit interface  
- **Permissions**: Work with your Snowflake ACCOUNTADMIN

## 🔄 Updates & Maintenance

### Updating the Application
```sql
-- Simply update the Streamlit code
ALTER STREAMLIT billing_dashboard SET MAIN_FILE = 'new_python_code_here';
```

### Monitoring Usage
```sql
-- Monitor warehouse costs
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH';
```

---

**🎯 Ready to monitor your reseller billing usage with a native Snowflake solution!**

*Compatible with Snowflake reseller/distributor accounts with BILLING schema access*