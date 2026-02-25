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
BILLING_SCHEMA = "SNOWFLAKE.BILLING"
CACHE_TTL_SECONDS = 3600  # 1 hour

# View names
VIEWS = {
    "USAGE": "PARTNER_USAGE_IN_CURRENCY_DAILY",
    "BALANCE": "PARTNER_REMAINING_BALANCE_DAILY", 
    "CONTRACT": "PARTNER_CONTRACT_ITEMS",
    "RATES": "PARTNER_RATE_SHEET_DAILY"
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
    # Core services
    "compute": "💻 Compute",
    "storage": "💾 Storage",
    "data transfer": "🌐 Data Transfer",
    "cloud services": "☁️ Cloud Services",
    # Data pipelines & streaming
    "snowpipe": "🚰 Snowpipe",
    "streams": "🌊 Streams",
    "serverless tasks": "⚡ Tasks",
    "dynamic tables": "🔄 Dynamic Tables",
    # Apps & developer platform
    "snowpark": "🐍 Snowpark",
    "streamlit": "📱 Streamlit",
    # Optimization
    "automatic clustering": "♻️ Auto Clustering",
    "materialized views": "📊 Materialized Views",
    "search optimization": "🔍 Search Optimization",
    # AI / Cortex suite
    "cortex": "🤖 Cortex AI Functions",
    "cortex analyst": "💬 Cortex Analyst",
    "cortex search": "🔎 Cortex Search",
    "cortex code": "💡 Cortex Code",
    "snowflake intelligence": "✨ Snowflake Intelligence",
    "ml functions": "🧠 ML Functions",
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
    "permission_error": "Access denied. Please check your permissions for the BILLING schema.",
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
    "advanced_filters": False,
    "real_time_refresh": False,
    "email_reports": False
}

# Demo mode flag - set to True to use sample data when BILLING schema is unavailable
USE_DEMO_DATA = False

# Demo data configuration - 5 customers with varying usage patterns
DEMO_CUSTOMERS = [
    {"name": "Acme Corporation", "org": "Acme Inc", "contract": "ACME-2024-001", "tier": "enterprise", "usage_multiplier": 1.5, "industry": "manufacturing"},
    {"name": "TechStart Labs", "org": "TechStart Holdings", "contract": "TSL-2024-002", "tier": "standard", "usage_multiplier": 0.6, "industry": "technology"},
    {"name": "Global Analytics Co", "org": "Global Analytics", "contract": "GAC-2024-003", "tier": "enterprise", "usage_multiplier": 2.2, "industry": "analytics"},
    {"name": "DataDriven Solutions", "org": "DataDriven Group", "contract": "DDS-2024-004", "tier": "business_critical", "usage_multiplier": 3.0, "industry": "financial services"},
    {"name": "SmallBiz Insights", "org": "SmallBiz LLC", "contract": "SBI-2024-005", "tier": "standard", "usage_multiplier": 0.3, "industry": "retail"},
]

# Each customer can have one or more Snowflake accounts.
# Each account has a unique ACCOUNT_NAME, ACCOUNT_LOCATOR, and a fixed REGION.
# This mirrors the real SNOWFLAKE.BILLING schema where every row is tied to a specific account.
DEMO_ACCOUNTS = {
    "Acme Corporation": [
        {"account_name": "acme_corp_prod",  "account_locator": "ACM38291", "region": "AWS_US_EAST_1"},
        {"account_name": "acme_corp_eu",    "account_locator": "ACM74512", "region": "AWS_EU_WEST_1"},
    ],
    "TechStart Labs": [
        {"account_name": "techstart_main",  "account_locator": "TSL20483", "region": "AWS_US_WEST_2"},
    ],
    "Global Analytics Co": [
        {"account_name": "globalanalytics_us",    "account_locator": "GAC51729", "region": "AWS_US_EAST_1"},
        {"account_name": "globalanalytics_azure", "account_locator": "GAC83064", "region": "AZURE_EASTUS2"},
    ],
    "DataDriven Solutions": [
        {"account_name": "datadriven_prod", "account_locator": "DDS94271", "region": "AWS_US_EAST_1"},
        {"account_name": "datadriven_dev",  "account_locator": "DDS38156", "region": "AWS_US_WEST_2"},
        {"account_name": "datadriven_eu",   "account_locator": "DDS62904", "region": "AWS_EU_WEST_1"},
    ],
    "SmallBiz Insights": [
        {"account_name": "smallbiz_main",   "account_locator": "SBI15738", "region": "AWS_US_EAST_1"},
    ],
}

# Single source of truth for demo contract dates and amounts.
# Both generate_demo_contract_data and generate_demo_balance_data read from here
# so the two datasets are always aligned.
DEMO_CONTRACT_INFO = {
    # Mid-contract, healthy pace
    'Acme Corporation':     {'amount': 150000, 'days_ago': 180, 'duration': 365},
    # Early stage, still ramping up
    'TechStart Labs':       {'amount':  45000, 'days_ago':  90, 'duration': 365},
    # Near contract end — renewal conversation needed
    'Global Analytics Co':  {'amount': 300000, 'days_ago': 270, 'duration': 365},
    # Brand new — lots of runway
    'DataDriven Solutions': {'amount': 600000, 'days_ago':  45, 'duration': 365},
    # Almost expired AND nearly depleted — double urgency
    'SmallBiz Insights':    {'amount':  15000, 'days_ago': 330, 'duration': 365},
}

# Generic upsell use cases per feature — shown in the Feature Adoption tab
FEATURE_USECASES = {
    "cortex":               "Build AI-powered apps, summarize documents, classify data, and generate content — no ML expertise or external tools needed",
    "ml functions":         "Built-in forecasting and anomaly detection — spot trends and outliers in any dataset without a data science team",
    "snowpark":             "Run Python, Java, or Scala transformations and ML workloads natively inside Snowflake — no data movement, no Spark clusters",
    "search optimization":  "Dramatically speed up point-lookup queries on large tables — ideal for interactive apps, dashboards, and API backends",
    "snowpipe":             "Replace scheduled batch loads with continuous, automated data ingestion — data is always fresh when you need it",
    "streams":              "Track every INSERT, UPDATE, and DELETE on any table and build event-driven, incremental pipelines using Change Data Capture",
    "serverless tasks":     "One of Snowflake's most-adopted features — automate and orchestrate data pipelines on a schedule without managing any compute",
    "dynamic tables":       "Declare the result you want; Snowflake works out when and how to refresh it — the modern alternative to complex ETL pipelines",
    "automatic clustering": "Keep large tables fast as data grows without any manual tuning — queries stay performant automatically",
    "materialized views":   "Pre-compute and cache the results of expensive queries — near-instant load times for dashboards and repeated analytical workloads",
    "streamlit":            "Build and share interactive data apps and dashboards natively inside Snowflake — no external hosting, no data copies",
    "cortex analyst":       "Ask questions about your data in plain English and get SQL-backed answers instantly — self-service analytics for everyone",
    "cortex search":        "Add semantic search to any application — returns relevant results even when the exact keywords don't match",
    "cortex code":          "AI-assisted SQL and Python generation inside Snowflake — write, explain, and debug code faster",
    "snowflake intelligence": "Snowflake's unified AI layer — combine conversational analytics, intelligent search, and automated agents in one place",
}

