"""Regression tests for streamlit_app.py. Run: python -m pytest tests -q"""
import os
import sys
from datetime import date, timedelta

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(__file__), "..", "streamlit_app.py")
sys.path.insert(0, os.path.dirname(APP))


class FakeResult:
    def __init__(self, df):
        self._df = df

    def to_pandas(self):
        return self._df

    def collect(self):
        return []


class FakeSession:
    """Minimal Snowpark stand-in that records queries and bound params."""

    def __init__(self, fail=False, missing=()):
        self.fail = fail
        self.missing = set(missing)
        self.calls = []

    def sql(self, query, params=None):
        self.calls.append((query, params))
        if self.fail and "SNOWFLAKE.BILLING" in query:
            raise Exception("Object 'SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY' does not exist or not authorized.")
        for view in self.missing:
            if view in query:
                raise Exception(f"Object 'SNOWFLAKE.BILLING.{view}' does not exist or not authorized.")
        today = date.today()
        if "PARTNER_RATE_SHEET_DAILY" in query:
            return FakeResult(pd.DataFrame([{
                "RATE_DATE": today - timedelta(days=i), "SOLD_TO_CUSTOMER_NAME": "Live Co",
                "ACCOUNT_NAME": "live_prod", "REGION": "AWS_US_WEST_2", "SERVICE_TYPE": "WAREHOUSE_METERING",
                "RATING_TYPE": "compute", "CURRENCY": "USD", "EFFECTIVE_RATE": 3.0} for i in range(20)]))
        if "PARTNER_REMAINING_BALANCE_DAILY" in query:
            return FakeResult(pd.DataFrame([{
                "SOLD_TO_ORGANIZATION_NAME": "Org", "SOLD_TO_CUSTOMER_NAME": "Live Co",
                "SOLD_TO_CONTRACT_NUMBER": "C1", "BALANCE_DATE": today, "CURRENCY": "USD",
                "FREE_USAGE_BALANCE": 0.0, "CAPACITY_BALANCE": 5000.0,
                "ON_DEMAND_CONSUMPTION_BALANCE": 0.0, "ROLLOVER_BALANCE": 0.0}]))
        if "PARTNER_CONTRACT_ITEMS" in query:
            return FakeResult(pd.DataFrame([{
                "SOLD_TO_CUSTOMER_NAME": "Live Co", "SOLD_TO_CONTRACT_NUMBER": "C1",
                "START_DATE": today - timedelta(days=60), "END_DATE": today + timedelta(days=300),
                "AMOUNT": 20000.0, "CURRENCY": "USD", "CONTRACT_ITEM": "Capacity"}]))
        if "SELECT DISTINCT" in query:
            return FakeResult(pd.DataFrame({"SOLD_TO_CUSTOMER_NAME": ["Live Co"]}))
        if "PARTNER_USAGE_IN_CURRENCY_DAILY" in query:
            rows = [{
                "SOLD_TO_ORGANIZATION_NAME": "Org", "SOLD_TO_CUSTOMER_NAME": "Live Co",
                "SOLD_TO_CONTRACT_NUMBER": "C1", "ACCOUNT_NAME": "live_prod", "ACCOUNT_LOCATOR": "LV1",
                "REGION": "AWS_US_WEST_2", "SERVICE_LEVEL": "Enterprise", "USAGE_DATE": today - timedelta(days=i),
                "USAGE_TYPE": "Compute" if i else "overage compute", "CURRENCY": "USD", "CREDITS_USED": 10.0,
                "USAGE_IN_CURRENCY": 30.0, "BALANCE_SOURCE": "capacity" if i else "overage",
                "SERVICE_TYPE": "WAREHOUSE_METERING", "BILLING_TYPE": "consumption",
                "RATING_TYPE": "compute", "IS_ADJUSTMENT": False} for i in range(20)]
            return FakeResult(pd.DataFrame(rows))
        return FakeResult(pd.DataFrame())


def run_app(monkeypatch, session=None, demo_env=None, lang=None):
    if demo_env is None:
        monkeypatch.delenv("USE_DEMO_DATA", raising=False)
    else:
        monkeypatch.setenv("USE_DEMO_DATA", demo_env)
    import streamlit as st
    st.cache_data.clear()
    at = AppTest.from_file(APP, default_timeout=60)
    if lang:
        at.query_params["lang"] = lang
    if session is not None:
        import streamlit as st

        class Conn:
            def session(self_inner):
                return session
        monkeypatch.setattr(st, "connection", lambda *a, **k: Conn())
    at.run()
    return at


