# Changelog

All notable changes to the Snowflake Billing Dashboard will be documented in this file.

## [1.1.0] - 2025-10-11

### 🐛 Bug Fixes

#### Contract Usage Report SQL Error (CRITICAL)
- **Issue:** Contract Usage Report tab was throwing SQL compilation error
- **Error Message:** `(42000): SQL compilation error: error line 4 at position 12 invalid identifier 'CAPACITY_TYPE_NAME'`
- **Root Cause:** Query was attempting to SELECT non-existent column `CAPACITY_TYPE_NAME` from `PARTNER_CONTRACT_ITEMS` view
- **Fix:** Removed `CAPACITY_TYPE_NAME` from SELECT statement in `load_contract_data()` function (line 783)
- **Impact:** No functional impact - column was never used in the application
- **Files Changed:** `streamlit_app.py`
- **Status:** ✅ Fixed and ready for testing

### 📚 Documentation

#### Added
- `TESTING_GUIDE.md` - Comprehensive testing guide for QA and partners
  - Step-by-step test plan
  - Expected results for all features
  - Edge case testing scenarios
  - Performance benchmarks
  - Debugging tips
  - Test results template

- `SCHEMA_VERIFICATION_RESULTS.md` - Technical documentation
  - Detailed root cause analysis
  - Calculation validation and formulas
  - Required columns from PARTNER_CONTRACT_ITEMS
  - Testing recommendations
  - Potential issues to watch for

- `verify_schema.sql` - Database verification script
  - Checks all columns in PARTNER_CONTRACT_ITEMS
  - Verifies calculation logic
  - Identifies NULL values
  - Provides sample data inspection queries

- `.gitignore` - Standard Python/Streamlit exclusions

- `CHANGELOG.md` - This file

### ✅ Validated

#### Contract Calculation Formulas
All formulas reviewed and confirmed mathematically correct:

1. **Capacity Calculation** (Line 449)
   ```python
   capacity_purchased = CONTRACTED_AMOUNT + ROLLOVER_AMOUNT + FREE_USAGE_AMOUNT
   ```
   - ✅ Correct formula
   - ✅ NULL handling implemented with `.get(column, 0)`

2. **Usage Calculation** (Line 462)
   ```python
   total_used = customer_usage['USAGE_IN_CURRENCY'].sum()
   ```
   - ✅ Correctly filters by contract period
   - ✅ Sums all usage within date range

3. **Overage Calculation** (Line 465)
   ```python
   overage = max(0, total_used - capacity_purchased)
   ```
   - ✅ Returns only positive overages
   - ✅ Returns 0 if under capacity

4. **Run Rate Calculations** (Lines 480-491)
   ```python
   daily_rate = recent_usage['USAGE_IN_CURRENCY'].sum() / actual_days
   days_until_overage = remaining_capacity / daily_rate
   annual_run_rate = daily_rate * 365
   ```
   - ✅ All formulas mathematically correct
   - ✅ Edge cases handled (division by zero, negative values)

5. **Utilization Percentage** (Line 509)
   ```python
   used_percent = (total_used / capacity_purchased * 100) if capacity_purchased > 0 else 0
   ```
   - ✅ Division by zero protection
   - ✅ Returns percentage 0-100+

---

## [1.0.0] - 2025-10-08 (Previous Release)

### ✨ Features

#### Core Dashboard
- Real-time credit usage monitoring
- Multi-customer support with filtering
- Customizable date range selection (Last 7/30/90 days, Current Month, Last Month, Custom)
- Responsive layout with modern UI

#### Analytics Tabs

1. **📊 Trends**
   - Enhanced trend charts with credit and cost metrics
   - Usage heatmap by week and day
   - Multi-line visualization by usage type

2. **🎯 Usage Patterns**
   - Usage distribution pie chart by type
   - Top customers by credit usage
   - Interactive filtering

3. **💰 Balance Analysis**
   - Balance waterfall chart showing breakdown
   - Balance trends over time
   - Free usage, capacity, rollover, and on-demand tracking

4. **⚡ Run Rate Analysis**
   - Overall run rate metrics (daily/weekly/monthly)
   - Customer-level run rate comparison
   - Days until balance depletion projections
   - Configurable run rate periods (3, 7, 14, 30 days)
   - Color-coded urgency indicators
   - Visual comparison charts

