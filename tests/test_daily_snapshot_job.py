import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from core.memory import (
    upsert_daily_snapshot,
    get_historical_snapshot,
    get_all_snapshots,
    get_distinct_tracked_symbols
)
from tools.snapshot_helper import calculate_period_return
from scripts.daily_snapshot_job import run_daily_snapshots

def test_daily_snapshot_upsert_and_retrieve():
    test_sym = "TEST_TICKER.NS"
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # 1. Upsert snapshot
    success = upsert_daily_snapshot(
        asset_type="equity",
        symbol_or_scheme_code=test_sym,
        name="Test Ticker Ltd",
        value=1000.0,
        snapshot_date=today_str,
        source="unit_test"
    )
    assert success is True
    
    # 2. Retrieve snapshot
    rec = get_historical_snapshot("equity", test_sym, today_str)
    assert rec is not None
    assert rec["symbol_or_scheme_code"] == test_sym
    assert rec["value"] == 1000.0
    
    # 3. Idempotent Upsert (update value on same date)
    upsert_daily_snapshot(
        asset_type="equity",
        symbol_or_scheme_code=test_sym,
        name="Test Ticker Ltd",
        value=1050.0,
        snapshot_date=today_str,
        source="unit_test"
    )
    rec_updated = get_historical_snapshot("equity", test_sym, today_str)
    assert rec_updated["value"] == 1050.0

def test_calculate_period_return():
    test_code = "TEST_MF_001"
    today = datetime.now(timezone.utc).date()
    date_7d_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Seed historical 7-day-old snapshot at 100.0
    upsert_daily_snapshot(
        asset_type="mutual_fund",
        symbol_or_scheme_code=test_code,
        name="Test Growth Fund",
        value=100.0,
        snapshot_date=date_7d_ago,
        source="unit_test"
    )
    
    # Calculate 1W return assuming today's live NAV is 112.50 (+12.5%)
    res = calculate_period_return(
        asset_type="mutual_fund",
        symbol_or_scheme_code=test_code,
        current_value=112.50,
        period="1w"
    )
    
    assert res["status"] == "success"
    assert res["period"] == "1W"
    assert res["past_value"] == 100.0
    assert res["current_value"] == 112.50
    assert res["pct_change"] == 12.5
    assert "+12.5%" in res["formatted_summary"]

def test_period_return_graceful_fallback():
    # Unrecorded asset returns graceful fallback instead of crashing
    res = calculate_period_return(
        asset_type="equity",
        symbol_or_scheme_code="NON_EXISTENT.NS",
        current_value=500.0,
        period="1m"
    )
    assert res["status"] == "no_history"
    assert res["pct_change"] is None
    assert "No historical" in res["formatted_summary"]

@patch("scripts.daily_snapshot_job.run_mf_nav_snapshot")
@patch("scripts.daily_snapshot_job.fetch_equity_closing_price")
@patch("scripts.daily_snapshot_job.fetch_amfi_nav")
def test_daily_snapshot_job_execution(mock_amfi, mock_equity, mock_mf_nav):
    mock_equity.return_value = 2500.0
    mock_amfi.return_value = 75.50
    mock_mf_nav.return_value = {"mf_nav_success": 6, "mf_nav_fail": 0}

    test_date = "2026-09-25"
    summary = run_daily_snapshots(custom_date=test_date)

    assert summary["status"] == "completed"
    assert summary["success_count"] > 0
    assert summary["fail_count"] == 0
    assert summary["mf_nav_success"] == 6


# ============================================================
# MF NAV Snapshot dedup tests (Phase 6 addition)
# ============================================================

from core.memory import upsert_mf_nav_snapshot, get_historical_mf_nav

def test_mf_nav_upsert_idempotency():
    """
    UNIQUE constraint validation: inserting the same (scheme_code, date) twice
    must produce exactly one row, not two -- this is the direct lesson from the
    nightly chunk-dedup incident applied to mf_nav_snapshots from the start.
    """
    code = "TEST_MF_DEDUP_001"
    date = "2026-09-25"

    # First insert
    upsert_mf_nav_snapshot(
        scheme_code=code,
        scheme_name="Test Dedup Fund",
        nav=100.50,
        snapshot_date=date,
        source="unit_test"
    )

    # Second insert -- same (code, date), different NAV (simulating re-run)
    upsert_mf_nav_snapshot(
        scheme_code=code,
        scheme_name="Test Dedup Fund",
        nav=101.25,          # updated value on re-run
        snapshot_date=date,
        source="unit_test_rerun"
    )

    # Fetch -- must find exactly one row with the UPDATED nav
    rec = get_historical_mf_nav(code, date)
    assert rec is not None, "Row must exist after upsert"
    assert rec["nav"] == 101.25, (
        f"Expected updated NAV 101.25 from second upsert, got {rec['nav']}. "
        f"UNIQUE constraint dedup failed -- would have created duplicate rows."
    )
    assert rec["source"] == "unit_test_rerun", "Source should reflect most recent upsert"


def test_mf_nav_graceful_no_history():
    """
    Scheme with no snapshot history must return None from get_historical_mf_nav,
    not crash. Callers (snapshot_helper) rely on this for the no-history-yet path.
    """
    from datetime import datetime, timedelta, timezone
    future = (datetime.now(timezone.utc).date() + timedelta(days=30)).strftime("%Y-%m-%d")
    rec = get_historical_mf_nav("NON_EXISTENT_SCHEME_XYZ", future)
    assert rec is None, "Expected None for scheme with no history"


def test_mf_nav_nearest_date_lookup():
    """
    get_historical_mf_nav must return the NEAREST date on or before target,
    not an exact match -- mirrors get_historical_snapshot semantics.
    """
    from datetime import datetime, timedelta, timezone
    import uuid
    code = "TEST_MF_NEAREST_" + str(uuid.uuid4())[:8]
    today = datetime.now(timezone.utc).date()
    date_5d_ago = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    date_10d_ago = (today - timedelta(days=10)).strftime("%Y-%m-%d")

    upsert_mf_nav_snapshot(code, "Test Nearest Fund", 200.0, date_10d_ago, "unit_test")
    upsert_mf_nav_snapshot(code, "Test Nearest Fund", 210.0, date_5d_ago,  "unit_test")

    # Query for 7 days ago -- nearest prior is 10 days ago (5d ago is after target)
    date_7d_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    rec = get_historical_mf_nav(code, date_7d_ago)
    assert rec is not None
    assert rec["nav"] == 200.0, (
        f"Expected nav from {date_10d_ago} (nearest prior to {date_7d_ago}), "
        f"got nav={rec['nav']} from {rec['snapshot_date']}"
    )