def texts(at, kind):
    return " ".join(e.value for e in getattr(at, kind))


def test_forced_demo_mode_renders_without_errors(monkeypatch):
    at = run_app(monkeypatch, demo_env="true")
    assert not at.exception
    assert not at.error
    assert "Demo Mode Active" in texts(at, "info")


def test_missing_billing_views_falls_back_to_demo(monkeypatch):
    at = run_app(monkeypatch, session=FakeSession(fail=True))
    assert not at.exception
    assert not at.error, texts(at, "error")
    assert "Live billing data is unavailable" in texts(at, "info")
    assert "Acme Corporation" in at.sidebar.selectbox[2].options


def test_live_mode_uses_billing_views(monkeypatch):
    at = run_app(monkeypatch, session=FakeSession())
    assert not at.exception
    assert not at.error, texts(at, "error")
    assert "Demo Mode Active" not in texts(at, "info")
    assert at.sidebar.selectbox[2].options == ["All Customers", "Live Co"]


def test_forced_live_mode_reports_missing_views(monkeypatch):
    at = run_app(monkeypatch, session=FakeSession(fail=True), demo_env="false")
    assert not at.exception
    assert "partner views are not readable" in texts(at, "error")


def test_japanese_all_customers_still_returns_data(monkeypatch):
    at = run_app(monkeypatch, demo_env="true", lang="ja")
    assert not at.exception
    assert at.sidebar.selectbox[2].value == "__ALL_CUSTOMERS__"
    assert at.sidebar.selectbox[2].options[0] == "全顧客"
    assert "選択した条件に該当するデータが見つかりません" not in texts(at, "warning")


def test_every_tab_renders(monkeypatch):
    at = run_app(monkeypatch, demo_env="true")
    for option in _app().TAB_KEYS:
        at.radio[0].set_value(option).run()
        assert not at.exception, option


def test_customer_filter_is_bound_not_interpolated(monkeypatch):
    import streamlit_app as app
    session = FakeSession()
    app.load_usage_data.clear()
    hostile = "x' OR '1'='1"
    app.load_usage_data(session, date(2026, 1, 1), date(2026, 1, 31), hostile, ["compute", "storage"])
    query, params = session.calls[-1]
    assert hostile not in query
    assert params == ["2026-01-01", "2026-01-31", hostile, "compute", "storage"]


# --------------------------------------------------------------------------
# Cost enhancements
# --------------------------------------------------------------------------

def _app():
    import streamlit_app as app
    return app


def _demo_consumption(days=89):
    app = _app()
    end = date.today()
    usage = app.clean_usage_data(app.generate_demo_usage_data(end - timedelta(days=days), end))
    return app.split_usage(usage)


def test_overage_prefix_parsed():
    app = _app()
    df = app.clean_usage_data(pd.DataFrame([
        {"USAGE_TYPE": "overage compute", "BALANCE_SOURCE": "overage", "USAGE_DATE": date.today(),
         "CREDITS_USED": 1.0, "USAGE_IN_CURRENCY": 3.0, "SERVICE_TYPE": None},
        {"USAGE_TYPE": "Storage", "BALANCE_SOURCE": "capacity", "USAGE_DATE": date.today(),
         "CREDITS_USED": 1.0, "USAGE_IN_CURRENCY": 3.0, "SERVICE_TYPE": "storage"},
    ]))
    assert df["IS_OVERAGE"].tolist() == [True, False]
    assert df["USAGE_TYPE"].tolist() == ["compute", "storage"]
    assert df["SERVICE_TYPE"].tolist() == ["COMPUTE", "STORAGE"]
    assert df["BILLING_TYPE"].tolist() == ["consumption", "consumption"]


def test_split_usage_separates_other_charges_and_adjustments():
    app = _app()
    usage = app.clean_usage_data(app.generate_demo_usage_data(date.today() - timedelta(days=29), date.today()))
    consumption, other = app.split_usage(usage)
    assert set(other["BILLING_TYPE"]) == {"support_credit", "rebate"}
    assert not consumption["IS_ADJUSTMENT"].any()
    with_adj, _ = app.split_usage(usage, include_adjustments=True)
    assert with_adj["IS_ADJUSTMENT"].sum() == 1