# =============================================================================
# DEMO DATA GENERATION FUNCTIONS
# =============================================================================
import numpy as np
import random

def generate_demo_usage_data(start_date, end_date):
    """Generate realistic demo usage data for 5 customers"""
    random.seed(42)
    np.random.seed(42)

    # Feature sets per tier — higher tiers unlock AI/ML and advanced features
    TIER_FEATURES = {
        'standard': {
            'compute': 0.45, 'storage': 0.25, 'data transfer': 0.15, 'cloud services': 0.10,
            'serverless tasks': 0.05,
        },
        'business_critical': {
            'compute': 0.35, 'storage': 0.17, 'data transfer': 0.09, 'cloud services': 0.07,
            'snowpipe': 0.05, 'serverless tasks': 0.05, 'dynamic tables': 0.04,
            'snowpark': 0.05, 'streams': 0.03, 'search optimization': 0.02,
            'streamlit': 0.02, 'cortex': 0.03, 'cortex analyst': 0.03,
        },
        'enterprise': {
            'compute': 0.30, 'storage': 0.12, 'data transfer': 0.08, 'cloud services': 0.06,
            'snowpipe': 0.05, 'serverless tasks': 0.04, 'automatic clustering': 0.03,
            'dynamic tables': 0.04, 'streams': 0.03, 'snowpark': 0.05,
            'streamlit': 0.02, 'search optimization': 0.01,
            'cortex': 0.04, 'ml functions': 0.03,
            'cortex analyst': 0.03, 'cortex search': 0.02, 'cortex code': 0.02,
            'snowflake intelligence': 0.03,
        },
    }

    balance_sources = ['capacity', 'rollover']

    data = []
    date_range = pd.date_range(start=start_date, end=end_date)

    for customer in DEMO_CUSTOMERS:
        accounts = DEMO_ACCOUNTS.get(customer['name'], [
            {"account_name": customer['name'].replace(' ', '_').lower() + "_main",
             "account_locator": f"UNK{abs(hash(customer['name'])) % 100000:05d}",
             "region": "AWS_US_EAST_1"}
        ])
        # Split total usage across the customer's accounts (first account carries most load)
        account_weights = [0.6] + [0.4 / max(len(accounts) - 1, 1)] * (len(accounts) - 1) if len(accounts) > 1 else [1.0]
        base_daily_credits = 100 * customer['usage_multiplier']
        type_multipliers = TIER_FEATURES.get(customer['tier'], TIER_FEATURES['standard'])

        for date in date_range:
            day_factor = 0.4 if date.weekday() >= 5 else 1.0
            trend_factor = 1 + (date - date_range[0]).days * 0.002

            for acct, weight in zip(accounts, account_weights):
                random_factor = np.random.uniform(0.7, 1.3)
                for usage_type, multiplier in type_multipliers.items():
                    credits = base_daily_credits * weight * multiplier * day_factor * trend_factor * random_factor
                    credits = max(0, credits + np.random.normal(0, credits * 0.1))

                    if credits > 0.01:
                        cost = credits * 3.00  # $3 per credit
                        data.append({
                            'SOLD_TO_ORGANIZATION_NAME': customer['org'],
                            'SOLD_TO_CUSTOMER_NAME': customer['name'],
                            'SOLD_TO_CONTRACT_NUMBER': customer['contract'],
                            'ACCOUNT_NAME': acct['account_name'],
                            'ACCOUNT_LOCATOR': acct['account_locator'],
                            'REGION': acct['region'],
                            'SERVICE_LEVEL': customer['tier'],
                            'USAGE_DATE': date.date(),
                            'USAGE_TYPE': usage_type,
                            'CURRENCY': 'USD',
                            'CREDITS_USED': round(credits, 4),
                            'USAGE_IN_CURRENCY': round(cost, 2),
                            'BALANCE_SOURCE': random.choice(balance_sources)
                        })
    
    df = pd.DataFrame(data)
    df['USAGE_DATE'] = pd.to_datetime(df['USAGE_DATE']).dt.date
    return df

def generate_demo_balance_data(start_date, end_date):
    """Generate demo balance data whose remaining capacity aligns with contract data.

    Starting balance at start_date = contract_amount minus what was already consumed
    between the contract start (today-180d) and start_date, so Days Until Depletion
    and Days Until Overage are derived from the same underlying consumption rate.
    """
    random.seed(42)
    np.random.seed(42)

    # Rollover = 5 % of contract value, fully exhausted within the first 90 days
    ROLLOVER_PCT   = 0.05
    ROLLOVER_DAYS  = 90

    today = datetime.now().date()

    # Normalise start_date to a date object
    if hasattr(start_date, 'date'):
        bal_start = start_date.date()
    else:
        bal_start = start_date

    data = []
    date_range = pd.date_range(start=start_date, end=end_date)

    for customer in DEMO_CUSTOMERS:
        info            = DEMO_CONTRACT_INFO.get(customer['name'], {'amount': 50000, 'days_ago': 180, 'duration': 365})
        contract_amount = info['amount']
        contract_start  = today - timedelta(days=info['days_ago'])
        daily_burn      = 100 * customer['usage_multiplier'] * 3.00  # $3/credit

        # Days elapsed from this customer's contract start to the balance window start
        days_elapsed = max(0, (bal_start - contract_start).days)

        # Capacity remaining at bal_start
        capacity_bal = max(0.0, contract_amount - daily_burn * days_elapsed)

        # Rollover depletes linearly in the first ROLLOVER_DAYS of the contract;
        # after that it is zero.
        rollover_total = contract_amount * ROLLOVER_PCT
        rollover_bal   = max(0.0, rollover_total * (1.0 - days_elapsed / ROLLOVER_DAYS))

        # Free usage is consumed before rollover; assume exhausted by bal_start
        free_bal = 0.0

        for date in date_range:
            # Draw-down order: free → rollover → capacity
            remaining = daily_burn * np.random.uniform(0.8, 1.2)

            if free_bal > 0:
                consumed  = min(free_bal, remaining)
                free_bal -= consumed
                remaining -= consumed

            if rollover_bal > 0 and remaining > 0:
                consumed     = min(rollover_bal, remaining)
                rollover_bal -= consumed
                remaining    -= consumed

            if remaining > 0:
                capacity_bal = max(0.0, capacity_bal - remaining)

            data.append({
                'SOLD_TO_ORGANIZATION_NAME':  customer['org'],
                'SOLD_TO_CUSTOMER_NAME':      customer['name'],
                'SOLD_TO_CONTRACT_NUMBER':    customer['contract'],
                'BALANCE_DATE':               date.date(),
                'CURRENCY':                   'USD',
                'FREE_USAGE_BALANCE':         0.0,
                'CAPACITY_BALANCE':           round(capacity_bal,   2),
                'ON_DEMAND_CONSUMPTION_BALANCE': 0,
                'ROLLOVER_BALANCE':           round(rollover_bal,   2),
            })

    df = pd.DataFrame(data)
    df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE']).dt.date
    return df

