# Testing Guide for Snowflake Billing Dashboard

## 🎯 Recent Changes (Need Testing)

### Critical Fix: Contract Usage Report Error
**Date:** October 11, 2025  
**Issue:** SQL compilation error on Contract Usage Report tab  
**Fix:** Removed non-existent `CAPACITY_TYPE_NAME` column from query

**Priority:** HIGH - Please test this first!

---

## 🚀 Quick Start for Testing

### Prerequisites
1. Snowflake account with:
   - Access to `SNOWFLAKE.BILLING` schema
   - `BILLING_DASHBOARD_USER` role (or equivalent permissions)
   - Active contract data in `PARTNER_CONTRACT_ITEMS`
2. Streamlit in Snowflake feature enabled

### Deployment Steps

1. **Run Schema Verification First:**
   ```sql
   -- Execute verify_schema.sql in Snowflake
   -- This confirms all required columns exist
   ```

2. **Deploy to Snowflake:**
   ```sql
   -- Option A: Update existing app (recommended)
   ALTER STREAMLIT billing_dashboard SET MAIN_FILE = '<paste streamlit_app.py contents>';
   
   -- Option B: Fresh deployment
   -- Follow instructions in DEPLOYMENT_GUIDE.md
   ```

3. **Grant Access:**
   ```sql
   GRANT USAGE ON STREAMLIT billing_dashboard TO ROLE BILLING_DASHBOARD_USER;
   GRANT ROLE BILLING_DASHBOARD_USER TO USER <test_user>;
   ```

---

## 🧪 Test Plan

### Test 1: Contract Usage Report (CRITICAL)
**Goal:** Verify the SQL error is fixed

**Steps:**
1. Open the dashboard in Snowflake
2. Navigate to "Advanced Analytics" section
3. Click on the **"📋 Contract Usage Report"** tab
4. Select a customer with active contracts from the dropdown

**Expected Results:**
- ✅ No SQL compilation error appears
- ✅ Contract metrics display:
  - Capacity Purchased
  - Total Capacity Used
  - Overage (if applicable)
  - Days until Overage
- ✅ Charts render showing:
  - Actual consumption (blue area)
  - Predicted consumption (orange area)
  - Cumulative consumption line (black)
  - Capacity line (gray dashed)

**Previous Error (Should NOT appear):**
```
❌ Error loading contract data: (1304): 01bf91ec-3201-ff0c-0007-ac5a00ea0ec6: 000904 (42000): 
SQL compilation error: error line 4 at position 12 invalid identifier 'CAPACITY_TYPE_NAME'
```

**If Test Fails:**
- Run `verify_schema.sql` to check database schema
- Check Snowflake query history for actual error
- Verify `PARTNER_CONTRACT_ITEMS` view is accessible

---

### Test 2: Contract Calculations Accuracy
**Goal:** Verify contract metrics are calculated correctly

**Test Data Needed:**
- Customer with known contract values
- Recent usage data for that customer

**Manual Verification Query:**
```sql
-- Get contract capacity
SELECT 
    SOLD_TO_CUSTOMER_NAME,
    CONTRACTED_AMOUNT,
    COALESCE(ROLLOVER_AMOUNT, 0) AS ROLLOVER,
    COALESCE(FREE_USAGE_AMOUNT, 0) AS FREE_USAGE,
    (CONTRACTED_AMOUNT + COALESCE(ROLLOVER_AMOUNT, 0) + COALESCE(FREE_USAGE_AMOUNT, 0)) AS TOTAL_CAPACITY,
    CONTRACT_ITEM_START_DATE,
    CONTRACT_ITEM_END_DATE,
    CURRENCY
FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS
WHERE SOLD_TO_CUSTOMER_NAME = '<TEST_CUSTOMER>'
  AND CONTRACT_ITEM_END_DATE >= CURRENT_DATE;

-- Get actual usage
SELECT 
    SUM(USAGE_IN_CURRENCY) AS TOTAL_USAGE,
    COUNT(DISTINCT USAGE_DATE) AS DAYS_WITH_USAGE,
    MIN(USAGE_DATE) AS FIRST_USAGE,
    MAX(USAGE_DATE) AS LAST_USAGE
FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY
WHERE SOLD_TO_CUSTOMER_NAME = '<TEST_CUSTOMER>'
  AND USAGE_DATE BETWEEN '<CONTRACT_START>' AND '<CONTRACT_END>';
```