def test_demo_overage_only_for_exhausted_customer():
    consumption, _ = _demo_consumption()
    assert set(consumption.loc[consumption["IS_OVERAGE"], "SOLD_TO_CUSTOMER_NAME"]) == {"SmallBiz Insights"}


def test_rates_missing_while_usage_live(monkeypatch):
    at = run_app(monkeypatch, session=FakeSession(missing={"PARTNER_RATE_SHEET_DAILY"}))
    assert not at.exception
    assert "Demo Mode Active" not in texts(at, "info")
    at.radio[0].set_value("tab_financial").run()
    assert not at.exception
    assert not at.error, texts(at, "error")
    assert "PARTNER_RATE_SHEET_DAILY is not readable" in texts(at, "info")


def test_live_overage_alert(monkeypatch):
    at = run_app(monkeypatch, session=FakeSession())
    at.radio[0].set_value("tab_trends").run()
    assert not at.exception
    assert "Live Co" in " ".join(m.value for m in at.markdown if "on-demand" in m.value)


def test_rate_change_detected():
    app = _app()
    end = date.today()
    summary, _ = app.summarize_rates(app.generate_demo_rate_data(end - timedelta(days=29), end))
    acme = summary.set_index("CUSTOMER").loc["Acme Corporation"]
    assert acme["FIRST_RATE"] == 2.70 and acme["LATEST_RATE"] == 2.55
    others = summary[summary["CUSTOMER"] != "Acme Corporation"]
    assert (others["CHANGE_PCT"].abs() < app.RATE_CHANGE_ALERT_PCT).all()


def test_anomaly_flags_only_injected_spike():
    app = _app()
    consumption, _ = _demo_consumption()
    anomalies = app.detect_anomalies(consumption)
    assert len(anomalies) == 1
    row = anomalies.iloc[0]
    assert row["CUSTOMER"] == "Global Analytics Co" and row["SERVICE_TYPE"] == "WAREHOUSE_METERING"
    assert (date.today() - row["DATE"]).days in range(12, 15)


def _flat_series(value=100.0, days=60):
    end = date.today()
    return pd.Series(value, index=[end - timedelta(days=i) for i in range(days)][::-1])


def test_forecast_band_and_exhaustion():
    app = _app()
    forecast = app.forecast_daily_cost(_flat_series(), 30)
    assert len(forecast) == 30
    assert forecast["YHAT"].round(6).eq(100.0).all()
    assert (forecast["LO"] <= forecast["YHAT"]).all() and (forecast["YHAT"] <= forecast["HI"]).all()
    assert app.forecast_exhaustion_date(forecast, 0, 1_000_000) is None
    assert app.forecast_exhaustion_date(forecast, 0, 1000) == date.today() + timedelta(days=10)
    assert app.forecast_daily_cost(_flat_series(days=10), 30) is None


def test_renewal_sizing():
    app = _app()
    spend, recommended = app.estimate_renewal_capacity(
        _flat_series(), date.today() + timedelta(days=1), 365, 10)
    assert round(spend) == 36500
    assert round(recommended) == 40150


def test_growth_ranking():
    app = _app()
    end = date.today()
    df = pd.DataFrame([
        {"SOLD_TO_CUSTOMER_NAME": "A", "USAGE_DATE": end - timedelta(days=d),
         "USAGE_IN_CURRENCY": 20.0 if d < 30 else 10.0} for d in range(60)
    ])
    growth = app.growth_ranking(df, end)
    assert round(growth.iloc[0]["GROWTH_PCT"]) == 100


@pytest.mark.parametrize("lang", ["en", "ja"])
def test_every_tab_renders_in_each_language(monkeypatch, lang):
    import streamlit as st
    monkeypatch.setenv("USE_DEMO_DATA", "true")
    for tab in _app().TAB_KEYS:
        st.cache_data.clear()
        at = AppTest.from_file(APP, default_timeout=60)
        at.query_params["lang"] = lang
        at.session_state["active_tab"] = tab
        at.run()
        assert not at.exception, (lang, tab, at.exception)
        assert not at.error, (lang, tab, texts(at, "error"))
        assert at.radio[0].value == tab
