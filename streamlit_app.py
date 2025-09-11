import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURATION SETTINGS (embedded for Streamlit in Snowflake compatibility)
# =============================================================================

# Application settings
APP_TITLE = "Snowflake Credit Usage Dashboard"
APP_ICON = "❄️"
DEFAULT_DATE_RANGE_DAYS = 30

# Database settings
BILLING_SCHEMA = "SNOWFLAKE.BILLING_USAGE"
CACHE_TTL_SECONDS = 3600  # 1 hour

# View names
VIEWS = {
    "USAGE": "USAGE_IN_CURRENCY_DAILY",
    "BALANCE": "REMAINING_BALANCE_DAILY", 
    "CONTRACT": "CONTRACT_ITEMS",
    "RATES": "RATE_SHEET_DAILY"
}

# Chart configuration
CHART_HEIGHT = 400
CHART_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "warning": "#d62728",
    "info": "#9467bd"
}

# Usage type mappings for better display
USAGE_TYPE_DISPLAY = {
    "compute": "💻 Compute",
    "storage": "💾 Storage", 
    "data transfer": "🌐 Data Transfer",
    "cloud services": "☁️ Cloud Services",
    "materialized views": "📊 Materialized Views",
    "snowpipe": "🚰 Snowpipe",
    "serverless tasks": "⚡ Serverless Tasks",
    "automatic clustering": "🔄 Auto Clustering"
}

# Balance source display names
BALANCE_SOURCE_DISPLAY = {
    "capacity": "📦 Capacity",
    "rollover": "🔄 Rollover", 
    "free usage": "🎁 Free Usage",
    "overage": "⚠️ Overage",
    "rebate": "💰 Rebate"
}

# Export file name templates
EXPORT_TEMPLATES = {
    "usage": "usage_data_{start_date}_{end_date}.csv",
    "balance": "balance_data_{start_date}_{end_date}.csv", 
    "contract": "contract_data.csv"
}

# UI Messages
MESSAGES = {
    "no_data": "No data found for the selected criteria.",
    "loading": "Loading data...",
    "connection_error": "Unable to connect to Snowflake. Please check your connection.",
    "permission_error": "Access denied. Please check your permissions for the BILLING_USAGE schema.",
    "data_refresh": "Data refreshed every hour. For the most current information, please refresh the page."
}

# Query configurations
QUERY_LIMITS = {
    "max_rows": 100000,
    "timeout_seconds": 300
}

# Feature flags
FEATURES = {
    "export_enabled": True,
    "advanced_filters": True,
    "real_time_refresh": False,
    "email_reports": False
}

# =============================================================================
# UTILITY FUNCTIONS (embedded for Streamlit in Snowflake compatibility)
# =============================================================================

def format_currency(amount, currency="USD"):
    """Format currency with proper symbols and formatting"""
    try:
        if pd.isna(amount) or amount == 0:
            return f"0.00 {currency}"
        
        # Format with commas and 2 decimal places
        formatted = f"{amount:,.2f}"
        
        # Add currency symbol based on currency code
        currency_symbols = {
            "USD": "$",
            "EUR": "€", 
            "GBP": "£",
            "JPY": "¥"
        }
        
        symbol = currency_symbols.get(currency, currency)
        return f"{symbol}{formatted}" if symbol != currency else f"{formatted} {currency}"
        
    except Exception:
        return f"0.00 {currency}"

def format_credits(credits):
    """Format credit values with proper number formatting"""
    try:
        if pd.isna(credits) or credits == 0:
            return "0.00"
        
        if credits >= 1000000:
            return f"{credits/1000000:.2f}M"
        elif credits >= 1000:
            return f"{credits/1000:.2f}K"
        else:
            return f"{credits:,.2f}"
            
    except Exception:
        return "0.00"

def get_date_range_options():
    """Get predefined date range options"""
    today = datetime.now().date()
    
    return {
        "Last 7 days": (today - timedelta(days=7), today),
        "Last 30 days": (today - timedelta(days=30), today),
        "Last 90 days": (today - timedelta(days=90), today),
        "Current Month": (today.replace(day=1), today),
        "Last Month": get_last_month_range(),
        "Custom": None
    }

def get_last_month_range():
    """Get date range for last month"""
    today = datetime.now().date()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    
    return (first_day_last_month, last_day_last_month)

def validate_date_range(start_date, end_date):
    """Validate date range inputs"""
    if start_date > end_date:
        st.error("Start date must be before end date.")
        return False
    
    if (end_date - start_date).days > 365:
        st.warning("Date range is longer than 1 year. This may result in slower performance.")
    
    return True

