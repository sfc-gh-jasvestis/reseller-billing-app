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

# UI Messages — now served via TRANSLATIONS; kept as fallback reference
# Access via t('msg_no_data'), t('msg_loading'), etc.

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

# =============================================================================
# INTERNATIONALIZATION (i18n)
# =============================================================================

SUPPORTED_LANGUAGES = {"en": "English", "ja": "日本語"}
DEFAULT_LANGUAGE = "en"

TRANSLATIONS = {
    "en": {
        # App-level
        "app_title": "Snowflake Credit Usage Dashboard",
        "app_subtitle": "Real-time credit consumption monitoring for Snowflake reseller customers",
        "app_demo_banner": "🎭 **Demo Mode Active** - Displaying sample data for 5 fictional customers. Set `USE_DEMO_DATA = False` to use live BILLING schema data.",

        # Sidebar
        "sidebar_controls": "🎛️ Dashboard Controls",
        "sidebar_date_range": "📅 Quick Date Range",
        "sidebar_customer": "👥 Select Customer",
        "sidebar_refresh": "🔄 Refresh Data",
        "sidebar_refresh_note": "🕐 Data refreshed every hour. For the most current information, refresh the page.",
        "sidebar_loading_customers": "Loading customers...",

        # Date range labels
        "date_last_7": "Last 7 days",
        "date_last_30": "Last 30 days",
        "date_last_90": "Last 90 days",
        "date_current_month": "Current Month",
        "date_last_month": "Last Month",
        "date_custom": "Custom",
        "date_start": "Start Date",
        "date_end": "End Date",

        # All Customers label
        "all_customers": "All Customers",

        # Tab names
        "tab_trends": "📊 Trends",
        "tab_usage": "🎯 Usage Patterns",
        "tab_financial": "💰 Financial Health",
        "tab_feature": "🔬 Feature Adoption",

        # KPI metrics
        "kpi_header": "📊 Key Performance Indicators",
        "kpi_total_credits": "Total Credits Used",
        "kpi_total_cost": "Total Cost",
        "kpi_avg_daily": "Avg Daily Credits",
        "kpi_vs_last_week": "{value:+.1f}% vs last week",
        "kpi_balance_header": "### 💰 Balance Metrics",
        "kpi_total_balance": "Total Available Balance",
        "kpi_balance_help": "Capacity + Rollover — total credits available before on-demand charges apply",

        # Portfolio overview
        "portfolio_header": "📋 Portfolio Overview",
        "portfolio_customer": "Customer",
        "portfolio_credits": "Credits Used",
        "portfolio_cost": "Cost",
        "portfolio_balance": "Balance",
        "portfolio_depletion": "Days to Depletion",
        "portfolio_contract_used": "Contract Used",
        "portfolio_overage_days": "Days to Overage",
        "portfolio_ai": "AI/ML",
        "portfolio_risk": "Risk",
        "portfolio_depleted": "🔴 Depleted",
        "portfolio_critical": "🔴 Critical",
        "portfolio_watch": "🟡 Watch",
        "portfolio_healthy": "🟢 Healthy",
        "portfolio_risk_caption": "Risk: 🔴 Critical = near depletion/overage/expiry · 🟡 Watch = approaching a limit · 🟢 Healthy",

        # Alerts
        "alert_header": "🚨 Alerts & Insights",
        "alert_high_usage": "⚡ High daily credit usage: {avg_daily} credits/day average",
        "alert_usage_growth": "📈 Usage growth is high: +{rate}% over the last week",
        "alert_inactive": "😶 No usage in the last 7 days: {names}",
        "alert_no_ai": "🤖 Not using AI/Cortex features (upsell opportunity): {names}",
        "alert_depleted": "🔴 Balance fully depleted — customer(s) in overage: {names}",
        "alert_low_balance": "⚠️ {count} customer(s) have very low balance (<$1,000)",
        "alert_contract_expire_30": "🔔 Contract for **{name}** expires in {days} days — renewal conversation needed now",
        "alert_contract_expire_60": "🔔 Contract for **{name}** expires in {days} days — start renewal discussion",
        "alert_contract_expired": "🚨 Contract for **{name}** has expired ({days} days ago)",
        "alert_overage": "🔴 **{name}** is in overage — used {pct}% of contracted capacity",
        "alert_none": "✅ No alerts detected. All metrics are within normal ranges.",

        # Trends tab
        "trend_monthly_spend_customer": "Monthly spend by customer",
        "trend_monthly_spend_mom": "Monthly spend with MoM % change",
        "trend_detailed_data": "📋 Detailed Data",
        "trend_usage_details": "💻 Usage Details",
        "trend_no_usage": "No usage data available.",
        "trend_export_header": "📥 Export Data",
        "trend_export_usage": "📊 Download Usage Data",
        "trend_export_balance": "💰 Download Balance Data",

        # Usage Patterns tab
        "usage_credit_share": "Credit share by feature",
        "usage_credits_per_feature": "Credits consumed per feature",
        "usage_account_breakdown": "#### Account-Level Breakdown",
        "usage_credits_by_account": "Credits consumed by account",
        "usage_single_account": "Only one account detected — account-level breakdown not applicable.",

        # Financial Health tab
        "financial_projection_window": "Projection window",
        "financial_last_n_days": "Last {n} days",
        "financial_balance_header": "#### 💰 Balance & Run Rate",
        "financial_using_days": "Using last **{effective}** days of data (only {effective} days available — {requested}d window requested)",
        "financial_based_on": "Based on the last {days} days of consumption across the full contract period",
        "financial_daily_rate": "Daily Run Rate",
        "financial_weekly": "Weekly Projection",
        "financial_monthly": "Monthly Projection",
        "financial_depletion": "Days Until Depletion",
        "financial_depletion_zero": "Balance already depleted",
        "financial_depletion_na": "No balance data",
        "financial_export_run_rate": "⬇️ Download run rate data",
        "financial_contract_header": "#### 📋 Contract Status",
        "financial_no_contracts": "No active contracts found for the selected customer.",
        "financial_no_usage_contracts": "No usage data available for active contracts.",
        "financial_select_customer": "Select Customer to View",
        "financial_capacity": "Capacity Purchased",
        "financial_total_used": "Total Used",
        "financial_overage_label": "Overage",
        "financial_days_overage": "Days Until Overage",
        "financial_already_overage": "Already in overage",
        "financial_within_contract": "Within contract",
        "financial_sufficient": "Sufficient capacity",
        "financial_capacity_exhausted": "🔴 Capacity already exhausted — customer is in overage",
        "financial_projected_exhaust": "⚠️ Projected to exhaust capacity by {date}",
        "financial_not_enough_data": "Not enough data to generate the projection chart.",
        "financial_run_rate_label": "**Consumption Run Rate**",
        "financial_run_rate_note": "Avg daily × 365 · based on last {days}d",
        "financial_run_rate_warn": "Avg daily × 365\n\n⚠️ Only {actual}d of data available ({requested}d requested)",
        "financial_contract_details": "📄 Contract Details",
        "financial_timeline": "**Timeline**",
        "financial_projections": "**Projections**",
        "financial_start": "Start: {date}",
        "financial_end": "End: {date}",
        "financial_duration": "Duration: {days} days",
        "financial_elapsed": "Elapsed: {days} days",
        "financial_remaining": "Remaining: {days} days",
        "financial_daily": "Daily: {value}/day",
        "financial_weekly_proj": "Weekly: {value}/week",
        "financial_monthly_proj": "Monthly: {value}/month",
        "financial_annual": "Annual: {value}/year",
        "financial_window": "Window: last {days} days",
        "financial_loading_history": "Loading full contract history...",
        "financial_capacity_used_pct": "{pct:.1f}% of capacity",
        "financial_overage_caption": "Used % and Days Until Overage are calculated against Capacity Purchased. Rollover and other adjustments may differ slightly from Snowflake's billing portal.",

        # Feature Adoption tab
        "feature_header": "### 🔬 Feature Adoption",
        "feature_subtitle": "*Which Snowflake features are your customers using — and where are the upsell opportunities?*",
        "feature_no_data": "No usage data available for feature analysis.",
        "feature_matrix": "#### Adoption Matrix",
        "feature_matrix_caption": "Credits consumed per feature per customer — blank = not used in this period",
        "feature_breakdown": "#### Customer Feature Breakdown",
        "feature_select_customer": "Select a customer",
        "feature_showing": "Showing: **{name}**",
        "feature_upsell": "**Upsell opportunities**",
        "feature_upsell_scope_customer": "Features **{name}** hasn't used in this period — potential upsell conversations:",
        "feature_upsell_scope_all": "Features with **no usage across any customer** in this period:",
        "feature_all_used": "All tracked features are being used in this period.",
        "feature_datasource": "ℹ️ Data source & schema reference",
        "feature_usage_over_time": "Feature usage over time — {name}",

        # Chart labels
        "chart_credit_trend": "Credit Usage Trend",
        "chart_cost_trend": "Cost Trend",
        "chart_usage_cost_trends": "Usage and Cost Trends",
        "chart_heatmap_title": "Credit usage by day of week — weekends typically lower",
        "chart_axis_credits": "Credits",
        "chart_axis_cost": "Cost",
        "chart_axis_date": "Date",
        "chart_axis_cost_usd": "Cost (USD)",
        "chart_consumption": "Consumption ({currency})",
        "chart_cumulative": "Cumulative Consumption",
        "chart_actual": "Actual",
        "chart_prediction": "Prediction",
        "chart_cumulative_consump": "Cumulative Consump",
        "chart_capacity_contract": "Capacity Contract Amt",
        "chart_monthly_cost": "Monthly Cost",

        # FEATURE_USECASES translations
        "usecase_cortex": "Build AI-powered apps, summarize documents, classify data, and generate content — no ML expertise or external tools needed",
        "usecase_ml_functions": "Built-in forecasting and anomaly detection — spot trends and outliers in any dataset without a data science team",
        "usecase_snowpark": "Run Python, Java, or Scala transformations and ML workloads natively inside Snowflake — no data movement, no Spark clusters",
        "usecase_search_optimization": "Dramatically speed up point-lookup queries on large tables — ideal for interactive apps, dashboards, and API backends",
        "usecase_snowpipe": "Replace scheduled batch loads with continuous, automated data ingestion — data is always fresh when you need it",
        "usecase_streams": "Track every INSERT, UPDATE, and DELETE on any table and build event-driven, incremental pipelines using Change Data Capture",
        "usecase_serverless_tasks": "One of Snowflake's most-adopted features — automate and orchestrate data pipelines on a schedule without managing any compute",
        "usecase_dynamic_tables": "Declare the result you want; Snowflake works out when and how to refresh it — the modern alternative to complex ETL pipelines",
        "usecase_automatic_clustering": "Keep large tables fast as data grows without any manual tuning — queries stay performant automatically",
        "usecase_materialized_views": "Pre-compute and cache the results of expensive queries — near-instant load times for dashboards and repeated analytical workloads",
        "usecase_streamlit": "Build and share interactive data apps and dashboards natively inside Snowflake — no external hosting, no data copies",
        "usecase_cortex_analyst": "Ask questions about your data in plain English and get SQL-backed answers instantly — self-service analytics for everyone",
        "usecase_cortex_search": "Add semantic search to any application — returns relevant results even when the exact keywords don't match",
        "usecase_cortex_code": "AI-assisted SQL and Python generation inside Snowflake — write, explain, and debug code faster",
        "usecase_snowflake_intelligence": "Snowflake's unified AI layer — combine conversational analytics, intelligent search, and automated agents in one place",
        "usecase_default": "Explore this feature with your customer.",

        # Messages (replaces MESSAGES dict)
        "msg_no_data": "No data found for the selected criteria.",
        "msg_loading": "Loading data...",
        "msg_connection_error": "Unable to connect to Snowflake. Please check your connection.",
        "msg_permission_error": "Access denied. Please check your permissions for the BILLING schema.",
        "msg_data_refresh": "Data refreshed every hour. For the most current information, please refresh the page.",
        "msg_date_range_long": "Date range is longer than 1 year. This may result in slower performance.",
        "msg_date_invalid": "Start date must be before end date.",
        "msg_adjust_filters": "💡 Try adjusting your filters or date range to find available data.",
        "msg_demo_fallback": "ℹ️ Live billing data is unavailable — displaying demo data.",
        "msg_auth_expired": "🔐 **Authentication token has expired**",
        "msg_auth_reconnect": "To reconnect, please try one of the following:\n1. **Refresh the browser page** - this will prompt for re-authentication\n2. **Run in terminal**: `snow connection test` to refresh your connection\n3. **Re-authenticate via SSO** if using federated authentication",
        "msg_retry": "🔄 Retry Connection",

        # Footer
        "footer_data_range": "Data Range: {start} to {end}",
        "footer_total_records": "Total Records: {count}",
    },
    "ja": {
        # App-level
        "app_title": "Snowflake クレジット使用量ダッシュボード",
        "app_subtitle": "Snowflake 再販顧客 クレジット消費リアルタイムモニタリング",
        "app_demo_banner": "🎭 **デモモード** — 5社の架空顧客のサンプルデータを表示中。実データを使用するには `USE_DEMO_DATA = False` に設定してください。",

        # Sidebar
        "sidebar_controls": "🎛️ ダッシュボード設定",
        "sidebar_date_range": "📅 期間選択",
        "sidebar_customer": "👥 顧客を選択",
        "sidebar_refresh": "🔄 データ更新",
        "sidebar_refresh_note": "🕐 データは1時間ごとに更新されます。最新情報を取得するにはページを更新してください。",
        "sidebar_loading_customers": "顧客を読み込み中...",

        # Date range labels
        "date_last_7": "過去7日間",
        "date_last_30": "過去30日間",
        "date_last_90": "過去90日間",
        "date_current_month": "今月",
        "date_last_month": "先月",
        "date_custom": "カスタム",
        "date_start": "開始日",
        "date_end": "終了日",

        # All Customers label
        "all_customers": "全顧客",

        # Tab names
        "tab_trends": "📊 トレンド",
        "tab_usage": "🎯 使用パターン",
        "tab_financial": "💰 財務状況",
        "tab_feature": "🔬 機能採用状況",

        # KPI metrics
        "kpi_header": "📊 主要指標",
        "kpi_total_credits": "総クレジット使用量",
        "kpi_total_cost": "総コスト",
        "kpi_avg_daily": "1日当たり平均消費クレジット",
        "kpi_vs_last_week": "前週比 {value:+.1f}%",
        "kpi_balance_header": "### 💰 残高メトリクス",
        "kpi_total_balance": "利用可能残高合計",
        "kpi_balance_help": "キャパシティ + ロールオーバー — オンデマンド課金前の利用可能クレジット合計",

        # Portfolio overview
        "portfolio_header": "📋 ポートフォリオ概要",
        "portfolio_customer": "顧客",
        "portfolio_credits": "クレジット使用量",
        "portfolio_cost": "コスト",
        "portfolio_balance": "残高",
        "portfolio_depletion": "残高枯渇日数",
        "portfolio_contract_used": "契約消費率",
        "portfolio_overage_days": "超過日数",
        "portfolio_ai": "AI/ML",
        "portfolio_risk": "リスク",
        "portfolio_depleted": "🔴 枯渇",
        "portfolio_critical": "🔴 危険",
        "portfolio_watch": "🟡 注意",
        "portfolio_healthy": "🟢 正常",
        "portfolio_risk_caption": "リスク: 🔴 危険 = 枯渇/超過/期限切れ間近 · 🟡 注意 = 閾値に接近中 · 🟢 正常",

        # Alerts
        "alert_header": "🚨 アラート & インサイト",
        "alert_high_usage": "⚡ 高い日次クレジット使用量: 平均 {avg_daily} クレジット/日",
        "alert_usage_growth": "📈 使用量が急増: 前週比 +{rate}%",
        "alert_inactive": "😶 過去7日間使用なし: {names}",
        "alert_no_ai": "🤖 AI/Cortex機能未使用（アップセル機会）: {names}",
        "alert_depleted": "🔴 残高完全枯渇 — 超過中の顧客: {names}",
        "alert_low_balance": "⚠️ {count} 社の残高が非常に少ない（<$1,000）",
        "alert_contract_expire_30": "🔔 **{name}** の契約が {days} 日後に期限切れ — 今すぐ更新の相談が必要",
        "alert_contract_expire_60": "🔔 **{name}** の契約が {days} 日後に期限切れ — 更新の検討を開始",
        "alert_contract_expired": "🚨 **{name}** の契約が期限切れ（{days} 日前）",
        "alert_overage": "🔴 **{name}** が超過中 — 契約キャパシティの {pct}% を消費",
        "alert_none": "✅ アラートなし。すべての指標が正常範囲内です。",

        # Trends tab
        "trend_monthly_spend_customer": "顧客別月次コスト",
        "trend_monthly_spend_mom": "月次コスト（前月比%変動付き）",
        "trend_detailed_data": "📋 詳細データ",
        "trend_usage_details": "💻 使用量詳細",
        "trend_no_usage": "使用量データがありません。",
        "trend_export_header": "📥 データエクスポート",
        "trend_export_usage": "📊 使用量データをダウンロード",
        "trend_export_balance": "💰 残高データをダウンロード",

        # Usage Patterns tab
        "usage_credit_share": "機能別クレジットシェア",
        "usage_credits_per_feature": "機能別クレジット消費量",
        "usage_account_breakdown": "#### アカウント別内訳",
        "usage_credits_by_account": "アカウント別クレジット消費量",
        "usage_single_account": "アカウントが1つのみのため、アカウント別内訳は該当しません。",

        # Financial Health tab
        "financial_projection_window": "予測ウィンドウ",
        "financial_last_n_days": "過去 {n} 日間",
        "financial_balance_header": "#### 💰 残高 & ランレート",
        "financial_using_days": "直近 **{effective}** 日間のデータを使用（{effective} 日分のみ利用可能 — {requested}日間を要求）",
        "financial_based_on": "契約期間全体の直近 {days} 日間の消費量に基づく",
        "financial_daily_rate": "日次ランレート",
        "financial_weekly": "週次予測",
        "financial_monthly": "月次予測",
        "financial_depletion": "残高が枯渇するまでの日数",
        "financial_depletion_zero": "残高は既に枯渇",
        "financial_depletion_na": "残高データなし",
        "financial_export_run_rate": "⬇️ ランレートデータをダウンロード",
        "financial_contract_header": "#### 📋 契約ステータス",
        "financial_no_contracts": "選択した顧客のアクティブな契約が見つかりません。",
        "financial_no_usage_contracts": "アクティブな契約の使用量データがありません。",
        "financial_select_customer": "表示する顧客を選択",
        "financial_capacity": "購入キャパシティ",
        "financial_total_used": "総使用量",
        "financial_overage_label": "超過",
        "financial_days_overage": "超過日数",
        "financial_already_overage": "既に超過中",
        "financial_within_contract": "契約範囲内",
        "financial_sufficient": "十分なキャパシティ",
        "financial_capacity_exhausted": "🔴 キャパシティは既に枯渇 — 顧客は超過中",
        "financial_projected_exhaust": "⚠️ {date} までにキャパシティ枯渇の見込み",
        "financial_not_enough_data": "予測チャートを生成するのに十分なデータがありません。",
        "financial_run_rate_label": "**消費ランレート**",
        "financial_run_rate_note": "日平均 × 365 · 直近 {days} 日間に基づく",
        "financial_run_rate_warn": "日平均 × 365\n\n⚠️ {actual} 日分のデータのみ利用可能（{requested} 日間を要求）",
        "financial_contract_details": "📄 契約詳細",
        "financial_timeline": "**タイムライン**",
        "financial_projections": "**予測**",
        "financial_start": "開始: {date}",
        "financial_end": "終了: {date}",
        "financial_duration": "期間: {days} 日",
        "financial_elapsed": "経過: {days} 日",
        "financial_remaining": "残り: {days} 日",
        "financial_daily": "日次: {value}/日",
        "financial_weekly_proj": "週次: {value}/週",
        "financial_monthly_proj": "月次: {value}/月",
        "financial_annual": "年次: {value}/年",
        "financial_window": "ウィンドウ: 直近 {days} 日間",
        "financial_loading_history": "契約履歴全体を読み込み中...",
        "financial_capacity_used_pct": "キャパシティの {pct:.1f}%",
        "financial_overage_caption": "消費率と超過日数は購入キャパシティに対して計算されます。ロールオーバー等の調整によりSnowflakeの請求ポータルとは若干異なる場合があります。",

        # Feature Adoption tab
        "feature_header": "### 🔬 機能採用状況",
        "feature_subtitle": "*顧客が使用しているSnowflake機能とアップセル機会は？*",
        "feature_no_data": "機能分析に使用できるデータがありません。",
        "feature_matrix": "#### 機能採用状況マトリクス",
        "feature_matrix_caption": "顧客×機能別クレジット消費量 — 空欄 = 当期間中未使用",
        "feature_breakdown": "#### 顧客別機能内訳",
        "feature_select_customer": "顧客を選択",
        "feature_showing": "表示中: **{name}**",
        "feature_upsell": "**アップセル機会**",
        "feature_upsell_scope_customer": "**{name}** が当期間中に使用していない機能 — アップセルの候補:",
        "feature_upsell_scope_all": "当期間中に**全顧客で使用されていない**機能:",
        "feature_all_used": "追跡対象の全機能が当期間中に使用されています。",
        "feature_datasource": "ℹ️ データソース & スキーマリファレンス",
        "feature_usage_over_time": "機能別使用量推移 — {name}",

        # Chart labels
        "chart_credit_trend": "クレジット使用量トレンド",
        "chart_cost_trend": "コストトレンド",
        "chart_usage_cost_trends": "使用量とコストのトレンド",
        "chart_heatmap_title": "曜日別クレジット使用量 — 週末は通常低下",
        "chart_axis_credits": "クレジット",
        "chart_axis_cost": "コスト",
        "chart_axis_date": "日付",
        "chart_axis_cost_usd": "コスト (USD)",
        "chart_consumption": "消費量 ({currency})",
        "chart_cumulative": "累積消費量",
        "chart_actual": "実績",
        "chart_prediction": "予測",
        "chart_cumulative_consump": "累積消費量",
        "chart_capacity_contract": "契約キャパシティ",
        "chart_monthly_cost": "月次コスト",

        # FEATURE_USECASES translations
        "usecase_cortex": "AIアプリの構築、文書要約、データ分類、コンテンツ生成 — ML専門知識や外部ツール不要",
        "usecase_ml_functions": "組み込みの予測・異常検知 — データサイエンスチームなしでトレンドや外れ値を発見",
        "usecase_snowpark": "Python/Java/Scala変換やMLワークロードをSnowflake内でネイティブ実行 — データ移動不要、Sparkクラスタ不要",
        "usecase_search_optimization": "大規模テーブルのポイントルックアップクエリを劇的に高速化 — インタラクティブアプリ、ダッシュボード、APIバックエンドに最適",
        "usecase_snowpipe": "スケジュールバッチをリアルタイムの自動データ取り込みに置換 — 必要な時にデータは常に最新",
        "usecase_streams": "テーブルの全INSERT/UPDATE/DELETEを追跡し、CDCによるイベント駆動型増分パイプラインを構築",
        "usecase_serverless_tasks": "Snowflakeで最も採用されている機能の一つ — コンピュート管理不要でデータパイプラインを自動化・オーケストレーション",
        "usecase_dynamic_tables": "求める結果を宣言するだけ — Snowflakeが更新タイミングと方法を自動決定。複雑なETLパイプラインの代替",
        "usecase_automatic_clustering": "データ増加に伴う大規模テーブルの性能を手動チューニングなしで維持 — クエリは自動的に高速を保持",
        "usecase_materialized_views": "高コストクエリの結果を事前計算・キャッシュ — ダッシュボードや反復分析ワークロードの読み込みをほぼ瞬時に",
        "usecase_streamlit": "Snowflake内でインタラクティブなデータアプリとダッシュボードをネイティブに構築・共有 — 外部ホスティングやデータコピー不要",
        "usecase_cortex_analyst": "自然言語でデータに質問し、SQLベースの回答を即座に取得 — 全員がセルフサービス分析を利用可能",
        "usecase_cortex_search": "アプリケーションにセマンティック検索を追加 — キーワードが完全一致しなくても関連結果を返却",
        "usecase_cortex_code": "Snowflake内でAI支援によるSQL/Python生成 — コードの作成、説明、デバッグを高速化",
        "usecase_snowflake_intelligence": "Snowflakeの統合AIレイヤー — 対話型分析、インテリジェント検索、自動エージェントを一元化",
        "usecase_default": "この機能を顧客と一緒に検討してみましょう。",

        # Messages
        "msg_no_data": "選択した条件に該当するデータが見つかりません。",
        "msg_loading": "データを読み込み中...",
        "msg_connection_error": "Snowflakeに接続できません。接続設定を確認してください。",
        "msg_permission_error": "アクセスが拒否されました。BILLINGスキーマの権限を確認してください。",
        "msg_data_refresh": "データは1時間ごとに更新されます。最新情報を取得するにはページを更新してください。",
        "msg_date_range_long": "期間が1年を超えています。パフォーマンスが低下する可能性があります。",
        "msg_date_invalid": "開始日は終了日より前でなければなりません。",
        "msg_adjust_filters": "💡 フィルターや期間を変更してデータを検索してみてください。",
        "msg_demo_fallback": "ℹ️ ライブ請求データが利用できないため、デモデータを表示しています。",
        "msg_auth_expired": "🔐 **認証トークンが期限切れです**",
        "msg_auth_reconnect": "再接続するには、以下をお試しください:\n1. **ブラウザページを更新** — 再認証が求められます\n2. **ターミナルで実行**: `snow connection test` で接続を更新\n3. **SSO再認証**（フェデレーション認証を使用している場合）",
        "msg_retry": "🔄 再接続",

        # Footer
        "footer_data_range": "データ範囲: {start} ～ {end}",
        "footer_total_records": "総レコード数: {count}",
    },
}