**Compare Against Dashboard:**
- ✅ Capacity Purchased = CONTRACTED_AMOUNT + ROLLOVER + FREE_USAGE
- ✅ Total Used = Sum of USAGE_IN_CURRENCY
- ✅ Used % = (Total Used / Capacity Purchased) × 100
- ✅ Overage = max(0, Total Used - Capacity Purchased)

---

### Test 3: Other Dashboard Tabs
**Goal:** Ensure other features still work after the fix

#### Test 3a: Trends Tab
1. Select date range (e.g., Last 30 days)
2. Select a customer
3. Navigate to "📊 Trends" tab

**Expected:**
- ✅ Credit usage trend chart displays
- ✅ Cost trend chart displays
- ✅ Charts show data for selected period

#### Test 3b: Usage Patterns Tab
1. Navigate to "🎯 Usage Patterns" tab

**Expected:**
- ✅ Usage distribution pie chart displays
- ✅ Top customers bar chart displays
- ✅ Charts match selected filters

#### Test 3c: Balance Analysis Tab
1. Navigate to "💰 Balance Analysis" tab

**Expected:**
- ✅ Balance waterfall chart displays
- ✅ Balance trends over time chart displays
- ✅ Balance metrics are accurate

#### Test 3d: Run Rate Analysis Tab
1. Navigate to "⚡ Run Rate Analysis" tab
2. Select run rate period (3, 7, 14, or 30 days)

**Expected:**
- ✅ Overall run rate metrics display:
  - Daily Run Rate
  - Weekly Projection
  - Monthly Projection
  - Days Until Depletion
- ✅ Customer run rate comparison table displays
- ✅ Bar charts show top customers
- ✅ Depletion timeline chart displays

---

### Test 4: Data Export
**Goal:** Verify export functionality works

**Steps:**
1. Scroll to "📥 Export Data" section
2. Click "📊 Download Usage Data"
3. Click "💰 Download Balance Data"
4. Click "⚡ Download Run Rate Analysis"

**Expected:**
- ✅ CSV files download successfully
- ✅ Files contain correct data for selected filters
- ✅ Files are properly formatted with headers

---

### Test 5: Filter Combinations
**Goal:** Test various filter combinations

**Test Cases:**

| Test Case | Date Range | Customer | Expected Result |
|-----------|-----------|----------|-----------------|
| TC-5.1 | Last 7 days | All Customers | All tabs display aggregate data |
| TC-5.2 | Last 30 days | Specific Customer | All tabs filtered to that customer |
| TC-5.3 | Last 90 days | All Customers | Performance acceptable, data loads |
| TC-5.4 | Custom range | Specific Customer | Date range respected in all views |

---

### Test 6: Edge Cases
**Goal:** Test boundary conditions

#### Test 6a: Customer with No Contracts
1. Select a customer with no active contracts
2. Go to Contract Usage Report tab

**Expected:**
- ✅ Warning message: "No active contracts found for the selected customer."
- ✅ No error occurs

#### Test 6b: Customer with No Recent Usage
1. Select a customer with no usage in selected period
2. Go to Run Rate Analysis tab

**Expected:**
- ✅ Info message: "Not enough data to calculate run rates."
- ✅ No crashes or errors

#### Test 6c: Future Date Range
1. Try selecting dates in the future

**Expected:**
- ✅ Date picker prevents future dates
- ✅ Or shows "No data found" message

---

## 🐛 Known Issues / Limitations

### Current Limitations
1. **Multiple Contracts:** If a customer has multiple active contracts, only one is displayed at a time
2. **Cache Duration:** Data refreshes hourly (configurable via `CACHE_TTL_SECONDS`)
3. **Row Limit:** Queries limited to 100,000 rows (configurable via `QUERY_LIMITS['max_rows']`)