def clean_usage_data(df):
    """Clean and prepare usage data"""
    if df.empty:
        return df
    
    # Convert date columns
    date_columns = ['USAGE_DATE']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date
    
    # Fill null values
    numeric_columns = ['CREDITS_USED', 'USAGE_IN_CURRENCY']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Clean string columns
    string_columns = ['USAGE_TYPE', 'BALANCE_SOURCE']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown').str.strip()
    
    return df

def clean_balance_data(df):
    """Clean and prepare balance data"""
    if df.empty:
        return df
    
    # Convert date columns
    if 'BALANCE_DATE' in df.columns:
        df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE']).dt.date
    
    # Fill null values for balance columns
    balance_columns = ['FREE_USAGE_BALANCE', 'CAPACITY_BALANCE', 
                      'ON_DEMAND_CONSUMPTION_BALANCE', 'ROLLOVER_BALANCE']
    for col in balance_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Calculate total balance
    df['TOTAL_BALANCE'] = (df.get('FREE_USAGE_BALANCE', 0) + 
                          df.get('CAPACITY_BALANCE', 0) + 
                          df.get('ROLLOVER_BALANCE', 0))
    
    return df

def get_usage_summary(df):
    """Generate usage summary statistics"""
    if df.empty:
        return {}
    
    summary = {
        'total_credits': df['CREDITS_USED'].sum(),
        'total_cost': df['USAGE_IN_CURRENCY'].sum(),
        'unique_customers': df['SOLD_TO_CUSTOMER_NAME'].nunique(),
        'unique_accounts': df['ACCOUNT_NAME'].nunique() if 'ACCOUNT_NAME' in df.columns else 0,
        'date_range': {
            'start': df['USAGE_DATE'].min(),
            'end': df['USAGE_DATE'].max()
        },
        'top_usage_types': df.groupby('USAGE_TYPE')['CREDITS_USED'].sum().sort_values(ascending=False).head(5).to_dict(),
        'avg_daily_credits': df.groupby('USAGE_DATE')['CREDITS_USED'].sum().mean()
    }
    
    return summary

def get_balance_summary(df):
    """Generate balance summary statistics"""
    if df.empty:
        return {}
    
    # Get latest balance for each customer
    latest_balances = df.loc[df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()]
    
    summary = {
        'total_free_usage': latest_balances['FREE_USAGE_BALANCE'].sum(),
        'total_capacity': latest_balances['CAPACITY_BALANCE'].sum(),
        'total_rollover': latest_balances['ROLLOVER_BALANCE'].sum(),
        'total_on_demand': latest_balances['ON_DEMAND_CONSUMPTION_BALANCE'].sum(),
        'customers_with_balance': (latest_balances['TOTAL_BALANCE'] > 0).sum(),
        'customers_on_demand': (latest_balances['ON_DEMAND_CONSUMPTION_BALANCE'] < 0).sum()
    }
    
    return summary

def get_usage_type_list(df):
    """Get unique list of usage types from dataframe"""
    if df.empty or 'USAGE_TYPE' not in df.columns:
        return []
    
    return sorted(df['USAGE_TYPE'].unique())

def export_to_csv(df, filename):
    """Export dataframe to CSV with proper formatting"""
    if df.empty:
        return None
    
    # Format numeric columns for export
    export_df = df.copy()
    
    # Round numeric columns
    numeric_cols = export_df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        if 'BALANCE' in col or 'USAGE' in col or 'AMOUNT' in col:
            export_df[col] = export_df[col].round(2)
    
    return export_df.to_csv(index=False)

def calculate_growth_rate(df, metric_column, date_column, periods=7):
    """Calculate growth rate over specified periods"""
    if df.empty or len(df) < periods * 2:
        return 0
    
    # Sort by date
    df_sorted = df.sort_values(date_column)
    
    # Get recent and previous period values
    recent_period = df_sorted.tail(periods)[metric_column].sum()
    previous_period = df_sorted.iloc[-2*periods:-periods][metric_column].sum()
    
    if previous_period == 0:
        return 0
    
    growth_rate = ((recent_period - previous_period) / previous_period) * 100
    return round(growth_rate, 2)

