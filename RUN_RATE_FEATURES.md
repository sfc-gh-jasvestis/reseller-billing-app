# ⚡ Run Rate Analysis Features

## Overview

The dashboard now includes comprehensive **Consumption Run Rate Analysis** to help you monitor and predict customer credit consumption patterns.

## What's New

### 🎯 New Tab: "Run Rate Analysis"

Located in the Advanced Analytics section, this tab provides real-time consumption run rate calculations and projections.

## Key Features

### 1. Overall Run Rate Metrics

**Four key metrics displayed:**
- **Daily Run Rate** - Average credits consumed per day
- **Weekly Projection** - Projected consumption for next 7 days
- **Monthly Projection** - Projected consumption for next 30 days
- **Days Until Depletion** - Estimated days until balance reaches zero

### 2. Customer Run Rate Comparison

**Comprehensive table showing per-customer:**
- Daily consumption rate (credits and cost)
- Monthly cost projection
- Current balance
- Days until balance depletion
- Color-coded urgency indicators:
  - 🔴 Critical (<30 days)
  - 🟡 Warning (30-60 days)
  - 🟢 Healthy (>60 days)

### 3. Visual Analytics

**Two interactive charts:**
- **Top 10 Customers by Daily Run Rate** - Bar chart showing highest consumers
- **Days Until Balance Depletion** - Color-coded urgency visualization

### 4. Configurable Run Rate Period

**Dropdown selector with options:**
- 3 days - Most recent short-term trend
- 7 days - **Default** - Weekly trend
- 14 days - Bi-weekly trend
- 30 days - Monthly trend

### 5. Export Functionality

**Download run rate analysis as CSV** including:
- All customer run rate metrics
- Daily and monthly projections
- Balance and depletion calculations

## How It Works

### Run Rate Calculation

```
Daily Run Rate = Total Credits Used / Number of Days
```

**Example:**
- Last 7 days: 1,400 credits consumed
- Daily Run Rate: 1,400 ÷ 7 = **200 credits/day**
- Monthly Projection: 200 × 30 = **6,000 credits/month**

### Days to Depletion Calculation

```
Days Until Depletion = Current Balance / Daily Run Rate (Cost)
```

**Example:**
- Current Balance: $10,000
- Daily Run Rate: $150/day
- Days Until Depletion: 10,000 ÷ 150 = **66.7 days**

## Use Cases

### 1. Proactive Customer Management
- Identify customers with high burn rates
- Contact customers before they run out of credits
- Plan capacity expansions based on trends

### 2. Revenue Forecasting
- Project monthly revenue based on consumption trends
- Identify growing vs declining accounts
- Plan sales targets based on run rates

### 3. Budget Planning
- Calculate when customers will need to purchase more credits
- Forecast infrastructure costs based on usage patterns
- Plan for seasonal variations

### 4. Risk Management
- Identify customers at risk of service interruption
- Monitor customers approaching balance depletion
- Flag unusually high consumption for investigation

## Example Workflow

### Scenario: Customer Approaching Depletion

1. **Open Dashboard** → Navigate to "Run Rate Analysis" tab
2. **Review Metrics** → See "Days Until Depletion" showing 25 days
3. **Check Table** → Find customer with 🔴 Critical status
4. **Export Data** → Download CSV for detailed analysis
5. **Take Action** → Contact customer to discuss renewal/expansion

## Tips & Best Practices

### Choosing Run Rate Period

- **3 days** - Use when you need to detect sudden changes
- **7 days** - Best for typical week-over-week analysis
- **14 days** - Smooths out weekly variations
- **30 days** - Good for long-term trending (includes full month cycles)

### Interpreting Days to Depletion

- **< 30 days (🔴)** - Urgent action required
- **30-60 days (🟡)** - Plan outreach/renewal
- **> 60 days (🟢)** - Healthy, monitor regularly

### Combined with Other Features

**Best used alongside:**
- **Trends Tab** - See if consumption is accelerating
- **Balance Analysis** - Understand balance composition
- **Alerts** - Get notifications for high consumption

## Data Requirements

**Minimum data needed:**
- At least 3 days of usage data in selected period
- Balance data (optional, but required for depletion calculations)

**Recommendations:**
- Use with 30+ days of historical data for context
- Include balance data for complete analysis
- Filter by customer for detailed individual analysis

## Technical Details

### Functions Added

1. **`calculate_run_rate_by_customer()`**
   - Calculates per-customer run rates
   - Parameters: usage_df, balance_df, run_rate_days
   - Returns: DataFrame with run rate metrics

2. **`calculate_overall_run_rate()`**
   - Calculates aggregate run rate across all customers
   - Parameters: usage_df, balance_df, run_rate_days
   - Returns: Dictionary with overall metrics

### Calculations Include

- Daily credit consumption rate
- Daily cost consumption rate
- Weekly projections (× 7)
- Monthly projections (× 30)
- Balance depletion timeline
- Urgency categorization

## Future Enhancements

**Potential additions:**
- Run rate trend (increasing/decreasing)
- Anomaly detection (unusual consumption spikes)
- Email alerts for critical depletion timelines
- Historical run rate comparison
- Seasonal adjustment factors
- Budget vs actual consumption tracking

## FAQ

**Q: Why does my run rate show N/A for days to depletion?**  
A: This happens when balance data is not available or balance is zero.

**Q: Can I filter run rate by specific customer?**  
A: Yes! Use the customer filter in the sidebar before viewing the Run Rate Analysis tab.

**Q: How often is the run rate updated?**  
A: Run rates are calculated on-demand based on the data in your selected date range and refresh with the dashboard (every hour by default).

**Q: What if I have less than 7 days of data?**  
A: Select a shorter run rate period (3 days) or extend your date range to include more historical data.

**Q: Can I export the run rate analysis?**  
A: Yes! Click "Download Run Rate Analysis" button at the bottom of the Run Rate Analysis tab.

---

## Summary

The Run Rate Analysis feature provides powerful insights into consumption patterns, helping you:
- ✅ Predict future consumption
- ✅ Identify at-risk customers
- ✅ Plan capacity and budgets
- ✅ Take proactive action before issues arise

**Location:** Dashboard → Advanced Analytics → ⚡ Run Rate Analysis Tab

**Access:** Available to all dashboard users with appropriate permissions

---

*For deployment instructions, see `DEPLOYMENT_GUIDE.md`*  
*For general information, see `README.md`*
