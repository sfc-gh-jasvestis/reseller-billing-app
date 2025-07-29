import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from config.app_config import *

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

def filter_data_by_customer(df, customer_name):
    """Filter dataframe by customer name"""
    if df.empty or not customer_name:
        return df
    
    return df[df['SOLD_TO_CUSTOMER_NAME'] == customer_name]

def filter_data_by_usage_type(df, usage_types):
    """Filter dataframe by usage types"""
    if df.empty or not usage_types:
        return df
    
    return df[df['USAGE_TYPE'].isin(usage_types)]

def get_customer_list(df):
    """Get unique list of customers from dataframe"""
    if df.empty or 'SOLD_TO_CUSTOMER_NAME' not in df.columns:
        return []
    
    return sorted(df['SOLD_TO_CUSTOMER_NAME'].unique())

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

def create_drill_down_data(df, group_by_columns, metric_column):
    """Create drill-down data for hierarchical analysis"""
    if df.empty:
        return pd.DataFrame()
    
    grouped = (df.groupby(group_by_columns)[metric_column]
              .agg(['sum', 'count', 'mean'])
              .reset_index())
    
    grouped.columns = group_by_columns + ['Total', 'Count', 'Average']
    
    return grouped.sort_values('Total', ascending=False) 