def get_top_customers_by_usage(df, top_n=5):
    """Get top N customers by total credit usage"""
    if df.empty:
        return pd.DataFrame()
    
    top_customers = (df.groupby('SOLD_TO_CUSTOMER_NAME')['CREDITS_USED']
                    .sum()
                    .sort_values(ascending=False)
                    .head(top_n)
                    .reset_index())
    
    return top_customers

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .alert-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: 0.25rem;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: 0.25rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stSelectbox > div > div {
        background-color: #ffffff;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_snowflake_session():
    """Get Snowflake session for Streamlit in Snowflake"""
    try:
        # Use Streamlit's built-in Snowflake connection for Streamlit in Snowflake
        session = st.connection('snowflake').session()
        # Test connection
        session.sql("SELECT CURRENT_USER()").collect()
        return session
    except Exception as e:
        st.error(f"❌ {MESSAGES['connection_error']}\nDetails: {str(e)}")
        return None

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_usage_data(_session, start_date, end_date, customer_filter=None, usage_type_filter=None):
    """Enhanced usage data loading with additional filters"""
    try:
        query = f"""
        SELECT 
            SOLD_TO_ORGANIZATION_NAME,
            SOLD_TO_CUSTOMER_NAME,
            SOLD_TO_CONTRACT_NUMBER,
            ACCOUNT_NAME,
            ACCOUNT_LOCATOR,
            REGION,
            SERVICE_LEVEL,
            USAGE_DATE,
            USAGE_TYPE,
            CURRENCY,
            USAGE as CREDITS_USED,
            USAGE_IN_CURRENCY,
            BALANCE_SOURCE
        FROM {BILLING_SCHEMA}.{VIEWS['USAGE']}
        WHERE USAGE_DATE BETWEEN '{start_date}' AND '{end_date}'
        """
        
        if customer_filter and customer_filter != "All Customers":
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
        
        if usage_type_filter:
            usage_types = "', '".join(usage_type_filter)
            query += f" AND USAGE_TYPE IN ('{usage_types}')"
            
        query += f" ORDER BY USAGE_DATE DESC, SOLD_TO_CUSTOMER_NAME LIMIT {QUERY_LIMITS['max_rows']}"
        
        df = _session.sql(query).to_pandas()
        return clean_usage_data(df)
        
    except Exception as e:
        st.error(f"❌ Error loading usage data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_balance_data(_session, start_date, end_date, customer_filter=None):
    """Enhanced balance data loading"""
    try:
        query = f"""
        SELECT 
            SOLD_TO_ORGANIZATION_NAME,
            SOLD_TO_CUSTOMER_NAME,
            SOLD_TO_CONTRACT_NUMBER,
            DATE as BALANCE_DATE,
            CURRENCY,
            FREE_USAGE_BALANCE,
            CAPACITY_BALANCE,
            ON_DEMAND_CONSUMPTION_BALANCE,
            ROLLOVER_BALANCE
        FROM {BILLING_SCHEMA}.{VIEWS['BALANCE']}
        WHERE DATE BETWEEN '{start_date}' AND '{end_date}'
        """
        
        if customer_filter and customer_filter != "All Customers":
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
            
        query += " ORDER BY DATE DESC, SOLD_TO_CUSTOMER_NAME"
        
        df = _session.sql(query).to_pandas()
        return clean_balance_data(df)
        
    except Exception as e:
        st.error(f"❌ Error loading balance data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_customer_list(_session):
    """Load available customers dynamically"""
    try:
        query = f"""
        SELECT DISTINCT SOLD_TO_CUSTOMER_NAME
        FROM {BILLING_SCHEMA}.{VIEWS['USAGE']}
        WHERE USAGE_DATE >= CURRENT_DATE - 90
        ORDER BY SOLD_TO_CUSTOMER_NAME
        """
        
        df = _session.sql(query).to_pandas()
        return ["All Customers"] + df['SOLD_TO_CUSTOMER_NAME'].tolist()
        
    except Exception as e:
        st.warning(f"⚠️ Could not load customer list: {str(e)}")
        return ["All Customers"]

def create_enhanced_trend_chart(df):
    """Create enhanced trend chart with multiple metrics"""
    if df.empty:
        return None
    
    # Prepare data
    daily_usage = df.groupby(['USAGE_DATE', 'USAGE_TYPE']).agg({
        'CREDITS_USED': 'sum',
        'USAGE_IN_CURRENCY': 'sum'
    }).reset_index()
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Credit Usage Trend', 'Cost Trend'),
        vertical_spacing=0.1,
        shared_xaxes=True
    )
    
    # Add credit usage lines
    usage_types = daily_usage['USAGE_TYPE'].unique()
    colors = px.colors.qualitative.Set3
    
    for i, usage_type in enumerate(usage_types):
        data = daily_usage[daily_usage['USAGE_TYPE'] == usage_type]
        display_name = USAGE_TYPE_DISPLAY.get(usage_type, usage_type)
        
        fig.add_trace(
            go.Scatter(
                x=data['USAGE_DATE'],
                y=data['CREDITS_USED'],
                name=f"{display_name} (Credits)",
                line=dict(color=colors[i % len(colors)]),
                mode='lines+markers'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['USAGE_DATE'],
                y=data['USAGE_IN_CURRENCY'],
                name=f"{display_name} (Cost)",
                line=dict(color=colors[i % len(colors)], dash='dash'),
                mode='lines+markers',
                showlegend=False
            ),
            row=2, col=1
        )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Credits", row=1, col=1)
    fig.update_yaxes(title_text="Cost", row=2, col=1)
    
    fig.update_layout(
        height=600,
        title="Usage and Cost Trends",
        hovermode='x unified'
    )
    
    return fig

def create_balance_waterfall_chart(df):
    """Create waterfall chart showing balance changes"""
    if df.empty:
        return None
    
    # Get the most recent balance data
    latest_data = df.loc[df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()]
    
    # Aggregate by balance type
    balance_types = ['FREE_USAGE_BALANCE', 'CAPACITY_BALANCE', 'ROLLOVER_BALANCE']
    values = [latest_data[col].sum() for col in balance_types]
    on_demand = abs(latest_data['ON_DEMAND_CONSUMPTION_BALANCE'].sum())
    
    fig = go.Figure(go.Waterfall(
        name="Balance Breakdown",
        orientation="v",
        measure=["absolute"] * len(balance_types) + ["total"],
        x=["Free Usage", "Capacity", "Rollover", "Total Available"],
        textposition="outside",
        text=[f"${val:,.0f}" for val in values + [sum(values)]],
        y=values + [sum(values)],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},
        totals={"marker": {"color": "blue"}}
    ))
    
    fig.update_layout(
        title="Current Balance Breakdown",
        showlegend=False,
        height=400
    )
    
    return fig

def create_usage_heatmap(df):
    """Create heatmap showing usage patterns"""
    if df.empty:
        return None
    
    # Prepare data for heatmap
    df['DAY_OF_WEEK'] = pd.to_datetime(df['USAGE_DATE']).dt.day_name()
    df['WEEK'] = pd.to_datetime(df['USAGE_DATE']).dt.isocalendar().week
    
    heatmap_data = df.groupby(['WEEK', 'DAY_OF_WEEK'])['CREDITS_USED'].sum().reset_index()
    
    # Pivot for heatmap
    heatmap_pivot = heatmap_data.pivot(index='WEEK', columns='DAY_OF_WEEK', values='CREDITS_USED').fillna(0)
    
    # Reorder columns to start with Monday
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(columns=day_order, fill_value=0)
    
    fig = px.imshow(
        heatmap_pivot,
        title="Usage Heatmap by Week and Day",
        color_continuous_scale="Blues",
        aspect="auto"
    )
    
    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Week Number",
        height=400
    )
    
    return fig

