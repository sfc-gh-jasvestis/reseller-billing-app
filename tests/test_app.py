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

    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def sql(self, query, params=None):
        self.calls.append((query, params))
        if self.fail and "SNOWFLAKE.BILLING" in query:
            raise Exception("Object 'SNOWFLAKE.BILLING.PARTNER_USAGE_IN_CURRENCY_DAILY' does not exist or not authorized.")
        today = date.today()
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
                "USAGE_TYPE": "Compute", "CURRENCY": "USD", "CREDITS_USED": 10.0,
                "USAGE_IN_CURRENCY": 30.0, "BALANCE_SOURCE": "capacity"} for i in range(20)]
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
    for option in at.radio[0].options:
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
