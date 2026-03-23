# ❄️ Snowflake Reseller Billing Dashboard

A **Streamlit in Snowflake** app for monitoring customer credit consumption, contract health, and feature adoption — powered by the `SNOWFLAKE.BILLING` schema.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)

<img width="1837" height="928" alt="image" src="https://github.com/user-attachments/assets/c446497e-2033-473a-844d-76610528f7e2" />

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

---

## Legal

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

This is a personal project and is **not an official Snowflake offering**. It comes with **no support or warranty**. Use it at your own risk. Snowflake has no obligation to maintain, update, or support this code. Do not use this code in production without thorough review and testing.