def generate_demo_contract_data():
    """Generate realistic demo contract data for 5 customers"""
    data = []
    today = datetime.now().date()

    for customer in DEMO_CUSTOMERS:
        info  = DEMO_CONTRACT_INFO.get(customer['name'], {'amount': 50000, 'days_ago': 180, 'duration': 365})
        start = today - timedelta(days=info['days_ago'])
        end   = start + timedelta(days=info['duration'])

        data.append({
            'SOLD_TO_CUSTOMER_NAME':    customer['name'],
            'SOLD_TO_CONTRACT_NUMBER':  customer['contract'],
            'START_DATE':               start,
            'END_DATE':                 end,
            'AMOUNT':                   info['amount'],
            'CURRENCY':                 'USD',
            'CONTRACT_ITEM':            'Snowflake Credits',
        })

    return pd.DataFrame(data)

def generate_demo_customer_list():
    """Generate demo customer list"""
    return ["All Customers"] + [c['name'] for c in DEMO_CUSTOMERS]

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
    
    # Normalise string columns — lowercase USAGE_TYPE so live data (which may return
    # "Compute", "Data Transfer", etc.) matches the lowercase keys in USAGE_TYPE_DISPLAY
    for col in ['USAGE_TYPE', 'BALANCE_SOURCE']:
        if col in df.columns:
            df[col] = df[col].fillna('unknown').str.strip().str.lower()
    
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

def calculate_run_rate_by_customer(usage_df, balance_df=None, run_rate_days=7):
    """
    Calculate consumption run rate per customer based on recent usage
    
    Args:
        usage_df: DataFrame with usage data
        balance_df: DataFrame with balance data (optional)
        run_rate_days: Number of recent days to use for run rate calculation (default 7)
    
    Returns:
        DataFrame with run rate metrics per customer
    """
    if usage_df.empty:
        return pd.DataFrame()
    
    # Get the most recent N days of data
    max_date = usage_df['USAGE_DATE'].max()
    cutoff_date = max_date - timedelta(days=run_rate_days)
    recent_usage = usage_df[usage_df['USAGE_DATE'] > cutoff_date]
    
    if recent_usage.empty:
        return pd.DataFrame()
    
    # Calculate actual days in the period
    actual_days = (max_date - recent_usage['USAGE_DATE'].min()).days + 1
    
    # Aggregate by customer
    run_rate_data = recent_usage.groupby('SOLD_TO_CUSTOMER_NAME').agg({
        'CREDITS_USED': 'sum',
        'USAGE_IN_CURRENCY': ['sum', lambda x: x.iloc[0] if len(x) > 0 else 'USD'],
        'USAGE_DATE': ['min', 'max']
    }).reset_index()
    
    # Flatten column names
    run_rate_data.columns = ['CUSTOMER', 'TOTAL_CREDITS', 'TOTAL_COST', 'CURRENCY', 'START_DATE', 'END_DATE']
    
    # Calculate daily run rate
    run_rate_data['DAILY_RUN_RATE_CREDITS'] = run_rate_data['TOTAL_CREDITS'] / actual_days
    run_rate_data['DAILY_RUN_RATE_COST'] = run_rate_data['TOTAL_COST'] / actual_days
    
    # Calculate projected monthly consumption (30 days)
    run_rate_data['PROJECTED_MONTHLY_CREDITS'] = run_rate_data['DAILY_RUN_RATE_CREDITS'] * 30
    run_rate_data['PROJECTED_MONTHLY_COST'] = run_rate_data['DAILY_RUN_RATE_COST'] * 30
    
    # Add balance information if available
    if balance_df is not None and not balance_df.empty:
        # Get latest balance for each customer
        latest_balances = balance_df.loc[balance_df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()]
        balance_lookup = latest_balances.set_index('SOLD_TO_CUSTOMER_NAME')[
            ['FREE_USAGE_BALANCE', 'CAPACITY_BALANCE', 'ROLLOVER_BALANCE', 'TOTAL_BALANCE']
        ].to_dict('index')
        
        run_rate_data['CURRENT_BALANCE'] = run_rate_data['CUSTOMER'].map(
            lambda x: balance_lookup.get(x, {}).get('TOTAL_BALANCE', 0)
        )
        
        # Calculate days until balance depletion
        run_rate_data['DAYS_UNTIL_DEPLETION'] = run_rate_data.apply(
            lambda row: (row['CURRENT_BALANCE'] / row['DAILY_RUN_RATE_COST']) 
            if row['DAILY_RUN_RATE_COST'] > 0 and row['CURRENT_BALANCE'] > 0 
            else None, 
            axis=1
        )
    else:
        run_rate_data['CURRENT_BALANCE'] = 0
        run_rate_data['DAYS_UNTIL_DEPLETION'] = None
    
    # Add metadata
    run_rate_data['RUN_RATE_PERIOD_DAYS'] = actual_days
    
    # Sort by daily run rate descending
    run_rate_data = run_rate_data.sort_values('DAILY_RUN_RATE_CREDITS', ascending=False)
    
    return run_rate_data

def calculate_overall_run_rate(usage_df, balance_df=None, run_rate_days=7):
    """Calculate overall run rate across all customers"""
    if usage_df.empty:
        return {}
    
    # Get the most recent N days of data
    max_date = usage_df['USAGE_DATE'].max()
    cutoff_date = max_date - timedelta(days=run_rate_days)
    recent_usage = usage_df[usage_df['USAGE_DATE'] > cutoff_date]
    
    if recent_usage.empty:
        return {}
    
    actual_days = (max_date - recent_usage['USAGE_DATE'].min()).days + 1
    
    total_credits = recent_usage['CREDITS_USED'].sum()
    total_cost = recent_usage['USAGE_IN_CURRENCY'].sum()
    
    daily_rate_credits = total_credits / actual_days
    daily_rate_cost = total_cost / actual_days
    
    run_rate = {
        'daily_rate_credits': daily_rate_credits,
        'daily_rate_cost': daily_rate_cost,
        'weekly_rate_credits': daily_rate_credits * 7,
        'weekly_rate_cost': daily_rate_cost * 7,
        'monthly_rate_credits': daily_rate_credits * 30,
        'monthly_rate_cost': daily_rate_cost * 30,
        'period_days': actual_days,
        'period_start': recent_usage['USAGE_DATE'].min(),
        'period_end': recent_usage['USAGE_DATE'].max()
    }
    
    # Add balance information if available
    if balance_df is not None and not balance_df.empty:
        latest_balances = balance_df.loc[balance_df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()]
        total_balance = latest_balances['TOTAL_BALANCE'].sum()
        run_rate['total_balance'] = total_balance
        
        if daily_rate_cost > 0:
            run_rate['days_until_depletion'] = total_balance / daily_rate_cost
        else:
            run_rate['days_until_depletion'] = None
    
    return run_rate

