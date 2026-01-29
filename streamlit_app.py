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
    "advanced_filters": True,
    "real_time_refresh": False,
    "email_reports": False
}

# Demo mode flag - set to True to use sample data when BILLING schema is unavailable
USE_DEMO_DATA = False

# Demo data configuration - 5 customers with varying usage patterns
DEMO_CUSTOMERS = [
    {"name": "Acme Corporation", "org": "Acme Inc", "contract": "ACME-2024-001", "tier": "enterprise", "usage_multiplier": 1.5},
    {"name": "TechStart Labs", "org": "TechStart Holdings", "contract": "TSL-2024-002", "tier": "standard", "usage_multiplier": 0.6},
    {"name": "Global Analytics Co", "org": "Global Analytics", "contract": "GAC-2024-003", "tier": "enterprise", "usage_multiplier": 2.2},
    {"name": "DataDriven Solutions", "org": "DataDriven Group", "contract": "DDS-2024-004", "tier": "business_critical", "usage_multiplier": 3.0},
    {"name": "SmallBiz Insights", "org": "SmallBiz LLC", "contract": "SBI-2024-005", "tier": "standard", "usage_multiplier": 0.3},
]

# =============================================================================
# DEMO DATA GENERATION FUNCTIONS
# =============================================================================
import numpy as np
import random

