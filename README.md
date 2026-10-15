# ❄️ Snowflake Reseller Billing Dashboard

A **Streamlit in Snowflake** app for monitoring customer credit consumption, contract health, and feature adoption — powered by the `SNOWFLAKE.BILLING` schema.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)

<img width="1837" height="928" alt="image" src="https://github.com/user-attachments/assets/c446497e-2033-473a-844d-76610528f7e2" />

---

## Deploy in 2 Steps

### Prerequisites
- Run in your **reseller/distributor organization account** (or an account with ORGADMIN enabled) — the `SNOWFLAKE.BILLING` partner views do not exist anywhere else
- `ACCOUNTADMIN` role — only ACCOUNTADMIN can read the BILLING views, and the app runs with its **owner's** rights, so ACCOUNTADMIN must own the app
- Snowflake CLI (`snow`) or SnowSQL to upload files

### Step 1 — Run `deploy.sql`

Run it as ACCOUNTADMIN, including the `PUT` commands from the repository root (uploads `streamlit_app.py` and `environment.yml`). It creates the warehouse, stage, app, and a viewer role.

### Step 2 — Grant access to your users
```sql
GRANT ROLE BILLING_DASHBOARD_USER TO USER <username>;
```

Viewers need only USAGE on the app (granted by `deploy.sql`); they don't need any BILLING grants.

That's it. The app is now available under **Projects → Streamlit → `billing_dashboard`**.

---

## Live Data vs. Demo Mode

The app detects which mode to use **automatically** — no configuration required.

| Scenario | What happens |
|----------|-------------|
| BILLING views are readable | Live customer data loads; no banner shown |
| BILLING views are missing or unreadable | App uses demo data and shows an info banner (never mixes live and demo rows) |

To override auto-detection, set the `USE_DEMO_DATA` environment variable: `true` forces demo data (e.g. for a sales demo); `false` forces live data and shows an error if the views can't be read.

---

## What's Inside

| Tab | Description |
|-----|-------------|
| 🏠 **Account Overview** | Credits-only summary, safe to share with customers |
| 📊 **Trends** | Portfolio health, alerts, daily cost trends, **cost anomalies** (per customer × service, z-score vs prior 28 days) and **customer growth** (last 30 vs prior 30 days) |
| 🎯 **Usage Patterns** | Spend by feature, by account, by **rating type** (compute / storage / data transfer) and by **service per customer** |
| 💰 **Financial Health** | Run rate, **on-demand (overage) spend**, **effective rates** per customer with rate-change alerts, **credits & other charges**, contract status with a **forecast range** and **renewal sizing** |
| 🔬 **Feature Adoption** | Usage per `SERVICE_TYPE` per customer and upsell opportunities |

Usage totals count consumption only. Rebates, support credits and other non-consumption billing types are listed separately, and month-close adjustment rows are excluded unless **Include billing adjustments** is ticked in the sidebar.

Forecasts and anomaly detection run in pandas inside the app. They don't create any Snowflake objects.

---

## Internationalization (i18n)

The dashboard supports multiple languages with a built-in translation system.

| Language | Code | Status |
|----------|------|--------|
| English  | `en` | Default |
| Japanese | `ja` | Fully translated |

Users can switch languages from the sidebar language selector. The chosen language is synced to the URL query parameter `?lang=`, so bookmarking the URL preserves the preference across sessions.

| URL | Behavior |
|-----|----------|
| `https://<app-url>` | Opens in English (default) |
| `https://<app-url>?lang=ja` | Opens in Japanese |
| `https://<app-url>?lang=en` | Opens in English (explicit) |

Sharing a `?lang=ja` link with colleagues opens the dashboard in Japanese for them as well. Invalid language codes fall back to English automatically.

### How It Works

- All UI strings are defined in the `TRANSLATIONS` dictionary at the top of `streamlit_app.py`, keyed by language code (`en`, `ja`, etc.)
- The helper function `t(key, **kwargs)` returns the translated string for the current language, with automatic fallback to English if a key is missing
- Feature use-case descriptions use a dedicated `t_usecase(feature_key)` helper
- Translation keys support Python format strings for dynamic values (e.g. `t("kpi_vs_last_week", value=12.3)`)

### Adding a New Language

1. Add the language code and display name to `SUPPORTED_LANGUAGES`:
   ```python
   SUPPORTED_LANGUAGES = {"en": "English", "ja": "日本語", "ko": "한국어"}
   ```
2. Add a new entry in the `TRANSLATIONS` dictionary with all keys translated:
   ```python
   TRANSLATIONS["ko"] = {
       "app_title": "Snowflake 크레딧 사용량 대시보드",
       # ... all other keys
   }
   ```
3. No other code changes are needed — the sidebar selector and `t()` function pick up new languages automatically.

---

## Data Sources

| View | Purpose | Required |
|------|---------|----------|
| `PARTNER_USAGE_IN_CURRENCY_DAILY` | Daily usage and cost per customer account, incl. `SERVICE_TYPE`, `BILLING_TYPE`, `RATING_TYPE`, `IS_ADJUSTMENT` and the `overage` usage-type prefix | Yes |
| `PARTNER_REMAINING_BALANCE_DAILY` | Daily balance snapshots | Yes |
| `PARTNER_CONTRACT_ITEMS` | Contract terms and capacity | Yes |
| `PARTNER_RATE_SHEET_DAILY` | Effective (discounted) price per credit per customer, service and region | Optional: without it the Rates section says it is unavailable |

`SERVICE_TYPE` display names come from Snowflake's documented list, which is not exhaustive. `AI_SERVICES` (Cortex) is an assumed value. Any unlisted service type shows its raw name, so check the names against your live data once after deploying.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Object does not exist or not authorized` on a `PARTNER_*` view | The account isn't a reseller org account, or the app owner isn't ACCOUNTADMIN. Check `SHOW VIEWS LIKE 'PARTNER_%' IN SCHEMA SNOWFLAKE.BILLING;` |
| Errors don't match this code | The deployed app may be an older version — re-upload the files (`deploy.sql` Step 3) |
| No data showing | Check the date range filter in the sidebar |
| Stale data | Click **Refresh Data** in the sidebar |

```sql
-- Verify BILLING access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;
```

---

*Built for Snowflake reseller partners.*

---

## Legal

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

This is a personal project and is **not an official Snowflake offering**. It comes with **no support or warranty**. Use it at your own risk. Snowflake has no obligation to maintain, update, or support this code. Do not use this code in production without thorough review and testing.
