# ❄️ Snowflake Credit Usage Dashboard for Resellers

A comprehensive **Streamlit in Snowflake** application for monitoring credit consumption, billing usage, and account balances using Snowflake's BILLING schema.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

---

## 🌟 Key Features

### 📊 Interactive Dashboard
- **Real-time Metrics**: Total credits, costs, active customers, and daily averages
- **Advanced Analytics**: Usage trends, patterns, and forecasting
- **Smart Alerts**: Automated warnings for high usage, low balances, and growth anomalies
- **Contract Monitoring**: Track capacity usage, overage projections, and renewal recommendations

<img width="2043" height="1025" alt="Screenshot 2025-09-11 at 3 36 46 PM (1)" src="https://github.com/user-attachments/assets/915656c6-96bd-467a-864b-8a49eecdda6d" />


### 📈 Five Analytics Tabs

1. **📊 Trends**: Daily usage and cost trends with multi-line charts
2. **🎯 Usage Patterns**: Pie charts, heatmaps, and top customer rankings
3. **💰 Balance Analysis**: Waterfall charts and balance trends over time
4. **⚡ Run Rate Analysis**: Consumption projections and balance depletion forecasting
5. **📋 Contract Usage Report**: Active contract monitoring with overage predictions

### 🎯 Run Rate Analysis
- Configurable analysis periods (3, 7, 14, or 30 days)
- Daily/weekly/monthly consumption projections
- Balance depletion timeline with color-coded urgency
- Customer-by-customer run rate comparison
- Export capabilities for further analysis

### 📋 Contract Usage Monitoring
- **Capacity Tracking**: Monitor contract capacity vs. actual usage
- **Overage Predictions**: Calculate days until capacity overage
- **Visual Projections**: Interactive charts showing actual vs. predicted consumption
- **Renewal Intelligence**: Automatic recommendations for contract renewals
- **12-Month Run Rate**: Projected annual consumption for upsell opportunities

### 📥 Export & Data Access
- Download usage and balance data as CSV
- Properly formatted reports with currency symbols
- Detailed data tables with sorting and filtering
- Run rate analysis exports

---

## 🚀 Quick Start (3 Steps)

### Prerequisites
- Snowflake account with **Streamlit in Snowflake** enabled
- Access to **BILLING** schema (contact Snowflake Support if needed)
- **ACCOUNTADMIN** role

### Step 1: Open `deploy.sql` in a Snowflake Worksheet

### Step 2: Paste `streamlit_app.py` code between the `$` markers
```sql
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS
$
-- PASTE streamlit_app.py CONTENTS HERE --
$;
```

### Step 3: Run the script & grant access
```sql
GRANT ROLE BILLING_DASHBOARD_USER TO USER your_username;
```

**Done! Access at:** Projects → Streamlit → `billing_dashboard`

---

### Minimal Deploy (If you already have BILLING access)
```sql
-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;

-- Create app (paste streamlit_app.py between $)
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS $ 
-- paste streamlit_app.py here
$;
```

---

## 📁 Project Structure

```
reseller-billing/
├── streamlit_app.py          # Main application (deploy this to Snowflake)
├── deploy.sql                # Complete deployment script
├── README.md                 # This file
│
├── docs/                     # 📚 Documentation
│   ├── DEPLOYMENT_GUIDE.md   # Detailed deployment instructions
│   ├── QUICK_DEPLOY.md       # Quick start guide
│   ├── PARTNER_SETUP.md      # Partner configuration guide
│   ├── TESTING_GUIDE.md      # Testing procedures
│   └── RUN_RATE_FEATURES.md  # Run rate analysis documentation
│
└── archive/                  # 🗄️ Archived files
    ├── MINIMAL_DEPLOY.sql    # Minimal deployment option
    ├── verify_schema.sql     # Schema verification script
    └── ...
```

---

## 📊 Data Sources

The application uses Snowflake's BILLING schema views:

| View | Purpose |
|------|---------|
| **PARTNER_USAGE_IN_CURRENCY_DAILY** | Daily credit and currency usage by account |
| **PARTNER_REMAINING_BALANCE_DAILY** | Daily balance snapshots (capacity, rollover, free usage) |
| **PARTNER_CONTRACT_ITEMS** | Contract terms, capacity, and dates |
| **PARTNER_RATE_SHEET_DAILY** | Effective rates for usage calculation |

---

