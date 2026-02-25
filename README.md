# ❄️ Snowflake Reseller Billing Dashboard

A **Streamlit in Snowflake** app for monitoring customer credit consumption, contract health, and feature adoption — powered by the `SNOWFLAKE.BILLING` schema.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)

<img width="1902" height="815" alt="image" src="https://github.com/user-attachments/assets/c71c7e11-9861-40f0-bfb4-3f17876f03cf" />

---

## Deploy in 2 Steps

### Prerequisites
- Snowflake account with Streamlit in Snowflake enabled
- Access to `SNOWFLAKE.BILLING` schema (request via Snowflake Support if needed)
- `ACCOUNTADMIN` role

### Step 1 — Run `deploy.sql` in a Snowflake Worksheet

Opens a worksheet, pastes the file, and runs it. This creates the warehouse, role, and Streamlit app automatically.

### Step 2 — Grant access to your users
```sql
GRANT ROLE BILLING_DASHBOARD_USER TO USER <username>;
```

That's it. The app is now available under **Projects → Streamlit → `billing_dashboard`**.

---

## Live Data vs. Demo Mode

The app detects which mode to use **automatically** — no configuration required.

| Scenario | What happens |
|----------|-------------|
| BILLING schema is accessible | Live customer data loads; no banner shown |
| BILLING schema is inaccessible | App falls back to demo data and shows an info banner |

Once deployed in your SPN account and the `BILLING_DASHBOARD_USER` role has been granted, live data loads seamlessly on first open.

To force demo mode at any time (e.g. for a sales demo), set this flag near the top of `streamlit_app.py`:

```python
USE_DEMO_DATA = True  # line ~107
```

---

## What's Inside

| Tab | Description |
|-----|-------------|
| 📊 **Trends** | Daily credit and cost trends per customer |
| 🎯 **Usage Patterns** | Customer usage breakdown and growth comparisons |
| 💰 **Financial Health** | Balance projections, run rate, and contract capacity |
| 🔬 **Feature Adoption** | Feature usage per customer and upsell opportunities |

---

## Data Sources

| View | Purpose |
|------|---------|
| `PARTNER_USAGE_IN_CURRENCY_DAILY` | Daily credit usage by customer account |
| `PARTNER_REMAINING_BALANCE_DAILY` | Daily balance snapshots |
| `PARTNER_CONTRACT_ITEMS` | Contract terms and capacity |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Object does not exist or not authorized` | Request `SNOWFLAKE.BILLING` access from Snowflake Support |
| No data showing | Check the date range filter in the sidebar |
| Stale data | Click **Refresh Data** in the sidebar |

```sql
-- Verify BILLING access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;
```

---

*Built for Snowflake reseller partners.*