def show_alerts_and_insights(usage_df, balance_df):
    """Display intelligent alerts and insights"""
    st.subheader("🚨 Alerts & Insights")
    
    alerts = []
    
    if not usage_df.empty:
        # High usage alert
        total_credits = usage_df['CREDITS_USED'].sum()
        avg_daily = usage_df.groupby('USAGE_DATE')['CREDITS_USED'].sum().mean()
        
        if avg_daily > 1000:  # Configurable threshold
            alerts.append({
                'type': 'warning',
                'message': f"High daily credit usage detected: {avg_daily:,.0f} credits/day average"
            })
        
        # Usage growth alert
        growth_rate = calculate_growth_rate(usage_df, 'CREDITS_USED', 'USAGE_DATE')
        if growth_rate > 50:
            alerts.append({
                'type': 'warning',
                'message': f"Usage growth rate is high: {growth_rate}% over last week"
            })
        elif growth_rate < -20:
            alerts.append({
                'type': 'success',
                'message': f"Usage has decreased: {abs(growth_rate)}% reduction over last week"
            })
    
    if not balance_df.empty:
        # Low balance alert
        latest_balances = balance_df.loc[balance_df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()]
        low_balance_customers = latest_balances[latest_balances['TOTAL_BALANCE'] < 1000]
        
        if not low_balance_customers.empty:
            alerts.append({
                'type': 'warning',
                'message': f"{len(low_balance_customers)} customer(s) have low balance (<$1,000)"
            })
        
        # On-demand usage alert
        on_demand_customers = latest_balances[latest_balances['ON_DEMAND_CONSUMPTION_BALANCE'] < -500]
        if not on_demand_customers.empty:
            alerts.append({
                'type': 'warning',
                'message': f"{len(on_demand_customers)} customer(s) have significant on-demand charges"
            })
    
    # Display alerts
    if alerts:
        for alert in alerts:
            alert_class = f"alert-{alert['type']}"
            st.markdown(f'<div class="{alert_class}">{alert["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-success">✅ No alerts detected. All metrics are within normal ranges.</div>', unsafe_allow_html=True)

