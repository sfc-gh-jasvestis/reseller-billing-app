# ❄️ Snowflake Reseller Billing Dashboard

A **Streamlit in Snowflake** application that gives Snowflake reseller partners a clear view of customer credit consumption, contract health, and feature adoption — all powered by the `SNOWFLAKE.BILLING` schema.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

---

## Dashboard Tabs

| Tab | What it shows |
|-----|---------------|
| **📊 Trends** | Daily credit and cost trends per customer with multi-line charts |
| **🎯 Usage Patterns** | Customer usage breakdown, heatmaps, and growth comparisons |
| **💰 Financial Health** | Balance & run rate projections + contract capacity vs. actual usage |
| **🔬 Feature Adoption** | Feature usage per customer, AI/ML adoption signals, and upsell opportunities |

---

## Data Sources

All data is read from the `SNOWFLAKE.BILLING` schema — the authoritative reseller view.

| View | Purpose |
|------|---------|
| `PARTNER_USAGE_IN_CURRENCY_DAILY` | Daily credit and currency usage by customer account |
| `PARTNER_REMAINING_BALANCE_DAILY` | Daily balance snapshots (capacity, rollover) |
| `PARTNER_CONTRACT_ITEMS` | Contract terms, capacity amounts, and dates |

> If the BILLING schema is unavailable, the app automatically falls back to built-in demo data so you can explore the interface immediately.

---

## Quick Deploy (3 Steps)

### Prerequisites
- Snowflake account with **Streamlit in Snowflake** enabled
- Access to `SNOWFLAKE.BILLING` schema (request via Snowflake Support if needed)
- **ACCOUNTADMIN** role

### Step 1 — Run `deploy.sql` in a Snowflake Worksheet

This creates:
- **Role** `BILLING_DASHBOARD_USER` with BILLING schema read access
- **Warehouse** `BILLING_DASHBOARD_WH` (XSMALL, auto-suspend 60s)
- **Streamlit app** `billing_dashboard`

### Step 2 — Grant access to your users
```sql
GRANT ROLE BILLING_DASHBOARD_USER TO USER your_username;
```

### Step 3 — Open the app
Navigate to **Projects → Streamlit → `billing_dashboard`** in your Snowflake account.

---

## Minimal Deploy (if you already have BILLING access)

```sql
-- Warehouse
CREATE WAREHOUSE IF NOT EXISTS BILLING_DASHBOARD_WH
    WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;

-- App (paste streamlit_app.py between the $$ markers)
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS $$
-- paste streamlit_app.py contents here
$$;
```

---

## Project Structure

```
reseller-billing/
├── streamlit_app.py   # Main application — deploy this to Snowflake
├── deploy.sql         # Full deployment script (roles, warehouse, app, grants)
└── README.md
```

---

## Security & Permissions

The app runs as the **viewing user**, not a service account.

Users need:
- `SELECT` on `SNOWFLAKE.BILLING.*` views
- `USAGE` on the warehouse
- `USAGE` on the Streamlit app

The `deploy.sql` script sets all of this up automatically via the `BILLING_DASHBOARD_USER` role.

---

## Updating the App

```sql
CREATE OR REPLACE STREAMLIT billing_dashboard
    QUERY_WAREHOUSE = 'BILLING_DASHBOARD_WH'
AS $$
-- paste updated streamlit_app.py here
$$;
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Object does not exist or not authorized` | Your user lacks access to `SNOWFLAKE.BILLING` — contact Snowflake Support |
| No data in dashboard | Check date range filter and that billing data exists for the selected period |
| Cache stale | Click **Refresh Data** in the sidebar |
| Column errors | Ensure you're running the latest `streamlit_app.py` |

### Verify BILLING access
```sql
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;
```

---

*Built for Snowflake reseller and distributor partners with BILLING schema access.*
