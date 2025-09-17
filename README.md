# Snowflake Credit Usage Dashboard for Resellers

A comprehensive **Streamlit in Snowflake** application that enables Snowflake reseller customers to view their credit consumption, billing usage, and account balances using Snowflake's BILLING schema.

## 🌟 Features

### 📊 Key Metrics Dashboard
- **Total Credits Used**: Aggregate credit consumption across all accounts
- **Total Cost**: Monetary value of usage in contract currency
- **Active Customers**: Number of customers with usage in the selected period
- **Average Daily Credits**: Daily credit consumption trends

### 📈 Interactive Visualizations
- **Usage Trend Chart**: Daily credit usage by usage type (compute, storage, data transfer, etc.)
- **Usage Breakdown**: Pie chart showing distribution of credits by usage type
- **Balance Overview**: Stacked bar chart showing current balances by customer

### 🔍 Data Views
- **Usage Details**: Comprehensive view of daily usage by account and service
- **Balance Details**: Current balance information including free usage, capacity, and rollover
- **Contract Information**: Contract terms and amounts for each customer

### 📥 Export Capabilities
- Download usage data as CSV
- Download balance data as CSV  
- Download contract information as CSV

### 🎛️ Filtering Options
- Date range selection (last 30 days by default)
- Customer-specific filtering
- Real-time data refresh capabilities

## 🛠️ Technical Implementation

### Data Sources
The application leverages Snowflake's BILLING schema views:

1. **PARTNER_USAGE_IN_CURRENCY_DAILY**: Daily credit and currency usage
2. **PARTNER_REMAINING_BALANCE_DAILY**: Daily balance information
3. **PARTNER_CONTRACT_ITEMS**: Contract terms and capacity information
4. **PARTNER_RATE_SHEET_DAILY**: Effective rates for usage calculation

### Key Components

#### Database Queries
```sql
-- Example usage query
SELECT 
    SOLD_TO_ORGANIZATION_NAME,
    SOLD_TO_CUSTOMER_NAME,
    ACCOUNT_NAME,
    USAGE_DATE,
    USAGE_TYPE,
    USAGE as CREDITS_USED,
    USAGE_IN_CURRENCY,
    BALANCE_SOURCE
FROM SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY
WHERE USAGE_DATE BETWEEN '2024-01-01' AND '2024-01-31'
ORDER BY USAGE_DATE DESC;
```

#### Caching Strategy
- Data caching for 1 hour using `@st.cache_data(ttl=3600)`
- Reduces query load on Snowflake
- Improves app performance

## 🚀 Deployment

### Prerequisites
- Snowflake account with **Streamlit in Snowflake** enabled
- Access to BILLING schema (available for resellers and distributors)
- ACCOUNTADMIN role or appropriate permissions

### Installation Steps

1. **Upload to Snowflake**:
   ```sql
   -- Create Streamlit app in Snowflake
   CREATE STREAMLIT APP billing_dashboard
   ROOT_LOCATION = '@your_stage/billing_app'
   MAIN_FILE = 'streamlit_app.py'
   QUERY_WAREHOUSE = 'your_warehouse';
   ```

2. **Grant Permissions**:
   ```sql
   -- Grant access to BILLING schema
   GRANT USAGE ON DATABASE SNOWFLAKE TO ROLE your_role;
   GRANT USAGE ON SCHEMA SNOWFLAKE.BILLING TO ROLE your_role;
   GRANT SELECT ON ALL VIEWS IN SCHEMA SNOWFLAKE.BILLING TO ROLE your_role;
   ```

3. **Run the Application**:
   ```sql
   -- Start the Streamlit app
   ALTER STREAMLIT billing_dashboard SET ROOT_LOCATION = '@your_stage/billing_app';
   ```

### File Structure
```
reseller-billing/
├── streamlit_app.py          # Main application file (enhanced version)
├── requirements.txt          # Python dependencies
├── README.md                # Documentation
├── DEPLOYMENT_GUIDE.md      # Step-by-step deployment instructions
├── deploy.sql               # Comprehensive Snowflake deployment script
├── config/
│   ├── __init__.py          # Package initialization
│   └── app_config.py        # Configuration settings
└── utils/
    ├── __init__.py          # Package initialization
    └── data_utils.py        # Data processing utilities
```

