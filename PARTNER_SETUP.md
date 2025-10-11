# 🚀 Partner Testing Setup Guide

## Quick Start for Testing Partners

Hi! Thanks for helping test the Snowflake Billing Dashboard. This guide will get you up and running quickly.

---

## 📍 GitHub Repository

**Repository:** https://github.com/sfc-gh-jasvestis/reseller-billing-app

### What You'll Find
- `streamlit_app.py` - Main application code (ready to deploy)
- `TESTING_GUIDE.md` - **START HERE** - Comprehensive testing instructions
- `verify_schema.sql` - Run this first to verify your database schema
- `DEPLOYMENT_GUIDE.md` - How to deploy to Snowflake
- `SCHEMA_VERIFICATION_RESULTS.md` - Technical details about the fix
- `CHANGELOG.md` - What changed in this version

---

## 🎯 What Needs Testing (Priority Order)

### 1. CRITICAL: Contract Usage Report Bug Fix
**Issue Fixed:** SQL error when loading Contract Usage Report tab  
**Test:** Make sure the Contract Usage Report tab loads without errors

See `TESTING_GUIDE.md` → Test 1 for detailed steps.

### 2. Verify Calculations
**Test:** Confirm contract metrics are accurate  
See `TESTING_GUIDE.md` → Test 2 for validation queries.

### 3. Regression Testing
**Test:** Make sure other tabs still work  
See `TESTING_GUIDE.md` → Tests 3-6 for complete coverage.

---

## 🔧 Prerequisites

Before you start testing, make sure you have:

- ✅ Snowflake account access
- ✅ Access to `SNOWFLAKE.BILLING` schema
- ✅ Role with SELECT permissions on:
  - `PARTNER_USAGE_IN_CURRENCY_DAILY`
  - `PARTNER_REMAINING_BALANCE_DAILY`
  - `PARTNER_CONTRACT_ITEMS`
  - `PARTNER_RATE_SHEET_DAILY`
- ✅ Streamlit in Snowflake feature enabled
- ✅ Active contract data (for Contract Usage Report testing)

---

## 📥 Getting Started

### Step 1: Clone the Repository
```bash
git clone https://github.com/sfc-gh-jasvestis/reseller-billing-app.git
cd reseller-billing-app
```

### Step 2: Verify Your Database Schema
```sql
-- Copy contents of verify_schema.sql and run in Snowflake
-- This confirms all required columns exist
```

### Step 3: Deploy to Snowflake
Choose your deployment method:

#### Option A: Update Existing App (Fastest)
```sql
-- If you already have the app deployed
ALTER STREAMLIT billing_dashboard 
SET MAIN_FILE = '<paste streamlit_app.py contents>';
```

#### Option B: Fresh Deployment
```sql
-- Follow the complete guide in DEPLOYMENT_GUIDE.md
-- Or use QUICK_DEPLOY.md for minimal setup
```

### Step 4: Start Testing
Open `TESTING_GUIDE.md` and follow the test plan starting with Test 1.

---

## 🆘 Quick Help

### "I don't have access to BILLING schema"
Contact your Snowflake account admin to:
1. Request BILLING schema access (requires Snowflake Support to enable)
2. Get necessary permissions granted

### "I see a different error"
1. Check the exact error message
2. Run `verify_schema.sql` to diagnose
3. Look at Snowflake query history for details
4. See `TESTING_GUIDE.md` → Debugging Tips section

### "How do I report test results?"
Use the template at the bottom of `TESTING_GUIDE.md` to document your findings.

---

## 📊 Test Results Reporting

### Where to Report
Create an issue on GitHub or send results via email with:

1. **Test Status:** PASS ✅ / FAIL ❌
2. **Environment:** Your Snowflake account/region
3. **Test Details:** Which tests passed/failed
4. **Screenshots:** If applicable (especially for UI issues)
5. **Error Messages:** Full text of any errors

### Use This Quick Template
```markdown
## Test Results
**Tester:** [Your Name]
**Date:** [Date]
**Environment:** [Snowflake Account]

### Critical Tests
- [ ] Test 1: Contract Usage Report - No SQL errors
- [ ] Test 2: Calculations accurate
- [ ] Test 3: Other tabs functional

### Status
- Overall: ✅ READY / ❌ ISSUES FOUND / ⚠️ NEEDS REVIEW
- Critical Issues: [List or "None"]
- Minor Issues: [List or "None"]

### Notes
[Any additional observations]
```

---

## 📚 Document Quick Reference

| Document | When to Use |
|----------|-------------|
| `TESTING_GUIDE.md` | **Start here** - Complete test plan and instructions |
| `verify_schema.sql` | Run first to verify your database |
| `DEPLOYMENT_GUIDE.md` | How to deploy the app |
| `QUICK_DEPLOY.md` | Fast deployment option |
| `SCHEMA_VERIFICATION_RESULTS.md` | Technical details about the fix |
| `CHANGELOG.md` | What changed and why |
| `README.md` | General project information |
| `RUN_RATE_FEATURES.md` | Documentation for Run Rate features |

---

## 🔄 Latest Changes (Version 1.1.0)

### Bug Fix
**Fixed:** Contract Usage Report was throwing SQL compilation error  
**Cause:** Query referenced non-existent column `CAPACITY_TYPE_NAME`  
**Solution:** Removed the unused column from query  
**Impact:** Zero functional impact - column was never used

### Added Documentation
- Comprehensive testing guide
- Schema verification scripts
- Technical validation documentation
- This partner setup guide

---

## 💡 Testing Tips

1. **Start Small:** Test with 1 customer, 7 days first
2. **Test Edge Cases:** Try "All Customers", long date ranges, customers with no data
3. **Compare Results:** Use the SQL queries in `TESTING_GUIDE.md` to validate calculations
4. **Document Everything:** Screenshots help a lot for UI issues
5. **Check Performance:** Note any slow operations

---

## 🎯 Success Criteria

The testing is successful when:

- ✅ Contract Usage Report tab loads without SQL errors
- ✅ Contract metrics match manual calculations
- ✅ All other tabs still function normally
- ✅ No new bugs introduced
- ✅ Performance is acceptable

---

## 📞 Questions?

### During Testing
- Check the relevant .md file first
- Look in `TESTING_GUIDE.md` → Debugging Tips
- Review Snowflake query history for errors

### After Testing
- Document all findings in the test results template
- Include suggestions for improvements
- Note any confusing UI/UX elements

---

## ⏱️ Estimated Testing Time

- **Quick Smoke Test:** 15-30 minutes (Test 1 only)
- **Full Test Suite:** 1-2 hours (All tests)
- **Comprehensive:** 2-3 hours (Including edge cases and performance)

---

## 🙏 Thank You!

Your testing helps ensure this dashboard works reliably for all users. We appreciate your time and thorough testing!

**Happy Testing! 🚀**

---

**Version:** 1.1.0  
**Last Updated:** October 11, 2025  
**Repository:** https://github.com/sfc-gh-jasvestis/reseller-billing-app