def t(key, **kwargs):
    """Return translated text for the current language. Falls back to English."""
    lang = st.session_state.get("language", DEFAULT_LANGUAGE)
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key)
    if text is None:
        text = TRANSLATIONS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def t_usecase(feature_key):
    """Return translated use-case description for a feature."""
    normalized = feature_key.replace(" ", "_")
    lang = st.session_state.get("language", DEFAULT_LANGUAGE)
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(f"usecase_{normalized}")
    if text is None:
        text = FEATURE_USECASES.get(feature_key, t("usecase_default"))
    return text


# Demo mode flag - auto-detects via env var, defaults to True outside Snowflake
import os
USE_DEMO_DATA = os.environ.get("USE_DEMO_DATA", "true").lower() != "false"

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
    return [t("all_customers")] + [c['name'] for c in DEMO_CUSTOMERS]

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
        t("date_last_7"): (today - timedelta(days=7), today),
        t("date_last_30"): (today - timedelta(days=30), today),
        t("date_last_90"): (today - timedelta(days=90), today),
        t("date_current_month"): (today.replace(day=1), today),
        t("date_last_month"): get_last_month_range(),
        t("date_custom"): None
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
        st.error(t("msg_date_invalid"))
        return False
    
    if (end_date - start_date).days > 365:
        st.warning(t("msg_date_range_long"))
    
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
    
    # Aggregate by customer
    run_rate_data = recent_usage.groupby('SOLD_TO_CUSTOMER_NAME').agg({
        'CREDITS_USED': 'sum',
        'USAGE_IN_CURRENCY': ['sum', lambda x: x.iloc[0] if len(x) > 0 else 'USD'],
        'USAGE_DATE': ['min', 'max']
    }).reset_index()
    
    # Flatten column names
    run_rate_data.columns = ['CUSTOMER', 'TOTAL_CREDITS', 'TOTAL_COST', 'CURRENCY', 'START_DATE', 'END_DATE']
    
    # Calculate actual days per customer (not a shared global value)
    # Using each customer's own date range avoids underestimating customers
    # that joined mid-window or have sparse data
    run_rate_data['ACTUAL_DAYS'] = run_rate_data.apply(
        lambda row: max((row['END_DATE'] - row['START_DATE']).days + 1, 1), axis=1
    )
    
    # Calculate daily run rate
    run_rate_data['DAILY_RUN_RATE_CREDITS'] = run_rate_data['TOTAL_CREDITS'] / run_rate_data['ACTUAL_DAYS']
    run_rate_data['DAILY_RUN_RATE_COST'] = run_rate_data['TOTAL_COST'] / run_rate_data['ACTUAL_DAYS']
    
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
    run_rate_data['RUN_RATE_PERIOD_DAYS'] = run_rate_days
    
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
    
    actual_days = max((max_date - recent_usage['USAGE_DATE'].min()).days + 1, 1)
    
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
            actual_days = max((max_date - recent_usage['USAGE_DATE'].min()).days + 1, 1)
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
        
        # Prediction from today — extend at least 90 days forward so the
        # slope change is always visible, even when the contract end is near
        # or already past (customer is in overage)
        current_cumulative = customer_usage['CUMULATIVE_USAGE'].iloc[-1] if not customer_usage.empty else 0
        prediction_end = max(contract_end, today + timedelta(days=90))
        prediction_dates = pd.date_range(start=today, end=prediction_end, freq='D')
        
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
                name=t('chart_actual'),
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
                name=t('chart_prediction'),
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
                name=t('chart_cumulative_consump'),
                line=dict(color='#00D4AA', width=2.5),
                mode='lines',
                legendgroup='cumulative'
            ),
            secondary_y=True
        )
        
        # Add capacity contract amount line (gray horizontal) - right y-axis
        # Extend to prediction_end so it stays visible across the full chart window
        fig.add_trace(
            go.Scatter(
                x=[contract_start, prediction_end],
                y=[metrics['capacity_purchased'], metrics['capacity_purchased']],
                name=t('chart_capacity_contract'),
                line=dict(color='#FFD166', width=2.5, dash='dash'),
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
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text=t("chart_consumption", currency=metrics['currency']),
            secondary_y=False,
            gridcolor='rgba(128,128,128,0.3)',
            tickformat="$,.0f"
        )
        fig.update_yaxes(
            title_text=t("chart_cumulative"),
            secondary_y=True,
            gridcolor='rgba(128,128,128,0.3)',
            tickformat="$,.0f"
        )
        
        # Update x-axis
        fig.update_xaxes(
            tickformat="%m/%d/%Y",
            tickangle=45,
            gridcolor='rgba(128,128,128,0.3)',
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
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: 0.25rem;
    }
    .alert-warning {
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: 0.25rem;
    }
    @media (prefers-color-scheme: light) {
        .alert-success {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        .alert-warning {
            background-color: #fff3cd;
            border-color: #ffeaa7;
            color: #856404;
        }
    }
    @media (prefers-color-scheme: dark) {
        .alert-success {
            background-color: rgba(40, 167, 69, 0.2);
            border-color: rgba(40, 167, 69, 0.4);
            color: #81C784;
        }
        .alert-warning {
            background-color: rgba(255, 193, 7, 0.15);
            border-color: rgba(255, 193, 7, 0.3);
            color: #FFD54F;
        }
    }
    .sidebar .sidebar-content {
    }
    .stSelectbox > div > div {
        border-radius: 5px;
    }
    /* Fix sidebar text visibility for both light and dark mode */
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: rgba(255, 255, 255, 0.9) !important;
        }
        [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
            color: rgba(255, 255, 255, 0.9) !important;
        }
    }
    @media (prefers-color-scheme: light) {
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: rgba(0, 0, 0, 0.85) !important;
        }
        [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
            color: rgba(0, 0, 0, 0.85) !important;
        }
    }
    /* Upsell cards — light/dark adaptive */
    .upsell-card {
        padding: 0.8rem 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 0.75rem;
    }
    @media (prefers-color-scheme: light) {
        .upsell-card {
            background: #fff3cd;
        }
        .upsell-card-title {
            color: #333333;
            font-size: 1rem;
        }
        .upsell-card-desc {
            color: #555555;
            font-size: 0.85rem;
            line-height: 1.4;
        }
    }
    @media (prefers-color-scheme: dark) {
        .upsell-card {
            background: rgba(255, 193, 7, 0.15);
        }
        .upsell-card-title {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1rem;
        }
        .upsell-card-desc {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.85rem;
            line-height: 1.4;
        }
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
        st.error(f"❌ {t('msg_connection_error')}\nDetails: {str(e)}")
        return None

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_usage_data(_session, start_date, end_date, customer_filter=None, usage_type_filter=None):
    """Enhanced usage data loading with additional filters - falls back to demo data"""
    # Use demo data if flag is set
    if USE_DEMO_DATA:
        df = generate_demo_usage_data(start_date, end_date)
        if customer_filter and customer_filter != t("all_customers"):
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
        
        if customer_filter and customer_filter != t("all_customers"):
            safe_customer = customer_filter.replace("'", "''")
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{safe_customer}'"

        if usage_type_filter:
            usage_types = "', '".join(usage_type_filter)
            query += f" AND USAGE_TYPE IN ('{usage_types}')"
            
        query += f" ORDER BY USAGE_DATE DESC, SOLD_TO_CUSTOMER_NAME LIMIT {QUERY_LIMITS['max_rows']}"
        
        df = _session.sql(query).to_pandas()
        return clean_usage_data(df)
        
    except Exception as e:
        st.info(t("msg_demo_fallback"))
        df = generate_demo_usage_data(start_date, end_date)
        if customer_filter and customer_filter != t("all_customers"):
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
        if customer_filter and customer_filter != t("all_customers"):
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
        
        if customer_filter and customer_filter != t("all_customers"):
            safe_customer = customer_filter.replace("'", "''")
            query += f" AND SOLD_TO_CUSTOMER_NAME = '{safe_customer}'"

        query += " ORDER BY DATE DESC, SOLD_TO_CUSTOMER_NAME"
        
        df = _session.sql(query).to_pandas()
        return clean_balance_data(df)
        
    except Exception as e:
        df = generate_demo_balance_data(start_date, end_date)
        if customer_filter and customer_filter != t("all_customers"):
            df = df[df['SOLD_TO_CUSTOMER_NAME'] == customer_filter]
        return clean_balance_data(df)

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_contract_data(_session, customer_filter=None):
    """Load contract data from PARTNER_CONTRACT_ITEMS - falls back to demo data"""
    # Use demo data if flag is set
    if USE_DEMO_DATA:
        df = generate_demo_contract_data()
        if customer_filter and customer_filter != t("all_customers"):
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
        
        if customer_filter and customer_filter != t("all_customers"):
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
        if customer_filter and customer_filter != t("all_customers"):
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
        return [t("all_customers")] + df['SOLD_TO_CUSTOMER_NAME'].tolist()
        
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
        subplot_titles=(t('chart_credit_trend'), t('chart_cost_trend')),
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
    
    fig.update_xaxes(title_text=t("chart_axis_date"), row=2, col=1)
    fig.update_yaxes(title_text=t("chart_axis_credits"), row=1, col=1)
    fig.update_yaxes(title_text=t("chart_axis_cost"), row=2, col=1)
    
    fig.update_layout(
        height=600,
        title=t("chart_usage_cost_trends"),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.3)')
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.3)')
    
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
        yaxis_tickformat='$,.0f',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.3)')
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.3)')
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
        color_continuous_scale="Viridis",
        aspect="auto",
        labels=dict(x="", y="Week of", color="Credits")
    )
    fig.update_layout(
        title=t("chart_heatmap_title"),
        xaxis_title="",
        yaxis_title="",
        height=min(480, max(220, len(heatmap_pivot) * 38 + 100)),
        coloraxis_colorbar=dict(title="Credits", thickness=12, len=0.7),
        margin=dict(l=10, r=20, t=40, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(side="top")
    return fig

def show_alerts_and_insights(usage_df, balance_df, contract_df=None):
    """Display intelligent alerts and insights"""
    st.subheader(t("alert_header"))

    alerts = []
    today = datetime.now().date()
    ai_features = {'cortex', 'cortex analyst', 'cortex search', 'cortex code',
                   'ml functions', 'snowflake intelligence'}

    if not usage_df.empty:
        all_customers = set(usage_df['SOLD_TO_CUSTOMER_NAME'].unique())

        # High usage alert
        avg_daily = usage_df.groupby('USAGE_DATE')['CREDITS_USED'].sum().mean()
        if avg_daily > 1000:
            alerts.append({'type': 'warning',
                'message': t("alert_high_usage", avg_daily=f"{avg_daily:,.0f}")})

        # Usage growth alert
        growth_rate = calculate_growth_rate(usage_df, 'CREDITS_USED', 'USAGE_DATE')
        if growth_rate > 50:
            alerts.append({'type': 'warning',
                'message': t("alert_usage_growth", rate=growth_rate)})

        # Zero usage in last 7 days — potential churn risk
        cutoff_7 = usage_df['USAGE_DATE'].max() - timedelta(days=7)
        active_7d = set(usage_df[usage_df['USAGE_DATE'] > cutoff_7]['SOLD_TO_CUSTOMER_NAME'].unique())
        inactive = sorted(all_customers - active_7d)
        if inactive:
            names = ", ".join(inactive)
            alerts.append({'type': 'warning',
                'message': t("alert_inactive", names=names)})

        # No AI / Cortex usage — upsell signal
        ai_users = set(
            usage_df[usage_df['USAGE_TYPE'].str.lower().isin(ai_features)]['SOLD_TO_CUSTOMER_NAME'].unique()
        )
        non_ai = sorted(all_customers - ai_users)
        if non_ai:
            names = ", ".join(non_ai)
            alerts.append({'type': 'info',
                'message': t("alert_no_ai", names=names)})

    if not balance_df.empty:
        latest_balances = balance_df.loc[
            balance_df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()
        ]
        # Depleted balance
        depleted = latest_balances[latest_balances['TOTAL_BALANCE'] <= 0]
        if not depleted.empty:
            names = ", ".join(depleted['SOLD_TO_CUSTOMER_NAME'].tolist())
            alerts.append({'type': 'error',
                'message': t("alert_depleted", names=names)})
        # Low balance
        low_bal = latest_balances[
            (latest_balances['TOTAL_BALANCE'] > 0) & (latest_balances['TOTAL_BALANCE'] < 1000)
        ]
        if not low_bal.empty:
            alerts.append({'type': 'warning',
                'message': t("alert_low_balance", count=len(low_bal))})

    if contract_df is not None and not contract_df.empty:
        for _, row in contract_df.iterrows():
            days_left = (row['END_DATE'] - today).days
            cname = row['SOLD_TO_CUSTOMER_NAME']
            # Contract ending soon
            if 0 < days_left <= 30:
                alerts.append({'type': 'error',
                    'message': t("alert_contract_expire_30", name=cname, days=days_left)})
            elif 0 < days_left <= 60:
                alerts.append({'type': 'warning',
                    'message': t("alert_contract_expire_60", name=cname, days=days_left)})
            # Already past contract end
            elif days_left <= 0:
                alerts.append({'type': 'error',
                    'message': t("alert_contract_expired", name=cname, days=abs(days_left))})

        # Check for overage (usage > capacity)
        if not usage_df.empty:
            for _, row in contract_df.iterrows():
                cname = row['SOLD_TO_CUSTOMER_NAME']
                cust_used = usage_df[
                    (usage_df['SOLD_TO_CUSTOMER_NAME'] == cname) &
                    (usage_df['USAGE_DATE'] >= row['START_DATE']) &
                    (usage_df['USAGE_DATE'] <= row['END_DATE'])
                ]['USAGE_IN_CURRENCY'].sum()
                if cust_used > row['AMOUNT'] and row['AMOUNT'] > 0:
                    pct = cust_used / row['AMOUNT'] * 100
                    alerts.append({'type': 'error',
                        'message': t("alert_overage", name=cname, pct=f"{pct:.0f}")})

    # Display
    if alerts:
        # Sort: errors first, then warnings, then info
        order = {'error': 0, 'warning': 1, 'info': 2, 'success': 3}
        alerts.sort(key=lambda a: order.get(a['type'], 9))
        for alert in alerts:
            css = {'error': 'alert-warning', 'warning': 'alert-warning',
                   'info': 'alert-info', 'success': 'alert-success'}.get(alert['type'], 'alert-info')
            st.markdown(f'<div class="{css}">{alert["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-success">{t("alert_none")}</div>',
                    unsafe_allow_html=True)

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
            t("kpi_total_credits"),
            format_credits(summary['total_credits']),
            delta=t("kpi_vs_last_week", value=growth_rate) if growth_rate != 0 else None
        )
    
    with col2:
        cost_growth = calculate_growth_rate(usage_df, 'USAGE_IN_CURRENCY', 'USAGE_DATE')
        st.metric(
            t("kpi_total_cost"),
            format_currency(summary['total_cost'], currency),
            delta=t("kpi_vs_last_week", value=cost_growth) if cost_growth != 0 else None
        )
    
    with col3:
        st.metric(
            t("kpi_avg_daily"),
            format_credits(summary['avg_daily_credits']),
            delta=None
        )
    
    # Additional balance metrics if available
    if not balance_df.empty:
        balance_summary = get_balance_summary(balance_df)
        
        st.markdown(t("kpi_balance_header"))
        total_balance = (
            balance_summary['total_free_usage'] +
            balance_summary['total_capacity'] +
            balance_summary['total_rollover']
        )
        col1, _ = st.columns([1, 3])
        with col1:
            st.metric(
                t("kpi_total_balance"),
                format_currency(total_balance, currency),
                help=t("kpi_balance_help")
            )

def show_portfolio_summary(usage_df, balance_df, contract_df):
    """One-row-per-customer portfolio health table for the All Customers view."""
    st.subheader(t("portfolio_header"))
    today = datetime.now().date()
    ai_features = {'cortex', 'cortex analyst', 'cortex search', 'cortex code',
                   'ml functions', 'snowflake intelligence'}

    customers = sorted(usage_df['SOLD_TO_CUSTOMER_NAME'].unique())
    currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"

    # Latest balances lookup
    bal_lookup = {}
    if not balance_df.empty:
        latest = balance_df.loc[balance_df.groupby('SOLD_TO_CUSTOMER_NAME')['BALANCE_DATE'].idxmax()]
        bal_lookup = latest.set_index('SOLD_TO_CUSTOMER_NAME')['TOTAL_BALANCE'].to_dict()

    # Contract lookup: capacity and end date per customer
    contract_lookup = {}
    if contract_df is not None and not contract_df.empty:
        for _, row in contract_df.iterrows():
            contract_lookup[row['SOLD_TO_CUSTOMER_NAME']] = {
                'capacity': row['AMOUNT'], 'end': row['END_DATE'], 'start': row['START_DATE']
            }

    rows = []
    for cust in customers:
        cdf = usage_df[usage_df['SOLD_TO_CUSTOMER_NAME'] == cust]
        credits = cdf['CREDITS_USED'].sum()
        cost = cdf['USAGE_IN_CURRENCY'].sum()

        # Daily rate from last 30 days
        max_date = cdf['USAGE_DATE'].max()
        cutoff = max_date - timedelta(days=30)
        recent = cdf[cdf['USAGE_DATE'] > cutoff]
        actual_days = max((max_date - recent['USAGE_DATE'].min()).days + 1, 1) if not recent.empty else 1
        daily_cost = recent['USAGE_IN_CURRENCY'].sum() / actual_days if not recent.empty else 0

        # Balance and days to depletion
        balance = bal_lookup.get(cust, 0)
        days_depletion = int(balance / daily_cost) if daily_cost > 0 and balance > 0 else None

        # Contract metrics
        ci = contract_lookup.get(cust)
        used_pct = None
        days_overage = None
        if ci:
            contract_used = usage_df[
                (usage_df['SOLD_TO_CUSTOMER_NAME'] == cust) &
                (usage_df['USAGE_DATE'] >= ci['start']) &
                (usage_df['USAGE_DATE'] <= ci['end'])
            ]['USAGE_IN_CURRENCY'].sum()
            used_pct = contract_used / ci['capacity'] * 100 if ci['capacity'] > 0 else 0
            remaining_cap = ci['capacity'] - contract_used
            if remaining_cap <= 0:
                days_overage = 0
            elif daily_cost > 0:
                days_overage = int(remaining_cap / daily_cost)
            else:
                days_overage = (ci['end'] - today).days

        # AI usage flag
        uses_ai = cdf['USAGE_TYPE'].str.lower().isin(ai_features).any()

        # Risk score
        risk_factors = 0
        if balance <= 0:  # Balance fully depleted — always critical
            risk_factors += 3
        elif days_depletion is not None and days_depletion < 30:
            risk_factors += 2
        elif days_depletion is not None and days_depletion < 90:
            risk_factors += 1
        if days_overage is not None and days_overage < 30: risk_factors += 2
        elif days_overage is not None and days_overage < 60: risk_factors += 1
        if ci and (ci['end'] - today).days < 60: risk_factors += 1
        risk = t("portfolio_critical") if risk_factors >= 3 else t("portfolio_watch") if risk_factors >= 1 else t("portfolio_healthy")

        rows.append({
            t('portfolio_customer'): cust,
            t('portfolio_credits'): format_credits(credits),
            t('portfolio_cost'): format_currency(cost, currency),
            t('portfolio_balance'): format_currency(balance, currency) if balance else '—',
            t('portfolio_depletion'): str(days_depletion) if days_depletion is not None else (t('portfolio_depleted') if balance == 0 else '—'),
            t('portfolio_contract_used'): f"{used_pct:.1f}%" if used_pct is not None else '—',
            t('portfolio_overage_days'): str(days_overage) if days_overage is not None else '—',
            t('portfolio_ai'): '✅' if uses_ai else '❌',
            t('portfolio_risk'): risk,
        })

    if rows:
        portfolio_df = pd.DataFrame(rows)
        st.dataframe(portfolio_df, use_container_width=True, hide_index=True)
        st.caption(t("portfolio_risk_caption"))
    st.markdown("---")


def main():
    # Language selector — persist choice in URL query params (?lang=ja)
    # Must be initialised before any t() calls so titles render in the correct language.
    _lang_options = list(SUPPORTED_LANGUAGES.keys())
    _qp_lang = st.query_params.get("lang", DEFAULT_LANGUAGE)
    if _qp_lang not in _lang_options:
        _qp_lang = DEFAULT_LANGUAGE

    st.sidebar.selectbox(
        "🌐 Language",
        options=_lang_options,
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        key="language",
        index=_lang_options.index(
            st.session_state.get("language", _qp_lang)
        ),
    )

    # Sync selection back to query params so bookmarks remember the choice
    if st.session_state["language"] != st.query_params.get("lang"):
        st.query_params["lang"] = st.session_state["language"]
    st.sidebar.markdown("---")

    # Header with enhanced styling
    st.markdown(f'<h1 class="main-header">{APP_ICON} {t("app_title")}</h1>', unsafe_allow_html=True)
    st.markdown(f"### {t('app_subtitle')}")
    
    # Demo mode banner
    if USE_DEMO_DATA:
        st.info(t("app_demo_banner"))
    
    st.markdown("---")
    
    # Get Snowflake session (skip when demo mode)
    if USE_DEMO_DATA:
        session = None
    else:
        session = get_snowflake_session()
        if not session:
            if st.session_state.get('auth_expired', False):
                st.error(t("msg_auth_expired"))
                st.info(t("msg_auth_reconnect"))
                if st.button(t("msg_retry"), type="primary"):
                    st.session_state['auth_expired'] = False
                    st.cache_data.clear()
                    st.rerun()
            st.stop()

    # Sidebar with enhanced filters
    st.sidebar.header(t("sidebar_controls"))
    
    # Quick date range selector
    date_range_options = get_date_range_options()
    selected_range = st.sidebar.selectbox(
        t("sidebar_date_range"),
        options=list(date_range_options.keys()),
        index=1  # Default to "Last 30 days"
    )
    
    if selected_range == t("date_custom"):
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                t("date_start"),
                value=datetime.now() - timedelta(days=DEFAULT_DATE_RANGE_DAYS),
                max_value=datetime.now().date()
            )
        with col2:
            end_date = st.date_input(
                t("date_end"),
                value=datetime.now().date(),
                max_value=datetime.now().date()
            )
    else:
        start_date, end_date = date_range_options[selected_range]
    
    # Validate date range
    if not validate_date_range(start_date, end_date):
        st.stop()
    
    # Load customer list dynamically
    with st.spinner(t("sidebar_loading_customers")):
        customer_options = load_customer_list(session)
    
    # Customer filter
    customer_filter = st.sidebar.selectbox(
        t("sidebar_customer"),
        options=customer_options,
        index=0
    )

    st.sidebar.markdown("---")
    if st.sidebar.button(t("sidebar_refresh"), help="Clear cached data and session state, then reload", use_container_width=True):
        st.cache_data.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.sidebar.caption(t("sidebar_refresh_note"))

    usage_type_filter = None
    
    # Load data with enhanced loading indicator
    with st.spinner(t("msg_loading")):
        progress_bar = st.progress(0)
        
        usage_df = load_usage_data(session, start_date, end_date, customer_filter, usage_type_filter)
        progress_bar.progress(25)
        
        balance_df = load_balance_data(session, start_date, end_date, customer_filter)
        progress_bar.progress(55)

        # Load contract data at top level — needed for smart alerts + portfolio table
        contract_df = load_contract_data(session, customer_filter)
        progress_bar.progress(100)
        progress_bar.empty()
    
    # Check for data
    if usage_df.empty:
        st.warning(t("msg_no_data"))
        st.info(t("msg_adjust_filters"))
        return
    
    # Tab navigation — st.radio persists across reruns via session_state,
    # unlike st.tabs which resets to the first tab on any widget-triggered rerun
    TAB_OPTIONS = [t("tab_trends"), t("tab_usage"), t("tab_financial"), t("tab_feature")]
    if 'active_tab' not in st.session_state:
        st.session_state['active_tab'] = TAB_OPTIONS[0]

    active_tab = st.radio(
        "Navigation",
        options=TAB_OPTIONS,
        horizontal=True,
        label_visibility="collapsed",
        key="active_tab"
    )
    st.markdown("---")

    if active_tab == t("tab_trends"):
        # KPIs, portfolio summary, and alerts all live here
        st.subheader(t("kpi_header"))
        display_enhanced_metrics(usage_df, balance_df)

        if customer_filter == t("all_customers"):
            show_portfolio_summary(usage_df, balance_df, contract_df)

        show_alerts_and_insights(usage_df, balance_df, contract_df)

        trend_chart = create_enhanced_trend_chart(usage_df)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
        
        # Usage heatmap
        if len(usage_df) > 7:
            heatmap_chart = create_usage_heatmap(usage_df)
            if heatmap_chart:
                st.plotly_chart(heatmap_chart, use_container_width=True)

        # Month-over-month comparison chart
        mom_df = usage_df.copy()
        mom_df['Month'] = pd.to_datetime(mom_df['USAGE_DATE']).dt.to_period('M').dt.to_timestamp()
        if customer_filter == t("all_customers"):
            mom_agg = mom_df.groupby(['Month', 'SOLD_TO_CUSTOMER_NAME'])['USAGE_IN_CURRENCY'].sum().reset_index()
            mom_agg.columns = ['Month', 'Customer', 'Cost']
            if mom_agg['Month'].nunique() >= 2:
                fig_mom = px.bar(
                    mom_agg, x='Month', y='Cost', color='Customer',
                    title=t("trend_monthly_spend_customer"),
                    labels={'Cost': t("chart_axis_cost_usd"), 'Month': ''},
                    barmode='stack'
                )
                fig_mom.update_layout(height=360, legend=dict(orientation='h', y=-0.25),
                                      margin=dict(t=40, b=80),
                                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                fig_mom.update_xaxes(gridcolor='rgba(128,128,128,0.3)')
                fig_mom.update_yaxes(gridcolor='rgba(128,128,128,0.3)')
                st.plotly_chart(fig_mom, use_container_width=True)
        else:
            mom_agg = mom_df.groupby('Month')['USAGE_IN_CURRENCY'].sum().reset_index()
            mom_agg.columns = ['Month', 'Cost']
            mom_agg['MoM %'] = mom_agg['Cost'].pct_change() * 100
            if mom_agg['Month'].nunique() >= 2:
                fig_mom = go.Figure()
                fig_mom.add_trace(go.Bar(
                    x=mom_agg['Month'], y=mom_agg['Cost'],
                    name=t("chart_monthly_cost"), marker_color='#4A90D9',
                    text=mom_agg['Cost'].apply(lambda v: f"${v:,.0f}"),
                    textposition='outside'
                ))
                # MoM % change annotations
                for _, row in mom_agg.dropna(subset=['MoM %']).iterrows():
                    color = '#4CAF50' if row['MoM %'] >= 0 else '#FF5252'
                    sign = '+' if row['MoM %'] >= 0 else ''
                    fig_mom.add_annotation(
                        x=row['Month'], y=row['Cost'],
                        text=f"{sign}{row['MoM %']:.1f}%",
                        showarrow=False, yshift=30,
                        font=dict(color=color, size=11)
                    )
                fig_mom.update_layout(
                    title=t("trend_monthly_spend_mom"),
                    height=360, xaxis_title='', yaxis_title=t("chart_axis_cost_usd"),
                    margin=dict(t=40, b=40),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
                )
                fig_mom.update_xaxes(gridcolor='rgba(128,128,128,0.3)')
                fig_mom.update_yaxes(gridcolor='rgba(128,128,128,0.3)')
                st.plotly_chart(fig_mom, use_container_width=True)

        # Detailed data table
        st.subheader(t("trend_detailed_data"))
        with st.expander(t("trend_usage_details"), expanded=False):
            if not usage_df.empty:
                display_df = usage_df.copy()
                display_df['Credits'] = display_df['CREDITS_USED'].apply(format_credits)
                display_df['Cost'] = display_df.apply(
                    lambda row: format_currency(row['USAGE_IN_CURRENCY'], row['CURRENCY']), axis=1
                )
                display_df['Feature'] = display_df['USAGE_TYPE'].apply(
                    lambda x: USAGE_TYPE_DISPLAY.get(x, x.title())
                )
                cols = [c for c in [
                    'USAGE_DATE', 'SOLD_TO_CUSTOMER_NAME', 'ACCOUNT_NAME',
                    'ACCOUNT_LOCATOR', 'REGION', 'Feature', 'Credits', 'Cost'
                ] if c in display_df.columns]
                st.dataframe(
                    display_df[cols].sort_values('USAGE_DATE', ascending=False),
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
            else:
                st.info(t("trend_no_usage"))

        # Export functionality
        if FEATURES['export_enabled']:
            st.subheader(t("trend_export_header"))
            col1, col2, col3 = st.columns(3)
            with col1:
                if not usage_df.empty:
                    csv_data = export_to_csv(usage_df, "usage_data")
                    if csv_data:
                        st.download_button(
                            label=t("trend_export_usage"),
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
                            label=t("trend_export_balance"),
                            data=csv_data,
                            file_name=EXPORT_TEMPLATES['balance'].format(
                                start_date=start_date, end_date=end_date
                            ),
                            mime="text/csv"
                        )

    elif active_tab == t("tab_usage"):
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
                title=t("usage_credit_share"),
                hole=0.35
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=380, showlegend=False, margin=dict(t=40, b=10),
                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_bar = px.bar(
                usage_by_type,
                x='Feature',
                y='CREDITS_USED',
                color='Feature',
                title=t("usage_credits_per_feature"),
                labels={'CREDITS_USED': t("chart_axis_credits"), 'Feature': ''},
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
                yaxis_title=t("chart_axis_credits"),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            fig_bar.update_xaxes(gridcolor='rgba(128,128,128,0.3)')
            fig_bar.update_yaxes(gridcolor='rgba(128,128,128,0.3)')
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

        # ── Per-account breakdown ─────────────────────────────────────────────
        st.markdown("---")
        st.markdown(t("usage_account_breakdown"))

        account_usage = (
            usage_df.groupby(['SOLD_TO_CUSTOMER_NAME', 'ACCOUNT_NAME', 'ACCOUNT_LOCATOR', 'REGION'])
            .agg(Credits=('CREDITS_USED', 'sum'), Cost=('USAGE_IN_CURRENCY', 'sum'))
            .reset_index()
            .sort_values('Credits', ascending=False)
        )
        # Only show this section when there are multiple accounts
        n_accounts = account_usage['ACCOUNT_NAME'].nunique()
        if n_accounts > 1:
            fig_acct = px.bar(
                account_usage,
                x='ACCOUNT_NAME',
                y='Credits',
                color='SOLD_TO_CUSTOMER_NAME' if customer_filter == t("all_customers") else 'REGION',
                title=t("usage_credits_by_account"),
                labels={'ACCOUNT_NAME': 'Account', 'Credits': 'Credits',
                        'SOLD_TO_CUSTOMER_NAME': 'Customer', 'REGION': 'Region'},
                text='Credits'
            )
            fig_acct.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_acct.update_layout(
                height=380, xaxis_tickangle=-25,
                margin=dict(t=40, b=80),
                legend=dict(orientation='h', y=-0.3),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            fig_acct.update_xaxes(gridcolor='rgba(128,128,128,0.3)')
            fig_acct.update_yaxes(gridcolor='rgba(128,128,128,0.3)')
            st.plotly_chart(fig_acct, use_container_width=True)

            # Account table
            display_acct = account_usage.copy()
            display_acct['Credits'] = display_acct['Credits'].apply(format_credits)
            display_acct['Cost'] = display_acct['Cost'].apply(lambda v: format_currency(v, currency))
            display_acct.columns = ['Customer', 'Account', 'Locator', 'Region', 'Credits', 'Cost']
            st.dataframe(display_acct, use_container_width=True, hide_index=True)
        else:
            st.caption(t("usage_single_account"))

    elif active_tab == t("tab_financial"):
        currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"

        # ── Shared projection window selector ─────────────────────────────────
        col_rr, _ = st.columns([1, 4])
        with col_rr:
            financial_run_rate_days = st.selectbox(
                t("financial_projection_window"),
                options=[7, 30, 60, 90],
                index=1,
                format_func=lambda x: t("financial_last_n_days", n=x),
                help="Days of recent consumption used to calculate run rate and projections across both sections below",
                key="financial_run_rate_days"
            )

        # contract_df already loaded at top level — extend to full contract period
        # for consistent run rate vs chart comparisons
        if not contract_df.empty:
            contract_data_start = contract_df['START_DATE'].min()
            if contract_data_start < start_date:
                with st.spinner(t("financial_loading_history")):
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
        st.markdown(t("financial_balance_header"))

        overall_run_rate = calculate_overall_run_rate(contract_usage_df, balance_df, financial_run_rate_days)
        customer_run_rates = calculate_run_rate_by_customer(contract_usage_df, balance_df, financial_run_rate_days)

        # Show effective window — if available history is shorter than the
        # requested window, make it explicit so users understand why changing
        # from e.g. 60 → 90 days produces identical numbers
        effective_days = overall_run_rate.get('period_days', financial_run_rate_days) if overall_run_rate else financial_run_rate_days
        if effective_days < financial_run_rate_days:
            st.caption(t("financial_using_days", effective=effective_days, requested=financial_run_rate_days))
        else:
            st.caption(t("financial_based_on", days=financial_run_rate_days))

        if overall_run_rate:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    t("financial_daily_rate"),
                    format_credits(overall_run_rate['daily_rate_credits']),
                    delta=f"{format_currency(overall_run_rate['daily_rate_cost'], currency)}/day"
                )
            with col2:
                st.metric(
                    t("financial_weekly"),
                    format_credits(overall_run_rate['weekly_rate_credits']),
                    delta=f"{format_currency(overall_run_rate['weekly_rate_cost'], currency)}/week"
                )
            with col3:
                st.metric(
                    t("financial_monthly"),
                    format_credits(overall_run_rate['monthly_rate_credits']),
                    delta=f"{format_currency(overall_run_rate['monthly_rate_cost'], currency)}/month"
                )
            with col4:
                days_remaining = overall_run_rate.get('days_until_depletion')
                if days_remaining is not None and days_remaining > 0:
                    dep_icon = "🔴" if days_remaining < 30 else "🟡" if days_remaining < 60 else "🟢"
                    depletion_date = (datetime.now().date() + timedelta(days=int(days_remaining))).strftime('%-d %b %Y')
                    st.metric(
                        t("financial_depletion"),
                        f"{dep_icon} {days_remaining:.0f}",
                        delta=f"~{depletion_date} · Balance: {format_currency(overall_run_rate['total_balance'], currency)}"
                    )
                elif days_remaining == 0:
                    st.metric(t("financial_depletion"), "🔴 0", delta=t("financial_depletion_zero"))
                else:
                    st.metric(t("financial_depletion"), "N/A", delta=t("financial_depletion_na"))

        if not customer_run_rates.empty:
            csv_run_rate = export_to_csv(customer_run_rates, "run_rate_data")
            if csv_run_rate:
                st.download_button(
                    label=t("financial_export_run_rate"),
                    data=csv_run_rate,
                    file_name=f"run_rate_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )

        st.markdown("---")

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 2 — CONTRACT STATUS
        # ══════════════════════════════════════════════════════════════════════
        st.markdown(t("financial_contract_header"))

        if contract_df.empty:
            st.info(t("financial_no_contracts"))
        else:
            contract_metrics = calculate_contract_usage_metrics(
                contract_usage_df, contract_df, financial_run_rate_days
            )

            if not contract_metrics:
                st.info(t("financial_no_usage_contracts"))
            else:
                if customer_filter == t("all_customers"):
                    selected_customer = st.selectbox(
                        t("financial_select_customer"),
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
                            t("financial_capacity"),
                            format_currency(metrics['capacity_purchased'], metrics['currency']),
                            delta=f"Start: {metrics['contract_start'].strftime('%d/%m/%Y')}"
                        )
                    with col2:
                        st.metric(
                            t("financial_total_used"),
                            format_currency(metrics['total_used'], metrics['currency']),
                            delta=t("financial_capacity_used_pct", pct=metrics['used_percent'])
                        )
                    with col3:
                        overage_val = metrics['overage']
                        st.metric(
                            t("financial_overage_label"),
                            format_currency(overage_val, metrics['currency']) if overage_val > 0 else "$0.00",
                            delta=f"End: {metrics['contract_end'].strftime('%d/%m/%Y')}"
                        )
                    with col4:
                        if metrics['days_until_overage'] is not None and metrics['days_until_overage'] >= 0:
                            ov_icon = "🔴" if metrics['days_until_overage'] < 30 else "🟡" if metrics['days_until_overage'] < 60 else "🟢"
                            if metrics['days_until_overage'] == 0 and metrics['overage'] > 0:
                                ov_delta = t("financial_already_overage")
                            elif metrics['overage_date']:
                                ov_delta = f"Est. overage: {metrics['overage_date'].strftime('%d/%m/%Y')}"
                            else:
                                ov_delta = t("financial_within_contract")
                            st.metric(t("financial_days_overage"), f"{ov_icon} {int(metrics['days_until_overage'])}", delta=ov_delta)
                        else:
                            st.metric(t("financial_days_overage"), "N/A", delta=t("financial_sufficient"))

                    st.caption(t("financial_overage_caption"))

                    if metrics['days_until_overage'] is not None:
                        if metrics['days_until_overage'] == 0 and metrics['overage'] > 0:
                            st.markdown(
                                f'<div style="color: #dc3545; font-weight: bold; text-align: right; font-size: 1.1rem; margin-top: 0.25rem;">{t("financial_capacity_exhausted")}</div>',
                                unsafe_allow_html=True
                            )
                        elif metrics['overage_date']:
                            st.markdown(
                                f'<div style="color: #dc3545; font-weight: bold; text-align: right; font-size: 1.1rem; margin-top: 0.25rem;">{t("financial_projected_exhaust", date=metrics["overage_date"].strftime("%d/%m/%Y"))}</div>',
                                unsafe_allow_html=True
                            )

                    col_chart, col_aside = st.columns([3, 1])
                    with col_chart:
                        chart = create_contract_usage_chart(contract_usage_df, contract_metrics, selected_customer)
                        if chart:
                            st.plotly_chart(
                                chart,
                                use_container_width=True,
                                key=f"contract_chart_{selected_customer}_{financial_run_rate_days}"
                            )
                        else:
                            st.info(t("financial_not_enough_data"))
                    with col_aside:
                        st.markdown(t("financial_run_rate_label"))
                        st.markdown(f"### {format_currency(metrics['annual_run_rate'], metrics['currency'])}")
                        actual_period = metrics.get('run_rate_period', financial_run_rate_days)
                        if actual_period < financial_run_rate_days:
                            st.caption(t("financial_run_rate_warn", actual=actual_period, requested=financial_run_rate_days))
                        else:
                            st.caption(t("financial_run_rate_note", days=actual_period))

                    with st.expander(t("financial_contract_details"), expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(t("financial_timeline"))
                            st.write(f"- {t('financial_start', date=metrics['contract_start'].strftime('%d %B %Y'))}")
                            st.write(f"- {t('financial_end', date=metrics['contract_end'].strftime('%d %B %Y'))}")
                            st.write(f"- {t('financial_duration', days=metrics['days_in_contract'])}")
                            st.write(f"- {t('financial_elapsed', days=metrics['days_elapsed'])}")
                            st.write(f"- {t('financial_remaining', days=(metrics['contract_end'] - datetime.now().date()).days)}")
                        with col2:
                            st.markdown(t("financial_projections"))
                            st.write(f"- {t('financial_daily', value=format_currency(metrics['daily_run_rate'], metrics['currency']))}")
                            st.write(f"- {t('financial_weekly_proj', value=format_currency(metrics['daily_run_rate'] * 7, metrics['currency']))}")
                            st.write(f"- {t('financial_monthly_proj', value=format_currency(metrics['daily_run_rate'] * 30, metrics['currency']))}")
                            st.write(f"- {t('financial_annual', value=format_currency(metrics['annual_run_rate'], metrics['currency']))}")
                            st.write(f"- {t('financial_window', days=metrics['run_rate_period'])}")
    
    elif active_tab == t("tab_feature"):
        st.markdown(t("feature_header"))
        st.markdown(t("feature_subtitle"))

        if usage_df.empty:
            st.info(t("feature_no_data"))
        else:
            currency = usage_df['CURRENCY'].iloc[0] if not usage_df.empty else "USD"
            all_known_features = set(USAGE_TYPE_DISPLAY.keys())
            used_globally = set(usage_df['USAGE_TYPE'].str.lower().unique())

            # ── Adoption matrix (all-customers view) ─────────────────────────
            if customer_filter == t("all_customers"):
                st.markdown(t("feature_matrix"))
                st.caption(t("feature_matrix_caption"))

                pivot = (
                    usage_df.groupby(['SOLD_TO_CUSTOMER_NAME', 'USAGE_TYPE'])['CREDITS_USED']
                    .sum().reset_index()
                )
                pivot['Feature'] = pivot['USAGE_TYPE'].apply(
                    lambda x: USAGE_TYPE_DISPLAY.get(x, x.title())
                )
                matrix = pivot.pivot(
                    index='SOLD_TO_CUSTOMER_NAME', columns='Feature', values='CREDITS_USED'
                ).fillna(0)

                fig_matrix = px.imshow(
                    matrix,
                    labels=dict(x='Feature', y='Customer', color='Credits'),
                    color_continuous_scale='Viridis',
                    aspect='auto',
                    text_auto='.0f'
                )
                fig_matrix.update_layout(
                    height=max(280, len(matrix) * 60),
                    margin=dict(t=20, b=60, l=160, r=20),
                    coloraxis_showscale=False,
                    xaxis=dict(tickangle=-35, side='bottom'),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
                )
                fig_matrix.update_traces(textfont_size=10)
                st.plotly_chart(fig_matrix, use_container_width=True)
                st.markdown("---")

            # ── Customer deep dive ────────────────────────────────────────────
            st.markdown(t("feature_breakdown"))

            if customer_filter == t("all_customers"):
                feature_customer = st.selectbox(
                    t("feature_select_customer"),
                    options=sorted(usage_df['SOLD_TO_CUSTOMER_NAME'].unique()),
                    key="feature_customer_select"
                )
            else:
                feature_customer = customer_filter
                st.markdown(t("feature_showing", name=feature_customer))

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
                        title=t("feature_usage_over_time", name=feature_customer),
                        labels={'CREDITS_USED': t("chart_axis_credits"), 'USAGE_DATE': t("chart_axis_date")}
                    )
                    fig_trend.update_layout(height=340, hovermode='x unified',
                                            legend=dict(orientation='h', y=-0.25),
                                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig_trend.update_xaxes(gridcolor='rgba(128,128,128,0.3)')
                    fig_trend.update_yaxes(gridcolor='rgba(128,128,128,0.3)')
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
            st.markdown(t("feature_upsell"))

            if customer_filter != t("all_customers") and not customer_feature_df.empty:
                used_scope = set(customer_feature_df['USAGE_TYPE'].str.lower().unique())
                scope_label = t("feature_upsell_scope_customer", name=customer_filter)
            else:
                used_scope = used_globally
                scope_label = t("feature_upsell_scope_all")

            unused_features = sorted(all_known_features - used_scope)

            if unused_features:
                st.caption(scope_label)
                # Show 2 cards per row
                for row_start in range(0, len(unused_features), 2):
                    row_feats = unused_features[row_start:row_start + 2]
                    cols = st.columns(len(row_feats))
                    for col_idx, feat in enumerate(row_feats):
                        display_name  = USAGE_TYPE_DISPLAY.get(feat, feat.title())
                        use_case_text = t_usecase(feat)
                        with cols[col_idx]:
                            st.markdown(
                                f'<div class="upsell-card">'
                                f'<strong class="upsell-card-title">{display_name}</strong><br>'
                                f'<span class="upsell-card-desc">{use_case_text}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
            else:
                st.success(t("feature_all_used"))

            # ── Data source note ─────────────────────────────────────────────
            with st.expander(t("feature_datasource"), expanded=False):
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

> **Demo mode:** synthetic data matches this schema exactly. Connect to your SPN account to see your customer(s) consumption.
                """)

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"*{t('msg_data_refresh')}*")
    
    with col2:
        st.markdown(f"*{t('footer_data_range', start=start_date, end=end_date)}*")
    
    with col3:
        if not usage_df.empty:
            st.markdown(f"*{t('footer_total_records', count=f'{len(usage_df):,}')}*")

if __name__ == "__main__":
    main() 