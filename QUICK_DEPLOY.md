# ⚡ Quick Deploy - 3 Simple Steps!

Deploy your Snowflake Reseller Billing Dashboard in under 5 minutes!

## 📌 **Choose Your Deployment**

### **Option A: Minimal** (Users already have BILLING access)
Use `MINIMAL_DEPLOY.sql` - Fastest! Only creates warehouse + app

### **Option B: Complete** (Need to set up permissions)
Use `deploy.sql` - Creates everything including role + permissions

---

## 🎯 **Super Simple Deployment**

### **Step 1: Copy Python Code** 📋
1. Open `streamlit_app.py` 
2. **Copy ALL the code** (Ctrl+A, Ctrl+C)

### **Step 2: Deploy in Snowflake** 🚀
1. Open `MINIMAL_DEPLOY.sql` OR `deploy.sql` in Snowflake worksheet
2. **Paste the Python code** into the `CREATE STREAMLIT` section (between `$$`)
3. **Run the script** ▶️

### **Step 3: Grant Access & Launch** 🔓

**For Minimal Setup:**
```sql
-- Grant to your existing role that has BILLING access
GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE YOUR_EXISTING_ROLE;
```

**For Complete Setup:**
```sql
-- Grant new role to yourself
GRANT ROLE BILLING_DASHBOARD_USER TO USER your_username;
```

**Access:** Projects > Streamlit > billing_dashboard 🎉

## ✅ **That's It!**

No file uploads, no stages, no complexity - just native Snowflake!

---

## 🔧 **What Gets Created**

### **Minimal Setup:**
- ✅ **Warehouse**: `BILLING_DASHBOARD_WH` (XSMALL, auto-suspend 60s)
- ✅ **Streamlit App**: `billing_dashboard` (your main application)

### **Complete Setup:**
- ✅ **Warehouse**: `BILLING_DASHBOARD_WH` (XSMALL, auto-suspend 60s)
- ✅ **Role**: `BILLING_DASHBOARD_USER` (with BILLING schema access)
- ✅ **Streamlit App**: `billing_dashboard` (your main application)

## 🔑 **Key Insight**

The Streamlit app runs **as the viewing user**, not as a service account.
- Users need BILLING schema access to query data
- Minimal setup: assumes users already have it
- Complete setup: creates a role that grants it

## 📊 **Expected Features**

Once deployed, your dashboard provides:

- **Real-time Credit Monitoring** 📈
- **Interactive Visualizations** 🎨
- **Smart Alerts & Insights** 🚨
- **Advanced Filtering** 🔍
- **Data Export** 📥
- **Balance Tracking** 💰

## 🆘 **Quick Troubleshooting**

### **"Table doesn't exist" error**
```sql
-- Verify BILLING access
SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY;
```
*If this fails: Contact Snowflake Support for BILLING schema access*

### **"Permission denied" error**
- Ensure you have **ACCOUNTADMIN** role
- Or ask your admin to run the deployment script

### **Dashboard shows "No data"**
- Check your date range (try "Last 30 days")
- Verify you have recent billing data

## 🎉 **Success!**

**Total Deployment Time**: ~3-5 minutes ⚡

**Your billing dashboard is ready!** Access it at:
**Snowflake UI → Projects → Streamlit → billing_dashboard**

---

*Need detailed instructions? Check out `DEPLOYMENT_GUIDE.md`*