def generate_demo_usage_data(start_date, end_date):
    """Generate realistic demo usage data for 5 customers"""
    random.seed(42)
    np.random.seed(42)
    
    usage_types = ['compute', 'storage', 'data transfer', 'cloud services', 'snowpipe', 'serverless tasks']
    regions = ['AWS_US_WEST_2', 'AWS_US_EAST_1', 'AZURE_EASTUS2', 'AWS_EU_WEST_1']
    balance_sources = ['capacity', 'free usage', 'rollover']
    
    data = []
    date_range = pd.date_range(start=start_date, end=end_date)
    
    for customer in DEMO_CUSTOMERS:
        base_daily_credits = 100 * customer['usage_multiplier']
        
        for date in date_range:
            # Add weekend dip
            day_factor = 0.4 if date.weekday() >= 5 else 1.0
            # Add some trend (slight growth over time)
            trend_factor = 1 + (date - date_range[0]).days * 0.002
            # Add randomness
            random_factor = np.random.uniform(0.7, 1.3)
            
            for usage_type in usage_types:
                # Different usage types have different base amounts
                type_multipliers = {
                    'compute': 0.5,
                    'storage': 0.2,
                    'data transfer': 0.1,
                    'cloud services': 0.1,
                    'snowpipe': 0.05,
                    'serverless tasks': 0.05
                }
                
                credits = base_daily_credits * type_multipliers.get(usage_type, 0.1) * day_factor * trend_factor * random_factor
                credits = max(0, credits + np.random.normal(0, credits * 0.1))
                
                if credits > 0.01:
                    cost = credits * 3.00  # $3 per credit
                    data.append({
                        'SOLD_TO_ORGANIZATION_NAME': customer['org'],
                        'SOLD_TO_CUSTOMER_NAME': customer['name'],
                        'SOLD_TO_CONTRACT_NUMBER': customer['contract'],
                        'ACCOUNT_NAME': f"{customer['name'].replace(' ', '_').lower()}_account",
                        'ACCOUNT_LOCATOR': f"LOC{hash(customer['name']) % 100000:05d}",
                        'REGION': random.choice(regions),
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
    """Generate realistic demo balance data for 5 customers"""
    random.seed(42)
    np.random.seed(42)
    
    data = []
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Initial balances per customer
    initial_balances = {
        'Acme Corporation': {'capacity': 50000, 'free': 1000, 'rollover': 5000},
        'TechStart Labs': {'capacity': 15000, 'free': 500, 'rollover': 1000},
        'Global Analytics Co': {'capacity': 100000, 'free': 2000, 'rollover': 10000},
        'DataDriven Solutions': {'capacity': 200000, 'free': 5000, 'rollover': 25000},
        'SmallBiz Insights': {'capacity': 5000, 'free': 200, 'rollover': 500},
    }
    
    for customer in DEMO_CUSTOMERS:
        balances = initial_balances.get(customer['name'], {'capacity': 10000, 'free': 500, 'rollover': 1000})
        daily_burn = 100 * customer['usage_multiplier'] * 3.00  # Daily cost
        
        capacity_bal = balances['capacity']
        free_bal = balances['free']
        rollover_bal = balances['rollover']
        
        for date in date_range:
            # Consume from free first, then rollover, then capacity
            daily_consumption = daily_burn * np.random.uniform(0.8, 1.2)
            
            if free_bal > 0:
                consumed_free = min(free_bal, daily_consumption * 0.1)
                free_bal -= consumed_free
            
            if rollover_bal > 0:
                consumed_rollover = min(rollover_bal, daily_consumption * 0.1)
                rollover_bal -= consumed_rollover
            
            capacity_bal -= daily_consumption * 0.8
            capacity_bal = max(0, capacity_bal)
            
            data.append({
                'SOLD_TO_ORGANIZATION_NAME': customer['org'],
                'SOLD_TO_CUSTOMER_NAME': customer['name'],
                'SOLD_TO_CONTRACT_NUMBER': customer['contract'],
                'BALANCE_DATE': date.date(),
                'CURRENCY': 'USD',
                'FREE_USAGE_BALANCE': round(max(0, free_bal), 2),
                'CAPACITY_BALANCE': round(max(0, capacity_bal), 2),
                'ON_DEMAND_CONSUMPTION_BALANCE': 0,
                'ROLLOVER_BALANCE': round(max(0, rollover_bal), 2)
            })
    
    df = pd.DataFrame(data)
    df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE']).dt.date
    return df

def generate_demo_contract_data():
    """Generate realistic demo contract data for 5 customers"""
    data = []
    today = datetime.now().date()
    
    contract_amounts = {
        'Acme Corporation': 150000,
        'TechStart Labs': 45000,
        'Global Analytics Co': 300000,
        'DataDriven Solutions': 600000,
        'SmallBiz Insights': 15000,
    }
    
    for customer in DEMO_CUSTOMERS:
        amount = contract_amounts.get(customer['name'], 50000)
        start = today - timedelta(days=180)
        end = today + timedelta(days=185)
        
        data.append({
            'SOLD_TO_CUSTOMER_NAME': customer['name'],
            'SOLD_TO_CONTRACT_NUMBER': customer['contract'],
            'START_DATE': start,
            'END_DATE': end,
            'AMOUNT': amount,
            'CURRENCY': 'USD',
            'CONTRACT_ITEM': 'Snowflake Credits'
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
            'contract_id': contract['CONTRACT_ITEM'],
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
        background-color: #ffffff;
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
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
        
        if usage_type_filter:
            usage_types = "', '".join(usage_type_filter)
            query += f" AND USAGE_TYPE IN ('{usage_types}')"
            
        query += f" ORDER BY USAGE_DATE DESC, SOLD_TO_CUSTOMER_NAME LIMIT {QUERY_LIMITS['max_rows']}"
        
        df = _session.sql(query).to_pandas()
        return clean_usage_data(df)
        
    except Exception as e:
        st.warning(f"⚠️ Using demo data (BILLING schema not available): {str(e)}")
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
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
            
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
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
            
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
    
    # Demo mode banner
    if USE_DEMO_DATA:
        st.info("🎭 **Demo Mode Active** - Displaying sample data for 5 fictional customers. Set `USE_DEMO_DATA = False` to use live BILLING schema data.")
    
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Trends", "🎯 Usage Patterns", "💰 Balance Analysis", "⚡ Run Rate Analysis", "📋 Contract Usage Report"])
    
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
    
    with tab4:
        st.markdown("### ⚡ Consumption Run Rate Analysis")
        st.markdown("*Based on the most recent 7 days of usage data*")
        
        # Run rate period selector
        col1, col2 = st.columns([1, 3])
        with col1:
            run_rate_days = st.selectbox(
                "Run Rate Period",
                options=[3, 7, 14, 30],
                index=1,
                help="Number of recent days to calculate run rate"
            )
        
        # Calculate run rates
        overall_run_rate = calculate_overall_run_rate(usage_df, balance_df, run_rate_days)
        customer_run_rates = calculate_run_rate_by_customer(usage_df, balance_df, run_rate_days)
        
        if overall_run_rate:
            # Overall run rate metrics
            st.markdown("#### 📊 Overall Run Rate Metrics")
            
            currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"
            
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
                    depletion_color = "🔴" if days_remaining < 30 else "🟡" if days_remaining < 60 else "🟢"
                    st.metric(
                        "Days Until Depletion",
                        f"{depletion_color} {days_remaining:.0f}",
                        delta=f"Balance: {format_currency(overall_run_rate['total_balance'], currency)}"
                    )
                else:
                    st.metric("Days Until Depletion", "N/A", delta="No balance data")
            
            st.markdown("---")
        
        # Customer run rate table
        if not customer_run_rates.empty:
            st.markdown("#### 📋 Customer Run Rate Comparison")
            
            # Create formatted display dataframe
            display_run_rate = customer_run_rates.copy()
            
            # Format numeric columns
            display_run_rate['Daily Rate (Credits)'] = display_run_rate['DAILY_RUN_RATE_CREDITS'].apply(format_credits)
            display_run_rate['Daily Rate (Cost)'] = display_run_rate.apply(
                lambda row: format_currency(row['DAILY_RUN_RATE_COST'], row['CURRENCY']), axis=1
            )
            display_run_rate['Monthly Projection'] = display_run_rate.apply(
                lambda row: format_currency(row['PROJECTED_MONTHLY_COST'], row['CURRENCY']), axis=1
            )
            display_run_rate['Current Balance'] = display_run_rate.apply(
                lambda row: format_currency(row['CURRENT_BALANCE'], row['CURRENCY']), axis=1
            )
            
            # Format days until depletion with color coding
            def format_depletion(days):
                if pd.isna(days) or days is None:
                    return "N/A"
                if days < 30:
                    return f"🔴 {days:.0f} days"
                elif days < 60:
                    return f"🟡 {days:.0f} days"
                else:
                    return f"🟢 {days:.0f} days"
            
            display_run_rate['Days to Depletion'] = display_run_rate['DAYS_UNTIL_DEPLETION'].apply(format_depletion)
            
            # Select columns for display
            display_columns = [
                'CUSTOMER',
                'Daily Rate (Credits)',
                'Daily Rate (Cost)',
                'Monthly Projection',
                'Current Balance',
                'Days to Depletion'
            ]
            
            st.dataframe(
                display_run_rate[display_columns],
                use_container_width=True,
                height=400
            )
            
            # Run rate visualization
            st.markdown("#### 📊 Visual Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily run rate bar chart
                fig_run_rate = px.bar(
                    customer_run_rates.head(10),
                    x='DAILY_RUN_RATE_COST',
                    y='CUSTOMER',
                    orientation='h',
                    title='Top 10 Customers by Daily Run Rate (Cost)',
                    labels={'DAILY_RUN_RATE_COST': 'Daily Cost', 'CUSTOMER': 'Customer'}
                )
                fig_run_rate.update_traces(marker_color='lightblue')
                st.plotly_chart(fig_run_rate, use_container_width=True)
            
            with col2:
                # Days until depletion chart (only customers with balance data)
                depletion_data = customer_run_rates[customer_run_rates['DAYS_UNTIL_DEPLETION'].notna()].copy()
                if not depletion_data.empty:
                    # Color code by urgency
                    depletion_data['Urgency'] = depletion_data['DAYS_UNTIL_DEPLETION'].apply(
                        lambda x: 'Critical (<30 days)' if x < 30 else 'Warning (30-60 days)' if x < 60 else 'Healthy (>60 days)'
                    )
                    
                    fig_depletion = px.bar(
                        depletion_data.sort_values('DAYS_UNTIL_DEPLETION').head(10),
                        x='DAYS_UNTIL_DEPLETION',
                        y='CUSTOMER',
                        orientation='h',
                        title='Days Until Balance Depletion',
                        labels={'DAYS_UNTIL_DEPLETION': 'Days', 'CUSTOMER': 'Customer'},
                        color='Urgency',
                        color_discrete_map={
                            'Critical (<30 days)': '#d62728',
                            'Warning (30-60 days)': '#ff7f0e',
                            'Healthy (>60 days)': '#2ca02c'
                        }
                    )
                    st.plotly_chart(fig_depletion, use_container_width=True)
                else:
                    st.info("No balance data available to calculate depletion timeline.")
            
            # Export run rate data
            st.markdown("#### 📥 Export Run Rate Data")
            csv_run_rate = export_to_csv(customer_run_rates, "run_rate_data")
            if csv_run_rate:
                st.download_button(
                    label="⚡ Download Run Rate Analysis",
                    data=csv_run_rate,
                    file_name=f"run_rate_analysis_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Not enough data to calculate run rates. Try extending your date range.")
    
    with tab5:
        st.markdown("### 📋 Active Contract Usage Report")
        
        # Load contract data
        with st.spinner("Loading contract data..."):
            contract_df = load_contract_data(session, customer_filter)
        
        if contract_df.empty:
            st.warning("No active contracts found for the selected customer.")
        else:
            # Get run rate from session state (set by radio button below)
            if 'contract_run_rate' not in st.session_state:
                st.session_state.contract_run_rate = 30
            contract_run_rate_days = st.session_state.contract_run_rate
            contract_metrics = calculate_contract_usage_metrics(usage_df, contract_df, contract_run_rate_days)
            
            if not contract_metrics:
                st.warning("No usage data available for active contracts.")
            else:
                # Select customer to display (use first customer if "All Customers" is selected)
                if customer_filter == "All Customers":
                    available_customers = list(contract_metrics.keys())
                    selected_customer = st.selectbox(
                        "Select Customer to View",
                        options=available_customers,
                        index=0
                    )
                else:
                    selected_customer = customer_filter
                
                metrics = contract_metrics.get(selected_customer)
                
                if metrics:
                    # Contract header with customer name and contract ID
                    st.markdown(f"## Active Contract - {selected_customer} (ID: {metrics['contract_id']})")
                    st.markdown("---")
                    
                    # Key metrics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown("**Capacity Purchased**")
                        st.markdown(f"### {format_currency(metrics['capacity_purchased'], metrics['currency'])}")
                        st.markdown(f"↑ ContractStart: {metrics['contract_start'].strftime('%m/%d/%Y')}")
                    
                    with col2:
                        st.markdown("**Total Capacity Used**")
                        st.markdown(f"### {format_currency(metrics['total_used'], metrics['currency'])}")
                        st.markdown(f"↑ Used % *: {metrics['used_percent']:.1f}%")
                    
                    with col3:
                        overage_display = format_currency(metrics['overage'], metrics['currency']) if metrics['overage'] > 0 else "$0.00"
                        st.markdown("**Overage**")
                        st.markdown(f"### {overage_display}")
                        st.markdown(f"↑ ContractEnd: {metrics['contract_end'].strftime('%m/%d/%Y')}")
                    
                    with col4:
                        st.markdown("**Days until Overage**")
                        if metrics['days_until_overage'] is not None and metrics['days_until_overage'] >= 0:
                            st.markdown(f"### {int(metrics['days_until_overage'])} days")
                            overage_date_display = ""
                            if metrics['overage_date']:
                                overage_date_display = f"↑ Overage Date: {metrics['overage_date'].strftime('%m/%d/%Y')}"
                            st.markdown(overage_date_display)
                        else:
                            st.markdown("### N/A")
                            st.markdown("↑ Sufficient capacity")
                    
                    # Note about Capacity Used %
                    st.markdown("<small>*Note: Capacity Used % is based on Total Capacity = Capacity Purchased + Free Usage + Rollover + Offset - Adjustment + Bal Transfer + CurrencyConv Adj + DataSharing Rebate + Balance Exp</small>", unsafe_allow_html=True)
                    
                    # Alert banner if overage is imminent
                    if metrics['days_until_overage'] is not None and metrics['overage_date']:
                        st.markdown(
                            f'<div style="color: #dc3545; font-weight: bold; text-align: right; font-size: 1.2rem; margin-top: 0.5rem;">Will run out of credits by {metrics["overage_date"].strftime("%m/%d/%Y")}</div>',
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("---")
                    
                    # Two-column layout: left for run rate selector and metrics, right for chart
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown("**Select a Run Rate period**")
                        run_rate_options = [30, 60, 90, 180]
                        current_value = st.session_state.get('contract_run_rate', 30)
                        default_index = run_rate_options.index(current_value) if current_value in run_rate_options else 0
                        contract_run_rate_days = st.radio(
                            "Run Rate Period",
                            options=run_rate_options,
                            format_func=lambda x: f"{x} days",
                            index=default_index,
                            key="contract_run_rate",
                            label_visibility="collapsed"
                        )
                        
                        # Metrics already calculated at tab5 start with current run rate
                        
                        st.markdown("---")
                        st.markdown("**Consumption Run Rate**")
                        st.markdown(f"### {format_currency(metrics['annual_run_rate'], metrics['currency'])}")
                        st.markdown("↑ Avg Daily Consump.*365")
                        
                        # Green renewal recommendation box
                        st.markdown(
                            f"""
                            <div style="background-color: #d4edda; padding: 1rem; border-radius: 10px; border: 2px solid #28a745; margin-top: 1rem;">
                                <p style="color: #155724; margin-bottom: 0; font-weight: bold;">
                                    Estimated 12 months run rate - {format_currency(metrics['annual_run_rate'], metrics['currency'])}. Can we renew a bigger ACV?
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        # Create the contract usage chart with dual y-axes
                        chart = create_contract_usage_chart(usage_df, contract_metrics, selected_customer)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                        else:
                            st.info("Not enough data to generate usage projection chart.")
                    
                    st.markdown("---")
                    
                    # Additional contract details in expandable section
                    with st.expander("📄 Additional Contract Details", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Contract Timeline:**")
                            st.write(f"- Start Date: {metrics['contract_start'].strftime('%B %d, %Y')}")
                            st.write(f"- End Date: {metrics['contract_end'].strftime('%B %d, %Y')}")
                            st.write(f"- Days in Contract: {metrics['days_in_contract']} days")
                            st.write(f"- Days Elapsed: {metrics['days_elapsed']} days")
                            st.write(f"- Days Remaining: {(metrics['contract_end'] - datetime.now().date()).days} days")
                        
                        with col2:
                            st.markdown("**Consumption Metrics:**")
                            st.write(f"- Daily Run Rate: {format_currency(metrics['daily_run_rate'], metrics['currency'])}/day")
                            st.write(f"- Weekly Projection: {format_currency(metrics['daily_run_rate'] * 7, metrics['currency'])}/week")
                            st.write(f"- Monthly Projection: {format_currency(metrics['daily_run_rate'] * 30, metrics['currency'])}/month")
                            st.write(f"- Annual Run Rate: {format_currency(metrics['annual_run_rate'], metrics['currency'])}/year")
                            st.write(f"- Run Rate Period: Last {metrics['run_rate_period']} days")
    
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