def calculate_contract_usage_metrics(usage_df, contract_df, run_rate_days=30):
    """
    Calculate contract usage metrics including capacity, overage, and projections
    
    Args:
        usage_df: DataFrame with usage data
        contract_df: DataFrame with contract data
        run_rate_days: Number of recent days to use for run rate calculation
    
    Returns:
        Dictionary with contract metrics per customer
    """
    if usage_df.empty or contract_df.empty:
        return {}
    
    metrics = {}
    
    for _, contract in contract_df.iterrows():
        customer_name = contract['SOLD_TO_CUSTOMER_NAME']
        contract_start = contract['START_DATE']
        contract_end = contract['END_DATE']
        capacity_purchased = contract['AMOUNT']
        
        # Filter usage for this customer and contract period
        customer_usage = usage_df[
            (usage_df['SOLD_TO_CUSTOMER_NAME'] == customer_name) &
            (usage_df['USAGE_DATE'] >= contract_start) &
            (usage_df['USAGE_DATE'] <= contract_end)
        ]
        
        if customer_usage.empty:
            continue
        
        # Calculate total usage
        total_used = customer_usage['USAGE_IN_CURRENCY'].sum()
        
        # Calculate overage
        overage = max(0, total_used - capacity_purchased)
        
        # Calculate days until overage
        today = datetime.now().date()
        days_in_contract = (contract_end - contract_start).days
        days_elapsed = (today - contract_start).days
        remaining_capacity = capacity_purchased - total_used
        
        # Calculate run rate based on recent days
        max_date = customer_usage['USAGE_DATE'].max()
        cutoff_date = max_date - timedelta(days=run_rate_days)
        recent_usage = customer_usage[customer_usage['USAGE_DATE'] > cutoff_date]
        
        if not recent_usage.empty and len(recent_usage) > 0:
            actual_days = (max_date - recent_usage['USAGE_DATE'].min()).days + 1
            daily_rate = recent_usage['USAGE_IN_CURRENCY'].sum() / actual_days
            
            # Calculate days until overage
            if daily_rate > 0 and remaining_capacity > 0:
                days_until_overage = remaining_capacity / daily_rate
            elif remaining_capacity <= 0:
                days_until_overage = 0
            else:
                days_until_overage = (contract_end - today).days
            
            # Calculate projected annual run rate
            annual_run_rate = daily_rate * 365
            
            # Calculate overage date
            overage_date = today + timedelta(days=days_until_overage)
            if overage_date > contract_end:
                overage_date = None
        else:
            daily_rate = 0
            days_until_overage = None
            annual_run_rate = 0
            overage_date = None
        
        metrics[customer_name] = {
            'contract_id': contract['SOLD_TO_CONTRACT_NUMBER'],
            'contract_start': contract_start,
            'contract_end': contract_end,
            'capacity_purchased': capacity_purchased,
            'total_used': total_used,
            'used_percent': (total_used / capacity_purchased * 100) if capacity_purchased > 0 else 0,
            'overage': overage,
            'remaining_capacity': remaining_capacity,
            'days_until_overage': days_until_overage,
            'overage_date': overage_date,
            'daily_run_rate': daily_rate,
            'annual_run_rate': annual_run_rate,
            'run_rate_period': run_rate_days,
            'currency': contract['CURRENCY'],
            'days_in_contract': days_in_contract,
            'days_elapsed': days_elapsed
        }
    
    return metrics

def create_contract_usage_chart(usage_df, contract_metrics, customer_name):
    """
    Create contract usage visualization with actual vs predicted consumption and dual y-axes
    
    Args:
        usage_df: DataFrame with usage data
        contract_metrics: Dictionary with contract metrics for the customer
        customer_name: Name of the customer
    
    Returns:
        Plotly figure object with dual y-axes (daily consumption left, cumulative right)
    """
    from plotly.subplots import make_subplots
    
    if usage_df.empty or not contract_metrics:
        return None
    
    metrics = contract_metrics.get(customer_name)
    if not metrics:
        return None
    
    # Filter usage for this customer
    customer_usage = usage_df[usage_df['SOLD_TO_CUSTOMER_NAME'] == customer_name].copy()
    customer_usage = customer_usage.sort_values('USAGE_DATE')
    
    # Calculate cumulative consumption
    customer_usage['CUMULATIVE_USAGE'] = customer_usage['USAGE_IN_CURRENCY'].cumsum()
    
    # Create prediction line
    contract_start = metrics['contract_start']
    contract_end = metrics['contract_end']
    today = datetime.now().date()
    
    # Generate dates for prediction
    if metrics['daily_run_rate'] > 0:
        # Actual dates
        actual_dates = customer_usage['USAGE_DATE'].tolist()
        actual_values = customer_usage['USAGE_IN_CURRENCY'].tolist()
        actual_cumulative = customer_usage['CUMULATIVE_USAGE'].tolist()
        
        # Prediction from today to contract end
        current_cumulative = customer_usage['CUMULATIVE_USAGE'].iloc[-1] if not customer_usage.empty else 0
        prediction_dates = pd.date_range(start=today, end=contract_end, freq='D')
        
        prediction_daily = [metrics['daily_run_rate'] for _ in prediction_dates]
        prediction_cumulative = []
        for i, date in enumerate(prediction_dates):
            predicted = current_cumulative + (metrics['daily_run_rate'] * i)
            prediction_cumulative.append(predicted)
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add actual consumption area (blue) - left y-axis
        fig.add_trace(
            go.Scatter(
                x=actual_dates,
                y=actual_values,
                name='Actual',
                fill='tozeroy',
                fillcolor='rgba(66, 133, 244, 0.7)',
                line=dict(color='rgba(66, 133, 244, 1)', width=0),
                mode='none',
                legendgroup='actual'
            ),
            secondary_y=False
        )
        
        # Add predicted consumption area (orange) - left y-axis
        fig.add_trace(
            go.Scatter(
                x=prediction_dates,
                y=prediction_daily,
                name='Prediction',
                fill='tozeroy',
                fillcolor='rgba(255, 167, 38, 0.7)',
                line=dict(color='rgba(255, 167, 38, 1)', width=0),
                mode='none',
                legendgroup='prediction'
            ),
            secondary_y=False
        )
        
        # Combine all dates and cumulative values for the line
        all_dates = actual_dates + prediction_dates.tolist()
        all_cumulative = actual_cumulative + prediction_cumulative
        
        # Add cumulative consumption line (black) - right y-axis
        fig.add_trace(
            go.Scatter(
                x=all_dates,
                y=all_cumulative,
                name='Cumulative Consump',
                line=dict(color='black', width=2),
                mode='lines',
                legendgroup='cumulative'
            ),
            secondary_y=True
        )
        
        # Add capacity contract amount line (gray horizontal) - right y-axis
        fig.add_trace(
            go.Scatter(
                x=[contract_start, contract_end],
                y=[metrics['capacity_purchased'], metrics['capacity_purchased']],
                name='Capacity Contract Amt',
                line=dict(color='gray', width=2, dash='dash'),
                mode='lines',
                legendgroup='capacity'
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            hovermode='x unified',
            height=450,
            margin=dict(l=50, r=50, t=30, b=80),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            plot_bgcolor='white'
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text=f"Consumption ({metrics['currency']})",
            secondary_y=False,
            gridcolor='lightgray',
            tickformat="$,.0f"
        )
        fig.update_yaxes(
            title_text="Cumulative Consumption",
            secondary_y=True,
            gridcolor='lightgray',
            tickformat="$,.0f"
        )
        
        # Update x-axis
        fig.update_xaxes(
            tickformat="%m/%d/%Y",
            tickangle=45,
            gridcolor='lightgray',
            nticks=20
        )
        
        return fig
    
    return None

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
        border-radius: 5px;
    }
    /* Fix sidebar text visibility in dark mode */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