## 🔐 Security & Permissions

**Important:** The Streamlit app runs as the viewing user, not as a service account.

### Required Permissions
Users need:
- ✅ `SELECT` access to `SNOWFLAKE.BILLING.*` views
- ✅ `USAGE` on the warehouse
- ✅ `USAGE` on the Streamlit app

### What Gets Created
The deployment script (`deploy.sql`) creates:
- **Role**: `BILLING_DASHBOARD_USER` with BILLING schema access
- **Warehouse**: `BILLING_DASHBOARD_WH` (XSMALL, auto-suspend 60s)
- **Streamlit App**: `billing_dashboard` with embedded code
- **Proper Grants**: Secure access to billing data

---

## 🛠️ Technical Details

### Built With
- **Python 3.9+**
- **Streamlit** (native Snowflake integration)
- **Pandas** for data manipulation
- **Plotly** for interactive visualizations

### Performance Features
- **Smart Caching**: 1-hour TTL for query results
- **Query Limits**: 100K rows max, 5-minute timeout
- **Efficient Queries**: Optimized SQL for fast data retrieval
- **Auto-suspend Warehouse**: Minimizes compute costs

### UI/UX Features
- Responsive design with modern styling
- Color-coded alerts (🔴 Critical, 🟡 Warning, 🟢 Healthy)
- Enhanced metric cards with gradients
- Interactive charts with drill-down capabilities
- Date range presets (Last 7/30/90 days, Current/Last Month)

---

## 📖 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Step-by-step deployment instructions
- **[Quick Deploy](docs/QUICK_DEPLOY.md)**: Fast setup for experienced users
- **[Partner Setup](docs/PARTNER_SETUP.md)**: Multi-partner configuration
- **[Testing Guide](docs/TESTING_GUIDE.md)**: Verification and testing procedures
- **[Run Rate Features](docs/RUN_RATE_FEATURES.md)**: Run rate analysis deep dive

---

## 🆘 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"Table doesn't exist"** | Verify BILLING schema access with Snowflake Support |
| **"Permission denied"** | Ensure ACCOUNTADMIN role or proper grants |
| **"No data" in dashboard** | Check date range, billing data availability, and filters |
| **Cache issues** | Press `C` in app to clear cache, then rerun |
| **Column name errors** | Ensure you're using the latest version of `streamlit_app.py` |

### Quick Verification
```sql
-- Test BILLING schema access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;

-- Verify app status
SHOW STREAMLIT APPS;
DESC STREAMLIT billing_dashboard;

-- Check warehouse
SHOW WAREHOUSES LIKE 'BILLING_DASHBOARD_WH';
```

---

## 🔄 Maintenance

### Updating the Application
```sql
-- Replace the Streamlit code
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS
$$ 
-- Paste new streamlit_app.py code here
$$;
```

### Monitoring Costs
```sql
-- Monitor warehouse usage
SELECT * 
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH'
ORDER BY START_TIME DESC
LIMIT 100;

-- Check app query history
SELECT * 
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE WAREHOUSE_NAME = 'BILLING_DASHBOARD_WH'
ORDER BY START_TIME DESC
LIMIT 100;
```

---

## 🎯 Use Cases

- **Reseller Account Managers**: Monitor customer consumption and proactively manage capacity
- **Finance Teams**: Track costs and create budget forecasts
- **Sales Teams**: Identify upsell opportunities based on usage trends
- **Operations**: Ensure customers stay within contracted capacity
- **Executive Dashboards**: High-level consumption and revenue tracking

---

## 📞 Support & Contributing

### Getting Help
- **BILLING Schema Access**: Contact Snowflake Support
- **Application Issues**: Check Streamlit logs and error messages
- **Permissions**: Work with your Snowflake ACCOUNTADMIN

### Contributing
Contributions are welcome! Please ensure:
- Code follows existing style and patterns
- All features are documented
- SQL queries are optimized
- Security best practices are maintained

---

## 📝 License

This project is provided as-is for Snowflake reseller and distributor customers with access to the BILLING schema.

---

## 🎉 Ready to Get Started?

1. **Review the [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**
2. **Run `deploy.sql` in your Snowflake account**
3. **Grant access to your users**
4. **Start monitoring your reseller billing!**

---

*Built with ❤️ for Snowflake reseller partners*

*Compatible with Snowflake accounts that have BILLING schema access enabled*