def display_enhanced_metrics(usage_df, balance_df):
    """Display enhanced metrics with better formatting"""
    if usage_df.empty:
        return
    
    summary = get_usage_summary(usage_df)
    currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        growth_rate = calculate_growth_rate(usage_df, 'CREDITS_USED', 'USAGE_DATE')
        st.metric(
            "Total Credits Used",
            format_credits(summary['total_credits']),
            delta=f"{growth_rate:+.1f}% vs last week" if growth_rate != 0 else None
        )
    
    with col2:
        cost_growth = calculate_growth_rate(usage_df, 'USAGE_IN_CURRENCY', 'USAGE_DATE')
        st.metric(
            "Total Cost",
            format_currency(summary['total_cost'], currency),
            delta=f"{cost_growth:+.1f}% vs last week" if cost_growth != 0 else None
        )
    
    with col3:
        st.metric(
            "Active Customers",
            summary['unique_customers'],
            delta=None
        )
    
    with col4:
        st.metric(
            "Avg Daily Credits",
            format_credits(summary['avg_daily_credits']),
            delta=None
        )
    
    # Additional balance metrics if available
    if not balance_df.empty:
        balance_summary = get_balance_summary(balance_df)
        
        st.markdown("### 💰 Balance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Available Balance", format_currency(
                balance_summary['total_free_usage'] + 
                balance_summary['total_capacity'] + 
                balance_summary['total_rollover'], currency
            ))
        
        with col2:
            st.metric("Free Usage Balance", format_currency(balance_summary['total_free_usage'], currency))
        
        with col3:
            st.metric("Capacity Balance", format_currency(balance_summary['total_capacity'], currency))
        
        with col4:
            st.metric("On-Demand Charges", format_currency(abs(balance_summary['total_on_demand']), currency))