def get_snowflake_session():
    """Get Snowflake session for Streamlit in Snowflake with token refresh support"""
    try:
        # Use Streamlit's built-in Snowflake connection for Streamlit in Snowflake
        conn = st.connection('snowflake')
        session = conn.session()
        # Test connection to verify token is valid
        session.sql("SELECT CURRENT_USER()").collect()
        return session
    except Exception as e:
        error_msg = str(e).lower()
        if 'token' in error_msg or 'expired' in error_msg or 'authentication' in error_msg:
            st.session_state['auth_expired'] = True
            return None
        st.error(f"❌ {MESSAGES['connection_error']}\nDetails: {str(e)}")
        return None

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_usage_data(_session, start_date, end_date, customer_filter=None, usage_type_filter=None):
    """Enhanced usage data loading with additional filters - falls back to demo data"""
    # Use demo data if flag is set
    if USE_DEMO_DATA:
        df = generate_demo_usage_data(start_date, end_date)
        if customer_filter and customer_filter != "All Customers":
            df = df[df['SOLD_TO_CUSTOMER_NAME'] == customer_filter]
        if usage_type_filter:
            df = df[df['USAGE_TYPE'].isin(usage_type_filter)]
        return clean_usage_data(df)
    
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
            safe_customer = customer_filter.replace("'", "''")
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{safe_customer}'"

        if usage_type_filter:
            usage_types = "', '".join(usage_type_filter)
            query += f" AND USAGE_TYPE IN ('{usage_types}')"
            
        query += f" ORDER BY USAGE_DATE DESC, SOLD_TO_CUSTOMER_NAME LIMIT {QUERY_LIMITS['max_rows']}"
        
        df = _session.sql(query).to_pandas()
        return clean_usage_data(df)
        
    except Exception as e:
        st.info("ℹ️ Live billing data is unavailable — displaying demo data.")
        df = generate_demo_usage_data(start_date, end_date)
        if customer_filter and customer_filter != "All Customers":
            df = df[df['SOLD_TO_CUSTOMER_NAME'] == customer_filter]
        if usage_type_filter:
            df = df[df['USAGE_TYPE'].isin(usage_type_filter)]
        return clean_usage_data(df)

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_balance_data(_session, start_date, end_date, customer_filter=None):
    """Enhanced balance data loading - falls back to demo data"""
    # Use demo data if flag is set
    if USE_DEMO_DATA:
        df = generate_demo_balance_data(start_date, end_date)
        if customer_filter and customer_filter != "All Customers":
            df = df[df['SOLD_TO_CUSTOMER_NAME'] == customer_filter]
        return clean_balance_data(df)
    
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
            safe_customer = customer_filter.replace("'", "''")
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{safe_customer}'"

        query += " ORDER BY DATE DESC, SOLD_TO_CUSTOMER_NAME"
        
        df = _session.sql(query).to_pandas()
        return clean_balance_data(df)
        
    except Exception as e:
        df = generate_demo_balance_data(start_date, end_date)
        if customer_filter and customer_filter != "All Customers":
            df = df[df['SOLD_TO_CUSTOMER_NAME'] == customer_filter]
        return clean_balance_data(df)

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_contract_data(_session, customer_filter=None):
    """Load contract data from PARTNER_CONTRACT_ITEMS - falls back to demo data"""
    # Use demo data if flag is set
    if USE_DEMO_DATA:
        df = generate_demo_contract_data()
        if customer_filter and customer_filter != "All Customers":
            df = df[df['SOLD_TO_CUSTOMER_NAME'] == customer_filter]
        return df
    
    try:
        query = f"""
        SELECT 
            SOLD_TO_CUSTOMER_NAME,
            SOLD_TO_CONTRACT_NUMBER,
            START_DATE,
            END_DATE,
            AMOUNT,
            CURRENCY,
            CONTRACT_ITEM
        FROM {BILLING_SCHEMA}.{VIEWS['CONTRACT']}
        WHERE END_DATE >= CURRENT_DATE
        """
        
        if customer_filter and customer_filter != "All Customers":
            safe_customer = customer_filter.replace("'", "''")
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{safe_customer}'"

        query += " ORDER BY SOLD_TO_CUSTOMER_NAME, START_DATE DESC"
        
        df = _session.sql(query).to_pandas()
        
        # Convert date columns
        if not df.empty:
            df['START_DATE'] = pd.to_datetime(df['START_DATE']).dt.date
            df['END_DATE'] = pd.to_datetime(df['END_DATE']).dt.date
            df['AMOUNT'] = df['AMOUNT'].fillna(0)
        
        return df
        
    except Exception as e:
        df = generate_demo_contract_data()
        if customer_filter and customer_filter != "All Customers":
            df = df[df['SOLD_TO_CUSTOMER_NAME'] == customer_filter]
        return df

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_customer_list(_session):
    """Load available customers dynamically - falls back to demo data"""
    # Use demo data if flag is set
    if USE_DEMO_DATA:
        return generate_demo_customer_list()
    
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
        return generate_demo_customer_list()

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

def create_balance_by_customer_chart(df):
    """Grouped bar chart showing latest balance composition per customer"""
    if df.empty:
        return None

    latest = df.loc[df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()].copy()

    bar_data = []
    for _, row in latest.iterrows():
        for col, label, color in [
            ('CAPACITY_BALANCE',  'Capacity', '#1f77b4'),
            ('ROLLOVER_BALANCE',  'Rollover', '#2ca02c'),
        ]:
            bar_data.append({
                'Customer': row['SOLD_TO_CUSTOMER_NAME'],
                'Type': label,
                'Balance': row[col],
                'Color': color
            })

    bar_df = pd.DataFrame(bar_data)
    bar_df = bar_df[bar_df['Balance'] > 0]

    if bar_df.empty:
        return None

    fig = px.bar(
        bar_df,
        x='Customer',
        y='Balance',
        color='Type',
        barmode='stack',
        labels={'Balance': 'Balance ($)', 'Customer': ''},
        color_discrete_map={'Capacity': '#1f77b4', 'Rollover': '#2ca02c', 'Free Usage': '#9467bd'},
        text='Balance'
    )
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='inside')
    fig.update_layout(
        height=380,
        legend=dict(
            orientation='h', y=-0.25, x=0,
            title=dict(text='Type ', side='left')
        ),
        margin=dict(t=20, b=80),
        xaxis_tickangle=-20,
        yaxis_tickformat='$,.0f'
    )
    return fig

