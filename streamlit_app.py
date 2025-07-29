import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import snowflake.connector
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session

# Page configuration
st.set_page_config(
    page_title="Snowflake Credit Usage Dashboard",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metrics-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_snowflake_session():
    """Get active Snowflake session"""
    try:
        return get_active_session()
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_usage_data(session, start_date, end_date, customer_filter=None):
    """Load usage data from BILLING_USAGE.USAGE_IN_CURRENCY_DAILY"""
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
        FROM SNOWFLAKE.BILLING_USAGE.USAGE_IN_CURRENCY_DAILY
        WHERE USAGE_DATE BETWEEN '{start_date}' AND '{end_date}'
        """
        
        if customer_filter:
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
            
        query += " ORDER BY USAGE_DATE DESC, SOLD_TO_CUSTOMER_NAME"
        
        df = session.sql(query).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error loading usage data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_balance_data(session, start_date, end_date, customer_filter=None):
    """Load balance data from BILLING_USAGE.REMAINING_BALANCE_DAILY"""
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
        FROM SNOWFLAKE.BILLING_USAGE.REMAINING_BALANCE_DAILY
        WHERE DATE BETWEEN '{start_date}' AND '{end_date}'
        """
        
        if customer_filter:
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
            
        query += " ORDER BY DATE DESC, SOLD_TO_CUSTOMER_NAME"
        
        df = session.sql(query).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error loading balance data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_contract_data(session, customer_filter=None):
    """Load contract information"""
    try:
        query = """
        SELECT 
            SOLD_TO_ORGANIZATION_NAME,
            SOLD_TO_CUSTOMER_NAME,
            SOLD_TO_CONTRACT_NUMBER,
            START_DATE,
            END_DATE,
            CONTRACT_ITEM,
            CURRENCY,
            AMOUNT
        FROM SNOWFLAKE.BILLING_USAGE.CONTRACT_ITEMS
        """
        
        if customer_filter:
            query += f" WHERE SOLD_TO_CUSTOMER_NAME = '{customer_filter}'"
            
        query += " ORDER BY START_DATE DESC"
        
        df = session.sql(query).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error loading contract data: {str(e)}")
        return pd.DataFrame()

def create_usage_trend_chart(df):
    """Create usage trend chart"""
    if df.empty:
        return None
    
    daily_usage = df.groupby(['USAGE_DATE', 'USAGE_TYPE']).agg({
        'CREDITS_USED': 'sum',
        'USAGE_IN_CURRENCY': 'sum'
    }).reset_index()
    
    fig = px.line(daily_usage, 
                  x='USAGE_DATE', 
                  y='CREDITS_USED',
                  color='USAGE_TYPE',
                  title='Daily Credit Usage Trend by Usage Type',
                  labels={'CREDITS_USED': 'Credits Used', 'USAGE_DATE': 'Date'})
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_usage_breakdown_chart(df):
    """Create usage breakdown pie chart"""
    if df.empty:
        return None
    
    usage_by_type = df.groupby('USAGE_TYPE')['CREDITS_USED'].sum().reset_index()
    
    fig = px.pie(usage_by_type, 
                 values='CREDITS_USED', 
                 names='USAGE_TYPE',
                 title='Credit Usage Distribution by Type')
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_balance_chart(df):
    """Create balance overview chart"""
    if df.empty:
        return None
    
    # Get latest balance data
    latest_balance = df.loc[df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()]
    
    fig = go.Figure()
    
    customers = latest_balance['SOLD_TO_CUSTOMER_NAME'].tolist()
    
    fig.add_trace(go.Bar(
        name='Free Usage Balance',
        x=customers,
        y=latest_balance['FREE_USAGE_BALANCE'],
        marker_color='lightgreen'
    ))
    
    fig.add_trace(go.Bar(
        name='Capacity Balance',
        x=customers,
        y=latest_balance['CAPACITY_BALANCE'],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Rollover Balance',
        x=customers,
        y=latest_balance['ROLLOVER_BALANCE'],
        marker_color='orange'
    ))
    
    fig.update_layout(
        title='Current Balance Overview by Customer',
        barmode='stack',
        height=400,
        xaxis_title='Customer',
        yaxis_title='Balance Amount'
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">❄️ Snowflake Credit Usage Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Get Snowflake session
    session = get_snowflake_session()
    if not session:
        st.error("Unable to connect to Snowflake. Please check your connection.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    
    # Date range selection
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now().date()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
    
    # Customer filter
    customer_filter = st.sidebar.selectbox(
        "Select Customer (Optional)",
        options=[None, "All Customers"] + ["Customer A", "Customer B", "Customer C"],  # This would be dynamic in real implementation
        index=0
    )
    
    if customer_filter == "All Customers":
        customer_filter = None
    
    # Load data
    with st.spinner("Loading data..."):
        usage_df = load_usage_data(session, start_date, end_date, customer_filter)
        balance_df = load_balance_data(session, start_date, end_date, customer_filter)
        contract_df = load_contract_data(session, customer_filter)
    
    if usage_df.empty:
        st.warning("No usage data found for the selected criteria.")
        return
    
    # Key Metrics
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_credits = usage_df['CREDITS_USED'].sum()
        st.metric("Total Credits Used", f"{total_credits:,.2f}")
    
    with col2:
        total_cost = usage_df['USAGE_IN_CURRENCY'].sum()
        currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"
        st.metric("Total Cost", f"{total_cost:,.2f} {currency}")
    
    with col3:
        unique_customers = usage_df['SOLD_TO_CUSTOMER_NAME'].nunique()
        st.metric("Active Customers", unique_customers)
    
    with col4:
        avg_daily_usage = usage_df.groupby('USAGE_DATE')['CREDITS_USED'].sum().mean()
        st.metric("Avg Daily Credits", f"{avg_daily_usage:,.2f}")
    
    # Charts
    st.subheader("📈 Usage Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_chart = create_usage_trend_chart(usage_df)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
    
    with col2:
        breakdown_chart = create_usage_breakdown_chart(usage_df)
        if breakdown_chart:
            st.plotly_chart(breakdown_chart, use_container_width=True)
    
    # Balance Overview
    if not balance_df.empty:
        st.subheader("💰 Balance Overview")
        balance_chart = create_balance_chart(balance_df)
        if balance_chart:
            st.plotly_chart(balance_chart, use_container_width=True)
    
    # Detailed Tables
    st.subheader("📋 Detailed Usage Data")
    
    # Usage details
    with st.expander("Usage Details", expanded=False):
        if not usage_df.empty:
            st.dataframe(
                usage_df.sort_values('USAGE_DATE', ascending=False),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No usage data available.")
    
    # Balance details
    with st.expander("Balance Details", expanded=False):
        if not balance_df.empty:
            st.dataframe(
                balance_df.sort_values('BALANCE_DATE', ascending=False),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No balance data available.")
    
    # Contract details
    with st.expander("Contract Information", expanded=False):
        if not contract_df.empty:
            st.dataframe(
                contract_df.sort_values('START_DATE', ascending=False),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No contract data available.")
    
    # Export functionality
    st.subheader("📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not usage_df.empty:
            csv = usage_df.to_csv(index=False)
            st.download_button(
                label="Download Usage Data CSV",
                data=csv,
                file_name=f"usage_data_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
    
    with col2:
        if not balance_df.empty:
            csv = balance_df.to_csv(index=False)
            st.download_button(
                label="Download Balance Data CSV",
                data=csv,
                file_name=f"balance_data_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
    
    with col3:
        if not contract_df.empty:
            csv = contract_df.to_csv(index=False)
            st.download_button(
                label="Download Contract Data CSV",
                data=csv,
                file_name="contract_data.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("*Data refreshed every hour. For the most current information, please refresh the page.*")

if __name__ == "__main__":
    main() 