def main():
    # Header with enhanced styling
    st.markdown(f'<h1 class="main-header">{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time credit consumption monitoring for Snowflake reseller customers")
    st.markdown("---")
    
    # Get Snowflake session
    session = get_snowflake_session()
    if not session:
        st.stop()
    
    # Sidebar with enhanced filters
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Quick date range selector
    date_range_options = get_date_range_options()
    selected_range = st.sidebar.selectbox(
        "📅 Quick Date Range",
        options=list(date_range_options.keys()),
        index=1  # Default to "Last 30 days"
    )
    
    if selected_range == "Custom":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=DEFAULT_DATE_RANGE_DAYS),
                max_value=datetime.now().date()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date(),
                max_value=datetime.now().date()
            )
    else:
        start_date, end_date = date_range_options[selected_range]
    
    # Validate date range
    if not validate_date_range(start_date, end_date):
        st.stop()
    
    # Load customer list dynamically
    with st.spinner("Loading customers..."):
        customer_options = load_customer_list(session)
    
    # Customer filter
    customer_filter = st.sidebar.selectbox(
        "👥 Select Customer",
        options=customer_options,
        index=0
    )
    
    # Advanced filters
    if FEATURES['advanced_filters']:
        with st.sidebar.expander("🔧 Advanced Filters"):
            # Load usage types for filter
            with st.spinner("Loading usage types..."):
                temp_df = load_usage_data(session, start_date, end_date)
                usage_types = get_usage_type_list(temp_df)
            
            usage_type_filter = st.multiselect(
                "Usage Types",
                options=usage_types,
                default=usage_types if len(usage_types) <= 5 else usage_types[:5]
            )
    else:
        usage_type_filter = None
    
    # Load data with enhanced loading indicator
    with st.spinner(MESSAGES['loading']):
        progress_bar = st.progress(0)
        
        usage_df = load_usage_data(session, start_date, end_date, customer_filter, usage_type_filter)
        progress_bar.progress(33)
        
        balance_df = load_balance_data(session, start_date, end_date, customer_filter)
        progress_bar.progress(66)
        
        progress_bar.progress(100)
        progress_bar.empty()
    
    # Check for data
    if usage_df.empty:
        st.warning(MESSAGES['no_data'])
        st.info("💡 Try adjusting your filters or date range to find available data.")
        return
    
    # Show alerts and insights
    show_alerts_and_insights(usage_df, balance_df)
    
    # Enhanced metrics display
    st.subheader("📊 Key Performance Indicators")
    display_enhanced_metrics(usage_df, balance_df)
    
    # Enhanced visualizations
    st.subheader("📈 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📊 Trends", "🎯 Usage Patterns", "💰 Balance Analysis"])
    
    with tab1:
        trend_chart = create_enhanced_trend_chart(usage_df)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
        
        # Usage heatmap
        if len(usage_df) > 7:  # Only show if we have enough data
            heatmap_chart = create_usage_heatmap(usage_df)
            if heatmap_chart:
                st.plotly_chart(heatmap_chart, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Usage breakdown pie chart
            usage_by_type = usage_df.groupby('USAGE_TYPE')['CREDITS_USED'].sum().reset_index()
            fig_pie = px.pie(
                usage_by_type,
                values='CREDITS_USED',
                names='USAGE_TYPE',
                title='Credit Usage Distribution by Type'
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Top customers chart
            top_customers = get_top_customers_by_usage(usage_df)
            if not top_customers.empty:
                fig_customers = px.bar(
                    top_customers,
                    x='CREDITS_USED',
                    y='SOLD_TO_CUSTOMER_NAME',
                    orientation='h',
                    title='Top Customers by Credit Usage'
                )
                st.plotly_chart(fig_customers, use_container_width=True)
    
    with tab3:
        if not balance_df.empty:
            # Balance waterfall chart
            waterfall_chart = create_balance_waterfall_chart(balance_df)
            if waterfall_chart:
                st.plotly_chart(waterfall_chart, use_container_width=True)
            
            # Balance trend over time
            balance_trend = balance_df.groupby('BALANCE_DATE').agg({
                'FREE_USAGE_BALANCE': 'sum',
                'CAPACITY_BALANCE': 'sum',
                'ROLLOVER_BALANCE': 'sum',
                'TOTAL_BALANCE': 'sum'
            }).reset_index()
            
            fig_balance_trend = px.line(
                balance_trend,
                x='BALANCE_DATE',
                y=['FREE_USAGE_BALANCE', 'CAPACITY_BALANCE', 'ROLLOVER_BALANCE'],
                title='Balance Trends Over Time'
            )
            st.plotly_chart(fig_balance_trend, use_container_width=True)
        else:
            st.info("No balance data available for the selected period.")
    
    # Data tables with enhanced features
    st.subheader("📋 Detailed Data")
    
    # Usage details with better formatting
    with st.expander("💻 Usage Details", expanded=False):
        if not usage_df.empty:
            # Add formatted columns for display
            display_df = usage_df.copy()
            display_df['CREDITS_FORMATTED'] = display_df['CREDITS_USED'].apply(format_credits)
            display_df['COST_FORMATTED'] = display_df.apply(
                lambda row: format_currency(row['USAGE_IN_CURRENCY'], row['CURRENCY']), axis=1
            )
            
            st.dataframe(
                display_df.sort_values('USAGE_DATE', ascending=False),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No usage data available.")
    
    # Export functionality
    if FEATURES['export_enabled']:
        st.subheader("📥 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not usage_df.empty:
                csv_data = export_to_csv(usage_df, "usage_data")
                if csv_data:
                    st.download_button(
                        label="📊 Download Usage Data",
                        data=csv_data,
                        file_name=EXPORT_TEMPLATES['usage'].format(
                            start_date=start_date, end_date=end_date
                        ),
                        mime="text/csv"
                    )
        
        with col2:
            if not balance_df.empty:
                csv_data = export_to_csv(balance_df, "balance_data")
                if csv_data:
                    st.download_button(
                        label="💰 Download Balance Data",
                        data=csv_data,
                        file_name=EXPORT_TEMPLATES['balance'].format(
                            start_date=start_date, end_date=end_date
                        ),
                        mime="text/csv"
                    )
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"*{MESSAGES['data_refresh']}*")
    
    with col2:
        st.markdown(f"*Data Range: {start_date} to {end_date}*")
    
    with col3:
        if not usage_df.empty:
            st.markdown(f"*Total Records: {len(usage_df):,}*")

if __name__ == "__main__":
    main() 