def create_usage_heatmap(df):
    """Create heatmap showing credit usage patterns by day of week and week"""
    if df.empty:
        return None

    df = df.copy()
    dates = pd.to_datetime(df['USAGE_DATE'])
    df['DAY_OF_WEEK'] = dates.dt.day_name()
    # Use the Monday of each ISO week as a human-readable label
    df['WEEK_START'] = (dates - pd.to_timedelta(dates.dt.dayofweek, unit='d')).dt.strftime('%b %-d')

    heatmap_data = df.groupby(['WEEK_START', 'DAY_OF_WEEK'])['CREDITS_USED'].sum().reset_index()

    # Keep week order sorted by actual date
    week_order = (
        df.drop_duplicates('WEEK_START')
        .assign(SORT_DATE=pd.to_datetime(df.drop_duplicates('USAGE_DATE')
                .groupby(lambda _: True).first()['USAGE_DATE']))
    )
    # Simple sort: re-derive the original Monday dates for ordering
    df['_WEEK_MON'] = dates - pd.to_timedelta(dates.dt.dayofweek, unit='d')
    week_sort = (
        df[['WEEK_START', '_WEEK_MON']]
        .drop_duplicates()
        .sort_values('_WEEK_MON')['WEEK_START']
        .tolist()
    )

    heatmap_pivot = heatmap_data.pivot(
        index='WEEK_START', columns='DAY_OF_WEEK', values='CREDITS_USED'
    ).fillna(0)

    day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    full_to_short = {
        'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
        'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
    }
    heatmap_pivot = heatmap_pivot.rename(columns=full_to_short)
    heatmap_pivot = heatmap_pivot.reindex(columns=day_order, fill_value=0)

    # Sort rows by week date
    valid_weeks = [w for w in week_sort if w in heatmap_pivot.index]
    heatmap_pivot = heatmap_pivot.reindex(valid_weeks)

    fig = px.imshow(
        heatmap_pivot,
        color_continuous_scale="Blues",
        aspect="auto",
        labels=dict(x="", y="Week of", color="Credits")
    )
    fig.update_layout(
        title="Credit usage by day of week — weekends typically lower",
        xaxis_title="",
        yaxis_title="",
        height=min(480, max(220, len(heatmap_pivot) * 38 + 100)),
        coloraxis_colorbar=dict(title="Credits", thickness=12, len=0.7),
        margin=dict(l=10, r=20, t=40, b=10)
    )
    fig.update_xaxes(side="top")
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
    
    col1, col2, col3 = st.columns(3)
    
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
            "Avg Daily Credits",
            format_credits(summary['avg_daily_credits']),
            delta=None
        )
    
    # Additional balance metrics if available
    if not balance_df.empty:
        balance_summary = get_balance_summary(balance_df)
        
        st.markdown("### 💰 Balance Metrics")
        total_balance = (
            balance_summary['total_free_usage'] +
            balance_summary['total_capacity'] +
            balance_summary['total_rollover']
        )
        col1, _ = st.columns([1, 3])
        with col1:
            st.metric(
                "Total Available Balance",
                format_currency(total_balance, currency),
                help="Capacity + Rollover — total credits available before on-demand charges apply"
            )