## 📊 Usage Types Tracked

The application tracks various Snowflake usage types:

- **compute**: Virtual warehouse credit usage
- **storage**: Data storage costs
- **data transfer**: Network transfer charges
- **cloud services**: Cloud services credit usage
- **materialized views**: Materialized view maintenance
- **snowpipe**: Snowpipe ingestion costs
- **serverless tasks**: Task execution costs
- **automatic clustering**: Table clustering costs

## 🔐 Security & Permissions

### Required Permissions
- `USAGE` on SNOWFLAKE database
- `USAGE` on SNOWFLAKE.BILLING_USAGE schema
- `SELECT` on all views in BILLING_USAGE schema

### Data Privacy
- All data queries are scoped to the reseller's organization
- Customer data is filtered based on contracts
- No data is stored outside of Snowflake

## 🎨 Customization

### Adding New Visualizations
```python
def create_custom_chart(df):
    """Create custom visualization"""
    fig = px.bar(df, x='USAGE_DATE', y='CREDITS_USED')
    return fig
```

### Modifying Filters
```python
# Add new filter in sidebar
region_filter = st.sidebar.selectbox(
    "Select Region",
    options=usage_df['REGION'].unique()
)
```

### Custom Styling
The app includes custom CSS for improved UI/UX:
- Professional color scheme
- Responsive layout
- Clean typography
- Interactive elements

## 📱 Mobile Responsiveness

The dashboard is optimized for various screen sizes:
- Desktop computers
- Tablets
- Mobile devices
- Large displays

## 🔄 Data Refresh

- **Automatic**: Data cached for 1 hour
- **Manual**: Refresh by reloading the page
- **Latency**: Up to 24-72 hours from actual usage

## 🆘 Troubleshooting

### Common Issues

1. **Caching Errors**:
   - **UnserializableReturnValueError**: If you see `Cannot serialize the return value (of type snowflake.snowpark.session.Session)`, ensure you're using `@st.cache_resource` for database connections, not `@st.cache_data`
   - **UnhashableParamError**: If you see `Cannot hash argument 'session'`, add a leading underscore to the session parameter: `def function(_session):`
   - **Solution**: Use `@st.cache_resource` for Snowflake sessions and `@st.cache_data` for serializable data like pandas DataFrames

2. **Connection Errors**:
   - Ensure you're running in **Streamlit in Snowflake** environment
   - Verify warehouse is running and accessible
   - Check that `st.connection('snowflake')` is available (Streamlit in Snowflake feature)

3. **Permission Denied**:
   - Ensure ACCOUNTADMIN role or proper grants
   - Verify access to BILLING_USAGE schema

4. **No Data Available**:
   - Check date range selection
   - Verify customer has usage in period
   - Confirm contract is active

### Streamlit Caching Guidelines

```python
# ✅ Correct: Use st.cache_resource for Streamlit in Snowflake connections
@st.cache_resource
def get_snowflake_session():
    return st.connection('snowflake').session()

# ✅ Correct: Use st.cache_data for serializable data
@st.cache_data
def load_data():
    return pd.DataFrame(data)

# ✅ Correct: Add underscore to unhashable parameters
@st.cache_data
def load_from_db(_session, query_params):
    return _session.sql(query).to_pandas()
```

### Error Handling
The application includes comprehensive error handling:
- Database connection failures
- Query execution errors
- Data processing issues
- UI/UX error messages

## 📞 Support

For support with this application:
1. Check Snowflake documentation for BILLING_USAGE schema
2. Verify permissions and access rights
3. Review application logs for errors
4. Contact your Snowflake administrator

## 🔗 References

- [Snowflake BILLING_USAGE Documentation](https://docs.snowflake.com/en/LIMITEDACCESS/billing-usage-resellers)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)

---

*Built with ❄️ for Snowflake reseller partners* 