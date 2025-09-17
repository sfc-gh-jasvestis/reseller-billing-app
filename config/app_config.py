# Configuration settings for Snowflake Credit Usage Dashboard

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