def main():
    # Header with enhanced styling
    st.markdown(f'<h1 class="main-header">{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time credit consumption monitoring for Snowflake reseller customers")
    
    # Demo mode banner
    if USE_DEMO_DATA:
        st.info("🎭 **Demo Mode Active** - Displaying sample data for 5 fictional customers. Set `USE_DEMO_DATA = False` to use live BILLING schema data.")
    
    st.markdown("---")
    
    # Get Snowflake session
    session = get_snowflake_session()
    if not session:
        if st.session_state.get('auth_expired', False):
            st.error("🔐 **Authentication token has expired**")
            st.info("""
To reconnect, please try one of the following:
1. **Refresh the browser page** - this will prompt for re-authentication
2. **Run in terminal**: `snow connection test` to refresh your connection
3. **Re-authenticate via SSO** if using federated authentication
            """)
            if st.button("🔄 Retry Connection", type="primary"):
                st.session_state['auth_expired'] = False
                st.cache_data.clear()
                st.rerun()
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

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Data", help="Clear cached data and reload from source", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.caption("🕐 Data refreshed every hour. For the most current information, refresh the page.")

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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Trends", "🎯 Usage Patterns", "💰 Financial Health", "🔬 Feature Adoption"])
    
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
        usage_by_type = usage_df.groupby('USAGE_TYPE').agg(
            CREDITS_USED=('CREDITS_USED', 'sum'),
            COST=('USAGE_IN_CURRENCY', 'sum')
        ).reset_index()
        usage_by_type['Feature'] = usage_by_type['USAGE_TYPE'].apply(
            lambda x: USAGE_TYPE_DISPLAY.get(x, x.title())
        )
        usage_by_type = usage_by_type.sort_values('CREDITS_USED', ascending=False)
        currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"

        col1, col2 = st.columns([2, 3])

        with col1:
            fig_pie = px.pie(
                usage_by_type,
                values='CREDITS_USED',
                names='Feature',
                title='Credit share by feature',
                hole=0.35
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=380, showlegend=False, margin=dict(t=40, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_bar = px.bar(
                usage_by_type,
                x='Feature',
                y='CREDITS_USED',
                color='Feature',
                title='Credits consumed per feature',
                labels={'CREDITS_USED': 'Total Credits', 'Feature': ''},
                text='CREDITS_USED'
            )
            fig_bar.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside',
                showlegend=False
            )
            fig_bar.update_layout(
                height=380,
                xaxis_tickangle=-30,
                margin=dict(t=40, b=80),
                yaxis_title="Credits"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Summary table below
        display_type = usage_by_type.copy()
        display_type['Credits'] = display_type['CREDITS_USED'].apply(format_credits)
        display_type['Cost'] = display_type['COST'].apply(lambda v: format_currency(v, currency))
        display_type['Share'] = (display_type['CREDITS_USED'] / display_type['CREDITS_USED'].sum() * 100).apply(lambda x: f"{x:.1f}%")
        st.dataframe(
            display_type[['Feature', 'Credits', 'Cost', 'Share']],
            use_container_width=True, hide_index=True
        )
    
    with tab3:  # Financial Health (Contract Status + Balance & Run Rate)
        currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"

        # ── Shared projection window selector ─────────────────────────────────
        if 'financial_run_rate_days' not in st.session_state:
            st.session_state['financial_run_rate_days'] = 30
        col_rr, _ = st.columns([1, 4])
        with col_rr:
            financial_run_rate_days = st.selectbox(
                "Projection window",
                options=[7, 30, 60, 90],
                index=[7, 30, 60, 90].index(st.session_state['financial_run_rate_days']),
                format_func=lambda x: f"Last {x} days",
                help="Days of recent consumption used to calculate run rate and projections across both sections below",
                key="financial_run_rate_days"
            )

        # Load contracts and full-period usage up front so both sections share
        # the same dataset — keeps the run rate KPIs consistent with the chart.
        with st.spinner("Loading contract data..."):
            contract_df = load_contract_data(session, customer_filter)

        if not contract_df.empty:
            contract_data_start = contract_df['START_DATE'].min()
            if contract_data_start < start_date:
                with st.spinner("Loading full contract history..."):
                    contract_usage_df = load_usage_data(
                        session, contract_data_start, end_date, customer_filter, None
                    )
            else:
                contract_usage_df = usage_df
        else:
            contract_usage_df = usage_df

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 1 — BALANCE & RUN RATE (summary, shown first)
        # ══════════════════════════════════════════════════════════════════════
        st.markdown("#### 💰 Balance & Run Rate")
        st.caption(f"Based on the last {financial_run_rate_days} days of consumption across the full contract period")

        overall_run_rate = calculate_overall_run_rate(contract_usage_df, balance_df, financial_run_rate_days)
        customer_run_rates = calculate_run_rate_by_customer(contract_usage_df, balance_df, financial_run_rate_days)

        if overall_run_rate:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Daily Run Rate",
                    format_credits(overall_run_rate['daily_rate_credits']),
                    delta=f"{format_currency(overall_run_rate['daily_rate_cost'], currency)}/day"
                )
            with col2:
                st.metric(
                    "Weekly Projection",
                    format_credits(overall_run_rate['weekly_rate_credits']),
                    delta=f"{format_currency(overall_run_rate['weekly_rate_cost'], currency)}/week"
                )
            with col3:
                st.metric(
                    "Monthly Projection",
                    format_credits(overall_run_rate['monthly_rate_credits']),
                    delta=f"{format_currency(overall_run_rate['monthly_rate_cost'], currency)}/month"
                )
            with col4:
                if overall_run_rate.get('days_until_depletion'):
                    days_remaining = overall_run_rate['days_until_depletion']
                    dep_icon = "🔴" if days_remaining < 30 else "🟡" if days_remaining < 60 else "🟢"
                    depletion_date = (datetime.now().date() + timedelta(days=int(days_remaining))).strftime('%-d %b %Y')
                    st.metric(
                        "Days Until Depletion",
                        f"{dep_icon} {days_remaining:.0f}",
                        delta=f"~{depletion_date} · Balance: {format_currency(overall_run_rate['total_balance'], currency)}"
                    )
                else:
                    st.metric("Days Until Depletion", "N/A", delta="No balance data")

        if not customer_run_rates.empty:
            csv_run_rate = export_to_csv(customer_run_rates, "run_rate_data")
            if csv_run_rate:
                st.download_button(
                    label="⬇️ Download run rate data",
                    data=csv_run_rate,
                    file_name=f"run_rate_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )

        st.markdown("---")

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 2 — CONTRACT STATUS
        # ══════════════════════════════════════════════════════════════════════
        st.markdown("#### 📋 Contract Status")

        if contract_df.empty:
            st.info("No active contracts found for the selected customer.")
        else:
            contract_metrics = calculate_contract_usage_metrics(
                contract_usage_df, contract_df, financial_run_rate_days
            )

            if not contract_metrics:
                st.info("No usage data available for active contracts.")
            else:
                if customer_filter == "All Customers":
                    selected_customer = st.selectbox(
                        "Select Customer to View",
                        options=list(contract_metrics.keys()),
                        index=0,
                        key="contract_customer_select"
                    )
                else:
                    selected_customer = customer_filter

                metrics = contract_metrics.get(selected_customer)

                if metrics:
                    st.markdown(f"**{selected_customer}** — Contract #{metrics['contract_id']}")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Capacity Purchased",
                            format_currency(metrics['capacity_purchased'], metrics['currency']),
                            delta=f"Start: {metrics['contract_start'].strftime('%m/%d/%Y')}"
                        )
                    with col2:
                        st.metric(
                            "Total Used",
                            format_currency(metrics['total_used'], metrics['currency']),
                            delta=f"{metrics['used_percent']:.1f}% of capacity"
                        )
                    with col3:
                        overage_val = metrics['overage']
                        st.metric(
                            "Overage",
                            format_currency(overage_val, metrics['currency']) if overage_val > 0 else "$0.00",
                            delta=f"End: {metrics['contract_end'].strftime('%m/%d/%Y')}"
                        )
                    with col4:
                        if metrics['days_until_overage'] is not None and metrics['days_until_overage'] >= 0:
                            ov_icon = "🔴" if metrics['days_until_overage'] < 30 else "🟡" if metrics['days_until_overage'] < 60 else "🟢"
                            ov_delta = f"Overage: {metrics['overage_date'].strftime('%m/%d/%Y')}" if metrics['overage_date'] else "Within contract"
                            st.metric("Days Until Overage", f"{ov_icon} {int(metrics['days_until_overage'])}", delta=ov_delta)
                        else:
                            st.metric("Days Until Overage", "N/A", delta="Sufficient capacity")

                    st.caption("Used % and Days Until Overage are calculated against Capacity Purchased. Rollover and other adjustments may differ slightly from Snowflake's billing portal.")

                    if metrics['days_until_overage'] is not None and metrics['overage_date']:
                        st.markdown(
                            f'<div style="color: #dc3545; font-weight: bold; text-align: right; font-size: 1.1rem; margin-top: 0.25rem;">⚠️ Projected to exhaust capacity by {metrics["overage_date"].strftime("%m/%d/%Y")}</div>',
                            unsafe_allow_html=True
                        )

                    col_chart, col_aside = st.columns([3, 1])
                    with col_chart:
                        chart = create_contract_usage_chart(contract_usage_df, contract_metrics, selected_customer)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                        else:
                            st.info("Not enough data to generate the projection chart.")
                    with col_aside:
                        st.markdown("**Consumption Run Rate**")
                        st.markdown(f"### {format_currency(metrics['annual_run_rate'], metrics['currency'])}")
                        st.caption("Avg daily × 365")

                    with st.expander("📄 Contract Details", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Timeline**")
                            st.write(f"- Start: {metrics['contract_start'].strftime('%B %d, %Y')}")
                            st.write(f"- End: {metrics['contract_end'].strftime('%B %d, %Y')}")
                            st.write(f"- Duration: {metrics['days_in_contract']} days")
                            st.write(f"- Elapsed: {metrics['days_elapsed']} days")
                            st.write(f"- Remaining: {(metrics['contract_end'] - datetime.now().date()).days} days")
                        with col2:
                            st.markdown("**Projections**")
                            st.write(f"- Daily: {format_currency(metrics['daily_run_rate'], metrics['currency'])}/day")
                            st.write(f"- Weekly: {format_currency(metrics['daily_run_rate'] * 7, metrics['currency'])}/week")
                            st.write(f"- Monthly: {format_currency(metrics['daily_run_rate'] * 30, metrics['currency'])}/month")
                            st.write(f"- Annual: {format_currency(metrics['annual_run_rate'], metrics['currency'])}/year")
                            st.write(f"- Window: last {metrics['run_rate_period']} days")
    
    with tab4:
        st.markdown("### 🔬 Feature Adoption")
        st.markdown("*Which Snowflake features are your customers using — and where are the upsell opportunities?*")

        if usage_df.empty:
            st.info("No usage data available for feature analysis.")
        else:
            currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"
            all_known_features = set(USAGE_TYPE_DISPLAY.keys())
            used_globally = set(usage_df['USAGE_TYPE'].str.lower().unique())

            # ── Customer deep dive ────────────────────────────────────────────
            st.markdown("#### Customer Feature Breakdown")

            if customer_filter == "All Customers":
                feature_customer = st.selectbox(
                    "Select a customer",
                    options=sorted(usage_df['SOLD_TO_CUSTOMER_NAME'].unique()),
                    key="feature_customer_select"
                )
            else:
                feature_customer = customer_filter
                st.markdown(f"Showing: **{feature_customer}**")

            customer_feature_df = usage_df[usage_df['SOLD_TO_CUSTOMER_NAME'] == feature_customer]

            if not customer_feature_df.empty:
                cust_feature_summary = customer_feature_df.groupby('USAGE_TYPE').agg(
                    total_credits=('CREDITS_USED', 'sum'),
                    total_cost=('USAGE_IN_CURRENCY', 'sum'),
                    days_active=('USAGE_DATE', 'nunique'),
                    first_seen=('USAGE_DATE', 'min'),
                    last_seen=('USAGE_DATE', 'max')
                ).reset_index()
                total_cust_credits = cust_feature_summary['total_credits'].sum()
                cust_feature_summary['pct_total'] = (
                    cust_feature_summary['total_credits'] / total_cust_credits * 100
                ).round(1)
                cust_feature_summary = cust_feature_summary.sort_values('total_credits', ascending=False)

                col1, col2 = st.columns([3, 2])

                with col1:
                    feature_trend = (
                        customer_feature_df
                        .groupby(['USAGE_DATE', 'USAGE_TYPE'])['CREDITS_USED']
                        .sum()
                        .reset_index()
                    )
                    feature_trend['Feature'] = feature_trend['USAGE_TYPE'].apply(
                        lambda x: USAGE_TYPE_DISPLAY.get(x, x.title())
                    )
                    fig_trend = px.area(
                        feature_trend,
                        x='USAGE_DATE',
                        y='CREDITS_USED',
                        color='Feature',
                        title=f'Feature usage over time — {feature_customer}',
                        labels={'CREDITS_USED': 'Credits', 'USAGE_DATE': 'Date'}
                    )
                    fig_trend.update_layout(height=340, hovermode='x unified',
                                            legend=dict(orientation='h', y=-0.25))
                    st.plotly_chart(fig_trend, use_container_width=True)

                with col2:
                    display_cust = cust_feature_summary.copy()
                    display_cust['Feature'] = display_cust['USAGE_TYPE'].apply(
                        lambda x: USAGE_TYPE_DISPLAY.get(x, x.title())
                    )
                    display_cust['Credits'] = display_cust['total_credits'].apply(format_credits)
                    display_cust['Cost'] = display_cust.apply(
                        lambda row: format_currency(row['total_cost'], currency), axis=1
                    )
                    display_cust['Share'] = display_cust['pct_total'].apply(lambda x: f"{x:.0f}%")
                    display_cust['Days Active'] = display_cust['days_active']
                    st.dataframe(
                        display_cust[['Feature', 'Credits', 'Cost', 'Share', 'Days Active']],
                        use_container_width=True,
                        height=340,
                        hide_index=True
                    )

            st.markdown("---")

            # ── Upsell opportunities ──────────────────────────────────────────
            st.markdown("**Upsell opportunities**")

            if customer_filter != "All Customers" and not customer_feature_df.empty:
                used_scope = set(customer_feature_df['USAGE_TYPE'].str.lower().unique())
                scope_label = f"Features **{customer_filter}** hasn't used in this period — potential upsell conversations:"
            else:
                used_scope = used_globally
                scope_label = "Features with **no usage across any customer** in this period:"

            unused_features = sorted(all_known_features - used_scope)

            if unused_features:
                st.caption(scope_label)
                # Show 2 cards per row
                for row_start in range(0, len(unused_features), 2):
                    row_feats = unused_features[row_start:row_start + 2]
                    cols = st.columns(len(row_feats))
                    for col_idx, feat in enumerate(row_feats):
                        display_name  = USAGE_TYPE_DISPLAY.get(feat, feat.title())
                        use_case_text = FEATURE_USECASES.get(feat, "Explore this feature with your customer.")
                        with cols[col_idx]:
                            st.markdown(
                                f'<div style="background:#fff3cd;padding:0.8rem 1rem;border-radius:8px;'
                                f'border-left:4px solid #ffc107;margin-bottom:0.75rem;">'
                                f'<strong style="color:#333333;font-size:1rem;">{display_name}</strong><br>'
                                f'<span style="color:#555555;font-size:0.85rem;line-height:1.4;">{use_case_text}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
            else:
                st.success("All tracked features are being used in this period.")

            # ── Data source note ─────────────────────────────────────────────
            with st.expander("ℹ️ Data source & schema reference", expanded=False):
                st.markdown("""
### Source: `SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY`

This is the authoritative reseller view — it shows daily credit consumption per customer account broken down by `USAGE_TYPE`. As a reseller this is the only Snowflake schema that exposes **your customers'** usage directly.

| `USAGE_TYPE` | Feature | Credit type |
|---|---|---|
| `compute` | 💻 Compute | Virtual warehouse credits |
| `storage` | 💾 Storage | TB/month |
| `data transfer` | 🌐 Data Transfer | Egress credits |
| `cloud services` | ☁️ Cloud Services | Metadata & API credits |
| `snowpipe` | 🚰 Snowpipe | Serverless ingest credits |
| `serverless tasks` | ⚡ Tasks | Serverless task credits |
| `automatic clustering` | ♻️ Auto Clustering | Clustering credits |
| `materialized views` | 📊 Materialized Views | Refresh credits |
| `search optimization` | 🔍 Search Optimization | Maintenance credits |
| `snowpark` | 🐍 Snowpark | Compute credits |
| `dynamic tables` | 🔄 Dynamic Tables | Refresh credits |
| `streams` | 🌊 Streams | Change tracking credits |
| `streamlit` | 📱 Streamlit | App compute credits |
| `cortex` | 🤖 Cortex AI Functions | Token-based credits |
| `cortex analyst` | 💬 Cortex Analyst | Query credits |
| `cortex search` | 🔎 Cortex Search | Index + serving credits |
| `cortex code` | 💡 Cortex Code | Token-based credits |
| `snowflake intelligence` | ✨ Snowflake Intelligence | Usage credits |
| `ml functions` | 🧠 ML Functions | Compute credits |

> **Demo mode:** synthetic data matches this schema exactly. Connect to your SPN account to see your customer consumption.
                """)


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