5. **📋 Contract Usage Report**
   - Active contract tracking
   - Capacity vs actual usage monitoring
   - Overage detection and alerts
   - Days until overage projection
   - Annual run rate estimation
   - Renewal recommendations
   - Contract usage visualization with predictions
   - Configurable run rate periods for projections

#### Metrics & KPIs
- Total credits used with week-over-week growth
- Total cost with trend indicators
- Active customer count
- Average daily credit consumption
- Balance metrics (free usage, capacity, rollover, on-demand)

#### Alerts & Insights
- High usage detection
- Usage growth/decline alerts
- Low balance warnings
- On-demand consumption alerts
- Intelligent threshold-based monitoring

#### Data Export
- Download usage data (CSV)
- Download balance data (CSV)
- Download run rate analysis (CSV)
- Formatted exports with proper numeric rounding
- Timestamped file names

#### Filtering & Controls
- Customer selection (All Customers or specific)
- Date range presets and custom ranges
- Advanced filters for usage types
- Real-time filter application

### 🔧 Technical Features
- Streamlit in Snowflake compatibility
- Caching with 1-hour TTL
- Query optimization with limits
- Responsive error handling
- Professional styling and theming
- Plotly interactive visualizations
- Pandas data processing

### 📊 Supported Snowflake Views
- `PARTNER_USAGE_IN_CURRENCY_DAILY`
- `PARTNER_REMAINING_BALANCE_DAILY`
- `PARTNER_CONTRACT_ITEMS`
- `PARTNER_RATE_SHEET_DAILY`

---

## 🔮 Future Enhancements (Planned)

### Potential Features
- Email report scheduling
- Real-time refresh option
- Multi-contract comparison for single customer
- Custom alert thresholds
- Forecasting with machine learning
- Budget vs actual tracking
- Cost optimization recommendations
- Historical trending analysis

### Performance Improvements
- Incremental data loading
- Advanced caching strategies
- Query result pagination
- Lazy loading for large datasets

---

## 📋 Upgrade Instructions

### From 1.0.0 to 1.1.0

1. **Backup Current Version** (Recommended)
   ```sql
   -- Get current app definition
   SELECT GET_DDL('STREAMLIT', 'billing_dashboard');
   -- Save output to a file
   ```

2. **Run Schema Verification**
   ```sql
   -- Execute verify_schema.sql to confirm compatibility
   -- Review results to ensure all columns exist
   ```

3. **Update Application Code**
   ```sql
   -- Option A: Update existing app
   ALTER STREAMLIT billing_dashboard 
   SET MAIN_FILE = '<paste contents of updated streamlit_app.py>';
   
   -- Option B: Recreate app
   DROP STREAMLIT billing_dashboard;
   -- Then follow deployment guide
   ```

4. **Test Critical Functionality**
   - Navigate to Contract Usage Report tab
   - Verify no SQL errors appear
   - Test with multiple customers
   - Validate calculations

5. **Clear Cache** (Optional but Recommended)
   - Refresh the browser page
   - Or wait for cache TTL to expire (1 hour)

### Rollback Procedure
If issues occur, you can rollback:
```sql
-- Use the backup from step 1
ALTER STREAMLIT billing_dashboard 
SET MAIN_FILE = '<paste backup code>';
```

---

## 🐛 Known Issues

### Current
- None reported in version 1.1.0

### Version 1.0.0 (Fixed in 1.1.0)
- ❌ Contract Usage Report SQL compilation error (`CAPACITY_TYPE_NAME` column)

---

## 📞 Support & Feedback

### Reporting Issues
Please include:
1. Version number
2. Error message or screenshot
3. Steps to reproduce
4. Expected vs actual behavior

### Contributing
Contributions are welcome! Please:
1. Review `TESTING_GUIDE.md`
2. Test changes thoroughly
3. Document in CHANGELOG.md
4. Update relevant documentation

---

## 📜 Version History

| Version | Date | Description | Status |
|---------|------|-------------|--------|
| 1.1.0 | 2025-10-11 | Bug fix: Contract Usage Report | ✅ Current |
| 1.0.0 | 2025-10-08 | Initial release | 📦 Stable |

---

**Last Updated:** October 11, 2025

