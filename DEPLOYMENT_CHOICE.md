# 🎯 Which Deployment Method Should I Use?

## Quick Decision Guide

### ❓ Do your users already have SELECT access to `SNOWFLAKE.BILLING` views?

**YES** → Use **MINIMAL_DEPLOY.sql**  
**NO** → Use **deploy.sql**  
**NOT SURE** → Use **deploy.sql** (safer option)

---

## Understanding the Difference

### 🔑 Key Concept

The Streamlit app **runs as the viewing user**, not as a service account or app identity.

This means when a user opens the dashboard, Snowflake executes all queries **as that user** with **that user's permissions**.

---

## Option A: Minimal Deployment

**File:** `MINIMAL_DEPLOY.sql`

### What It Creates
```
✅ Warehouse (BILLING_DASHBOARD_WH)
✅ Streamlit App (billing_dashboard)
❌ NO role creation
❌ NO BILLING schema permissions
```

### When to Use
- Your users already have a role with BILLING schema access
- You just need to deploy the app, not set up permissions
- You want the fastest deployment

### What Users Need (must already have)
```sql
-- Users must already have these permissions via some role:
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE <existing_role>;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE <existing_role>;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE <existing_role>;
```

### Example Scenario
*"Our team already has the RESELLER_ADMIN role that has BILLING access. We just need to deploy the Streamlit app for them to use."*

---

## Option B: Complete Deployment

**File:** `deploy.sql`

### What It Creates
```
✅ Warehouse (BILLING_DASHBOARD_WH)
✅ Role (BILLING_DASHBOARD_USER)
✅ BILLING schema permissions
✅ Streamlit App (billing_dashboard)
```

### When to Use
- You need to set up BILLING access from scratch
- You want a dedicated role specifically for this dashboard
- You prefer a clean, all-in-one deployment
- You're not sure if users have BILLING access

### What Gets Granted
```sql
-- Automatically creates and grants:
GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE BILLING_DASHBOARD_USER;
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;
```

### Example Scenario
*"We're setting up this dashboard for the first time and want to create a dedicated role with exactly the permissions needed."*

---

## Side-by-Side Comparison

| Feature | Minimal | Complete |
|---------|---------|----------|
| Creates Warehouse | ✅ | ✅ |
| Creates Streamlit App | ✅ | ✅ |
| Creates Role | ❌ | ✅ |
| Grants BILLING Permissions | ❌ | ✅ |
| Deployment Speed | Fastest | Fast |
| Setup Complexity | Lowest | Low |
| Best For | Existing permissions | New setup |

---

## 📋 Deployment Steps (Both Options)

### Step 1: Copy Python Code
1. Open `streamlit_app.py`
2. Copy **all** code (Ctrl+A / Cmd+A, then Ctrl+C / Cmd+C)

### Step 2: Choose & Execute
**Option A (Minimal):**
1. Open `MINIMAL_DEPLOY.sql` in Snowflake
2. Paste Python code between `$$` markers
3. Replace `YOUR_EXISTING_ROLE` with actual role name
4. Execute

**Option B (Complete):**
1. Open `deploy.sql` in Snowflake
2. Paste Python code between `$$` markers
3. Execute

### Step 3: Grant Access to Users
**Option A (Minimal):**
```sql
-- App uses existing role, just grant Streamlit access
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE YOUR_EXISTING_ROLE;
GRANT USAGE ON WAREHOUSE BILLING_DASHBOARD_WH TO ROLE YOUR_EXISTING_ROLE;
```

**Option B (Complete):**
```sql
-- Grant new role to users
GRANT ROLE BILLING_DASHBOARD_USER TO USER username1;
GRANT ROLE BILLING_DASHBOARD_USER TO USER username2;
```

---

## 🧪 Test Your Setup

### Verify BILLING Access (Before Minimal Deployment)
```sql
-- Switch to the role you plan to use
USE ROLE YOUR_EXISTING_ROLE;

-- Test BILLING access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;
```

**If this works** → You're ready for Minimal deployment  
**If this fails** → Use Complete deployment

---

## ❓ FAQ

### Q: Can I switch between deployment methods?
**A:** Yes! You can run the Complete deployment script even if you used Minimal first. It will just create the additional role and permissions.

### Q: What if I want multiple roles to access the dashboard?
**A:** 
- **Minimal**: Grant Streamlit access to each role
- **Complete**: Grant `BILLING_DASHBOARD_USER` to each user, OR grant Streamlit access to multiple roles

### Q: Do I need ACCOUNTADMIN role to deploy?
**A:** You need sufficient privileges to:
- Create warehouses
- Create roles (Complete only)
- Grant permissions
- Create Streamlit apps

Typically ACCOUNTADMIN or a custom admin role works.

### Q: Which method is more secure?
**A:** Both are equally secure! Complete deployment just provides cleaner role management.

### Q: Can I use a different warehouse?
**A:** Yes! Edit the `QUERY_WAREHOUSE` parameter in the CREATE STREAMLIT statement to use any warehouse your users have access to.

---

## 🎉 Still Not Sure?

**Use `deploy.sql` (Complete Deployment)**

It's the safest choice and gives you a dedicated role you can manage independently. You can always skip using the role if you don't need it.

---

*For detailed instructions, see `DEPLOYMENT_GUIDE.md`  
For quick start, see `QUICK_DEPLOY.md`*