### Not Issues (By Design)
- Run rate calculations use recent period only (configurable: 3, 7, 14, or 30 days)
- "Days Until Depletion" returns N/A if no balance data available
- Overage shows $0.00 if usage is below capacity

---

## 📊 Performance Benchmarks

### Expected Load Times
| Operation | Expected Time | Alert If Exceeds |
|-----------|--------------|------------------|
| Initial page load | < 3 seconds | 10 seconds |
| Switch between tabs | < 1 second | 3 seconds |
| Change date filter | < 5 seconds | 15 seconds |
| Change customer filter | < 5 seconds | 15 seconds |
| Generate export | < 2 seconds | 5 seconds |

### Data Volume Tests
Test with:
- ✅ Small dataset: 1 customer, 7 days
- ✅ Medium dataset: 10 customers, 30 days
- ✅ Large dataset: All customers, 90 days

---

## 🔍 Debugging Tips

### If Contract Usage Report Still Fails

1. **Check Snowflake Query History:**
   ```sql
   SELECT 
       query_text,
       error_message,
       execution_status
   FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
   WHERE USER_NAME = CURRENT_USER()
     AND START_TIME >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
     AND ERROR_MESSAGE IS NOT NULL
   ORDER BY START_TIME DESC;
   ```

2. **Verify Schema Access:**
   ```sql
   -- Test each view
   SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_CONTRACT_ITEMS LIMIT 1;
   SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY LIMIT 1;
   SELECT COUNT(*) FROM SNOWFLAKE.BILLING.PARTNER_REMAINING_BALANCE_DAILY LIMIT 1;
   ```

3. **Check Permissions:**
   ```sql
   SHOW GRANTS TO ROLE BILLING_DASHBOARD_USER;
   ```

4. **Review Streamlit Logs:**
   - In Snowflake UI, go to Projects > Streamlit > billing_dashboard
   - Click "View Logs" to see error details

---

## ✅ Test Completion Checklist

### Critical Tests (Must Pass)
- [ ] Test 1: Contract Usage Report loads without SQL error
- [ ] Test 2: Contract calculations are accurate
- [ ] Test 3: All other tabs still function

### Important Tests (Should Pass)
- [ ] Test 4: Data export works
- [ ] Test 5: Filter combinations work correctly
- [ ] Test 6: Edge cases handled gracefully

### Performance Tests (Nice to Have)
- [ ] Load times within expected ranges
- [ ] Large datasets perform acceptably
- [ ] No memory or timeout issues

---

## 📝 Test Results Template

Please document your findings:

```markdown
## Test Results - [Date]
**Tester:** [Name]
**Environment:** [Snowflake Account/Region]

### Test 1: Contract Usage Report
- Status: ✅ PASS / ❌ FAIL
- Notes: 
- Screenshots: [if applicable]

### Test 2: Contract Calculations
- Status: ✅ PASS / ❌ FAIL
- Manual calculation matches dashboard: YES / NO
- Discrepancies found:

### Test 3: Other Tabs
- Trends: ✅ / ❌
- Usage Patterns: ✅ / ❌
- Balance Analysis: ✅ / ❌
- Run Rate Analysis: ✅ / ❌

### Overall Assessment
- Ready for production: YES / NO / NEEDS WORK
- Critical issues found:
- Minor issues found:
- Recommendations:
```

---

## 🆘 Support

### Questions or Issues?
1. Check `SCHEMA_VERIFICATION_RESULTS.md` for detailed technical info
2. Run `verify_schema.sql` to diagnose schema issues
3. Review `DEPLOYMENT_GUIDE.md` for setup instructions
4. Check `README.md` for general documentation

### Reporting Bugs
When reporting issues, please include:
1. Error message (exact text or screenshot)
2. Steps to reproduce
3. Selected filters (date range, customer)
4. Expected vs actual behavior
5. Snowflake query history (if available)

---

**Good luck with testing! 🚀**

