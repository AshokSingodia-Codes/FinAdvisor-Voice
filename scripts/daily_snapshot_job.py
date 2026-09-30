import os
import sys
import time
import requests
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory import (
    upsert_daily_snapshot,
    upsert_mf_nav_snapshot,
    get_distinct_tracked_symbols,
)
from nodes.market_data import _get_yfinance_data_with_retries, _get_finnhub_fallback_data

# Seed list of core Indian Equities & Major Benchmarks
SEED_EQUITIES = [
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services Ltd"},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd"},
    {"ticker": "INFY.NS", "name": "Infosys Ltd"},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd"},
    {"ticker": "ITC.NS", "name": "ITC Ltd"},
    {"ticker": "SBIN.NS", "name": "State Bank of India"},
    {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd"},
    {"ticker": "LT.NS", "name": "Larsen & Toubro Ltd"},
    {"ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd"},
    {"ticker": "^NSEI", "name": "NIFTY 50 Index"},
    {"ticker": "^BSESN", "name": "S&P BSE SENSEX Index"}
]

# Seed list of top AMFI Mutual Fund Schemes (Direct Growth)
SEED_MUTUAL_FUNDS = [
    {"code": "122639", "name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth"},
    {"code": "120503", "name": "Mirae Asset Large Cap Fund - Direct Plan - Growth"},
    {"code": "118989", "name": "HDFC Top 100 Fund - Direct Plan - Growth"},
    {"code": "119598", "name": "SBI Bluechip Fund - Direct Plan - Growth"},
    {"code": "120847", "name": "Quant Small Cap Fund - Direct Plan - Growth"},
    {"code": "125354", "name": "Axis Small Cap Fund - Direct Plan - Growth"}
]

def fetch_equity_closing_price(ticker: str) -> Optional[float]:
    """Fetches the latest closing/current price for a given stock ticker."""
    try:
        info, _, _ = _get_yfinance_data_with_retries(ticker)
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if price is not None and float(price) > 0:
            return float(price)
    except Exception as yf_err:
        try:
            fh_info, _, _ = _get_finnhub_fallback_data(ticker)
            price = fh_info.get("currentPrice")
            if price is not None and float(price) > 0:
                return float(price)
        except Exception:
            pass
    return None


AMFI_NAVALL_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

# NAVAll.txt column indices (semicolon-delimited, 8 cols):
#  0=SchemeCode  1=ISIN_Div  2=ISIN_Growth  3=SchemeName  4=Plan  5=Option  6=NAV  7=Date
_NAVALL_CODE_IDX  = 0
_NAVALL_NAME_IDX  = 3
_NAVALL_NAV_IDX   = 6
_NAVALL_DATE_IDX  = 7


def fetch_navall_for_watchlist(
    scheme_codes: set,
    snapshot_date: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Downloads NAVAll.txt once and extracts NAVs for the given scheme_codes.
    Returns {scheme_code: {scheme_name, nav, date}} for matched schemes only.
    Much cheaper than one mfapi.in call per scheme for large watchlists.
    """
    try:
        res = requests.get(AMFI_NAVALL_URL, timeout=20)
        if res.status_code != 200:
            print(f"  [NAVAll] HTTP {res.status_code} -- skipping batch NAV sync")
            return {}
    except Exception as e:
        print(f"  [NAVAll] Fetch error: {e} -- skipping batch NAV sync")
        return {}

    results: Dict[str, Dict[str, Any]] = {}
    for line in res.text.splitlines():
        parts = line.split(";")
        if len(parts) < 8:
            continue
        code = parts[_NAVALL_CODE_IDX].strip()
        if code not in scheme_codes:
            continue
        try:
            nav  = float(parts[_NAVALL_NAV_IDX].strip())
            name = parts[_NAVALL_NAME_IDX].strip()
            date_raw = parts[_NAVALL_DATE_IDX].strip()  # e.g. "25-Sep-2026"
            # Normalise to YYYY-MM-DD
            from datetime import datetime
            try:
                parsed = datetime.strptime(date_raw, "%d-%b-%Y")
                date_iso = parsed.strftime("%Y-%m-%d")
            except ValueError:
                date_iso = snapshot_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
            results[code] = {"scheme_name": name, "nav": nav, "date": date_iso}
        except (ValueError, IndexError):
            continue
    return results


def run_mf_nav_snapshot(mf_scheme_codes: Dict[str, str],
                        snapshot_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches NAVAll.txt once and upserts NAV snapshots for all tracked/seed
    MF schemes into mf_nav_snapshots (UNIQUE on scheme_code+date -- safe to
    re-run; second pass updates, never duplicates).
    """
    snapshot_date = snapshot_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    code_set = set(mf_scheme_codes.keys())
    nav_data = fetch_navall_for_watchlist(code_set, snapshot_date)

    print(f"\n[*] NAVAll.txt returned {len(nav_data)}/{len(code_set)} watched schemes")
    success, fail = 0, 0
    for code, info in nav_data.items():
        upsert_mf_nav_snapshot(
            scheme_code=code,
            scheme_name=info["scheme_name"] or mf_scheme_codes.get(code, code),
            nav=info["nav"],
            snapshot_date=info["date"],
            source="NAVAll.txt"
        )
        print(f"  \u2713 [mf_nav] {code} ({info['scheme_name'][:35]}): NAV \u20b9{info['nav']:,.4f} ({info['date']})")
        success += 1
    for code in code_set - set(nav_data.keys()):
        print(f"  \u2717 [mf_nav] {code}: not found in NAVAll.txt")
        fail += 1
    return {"mf_nav_success": success, "mf_nav_fail": fail}


def fetch_amfi_nav(scheme_code: str) -> Optional[float]:
    """Fetches the latest NAV for an AMFI scheme from mfapi.in (single-scheme path)."""
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}/latest"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data and "data" in data and len(data["data"]) > 0:
                nav_str = data["data"][0].get("nav")
                if nav_str:
                    return float(nav_str)
    except Exception as e:
        print(f"Error fetching NAV for scheme {scheme_code}: {e}")
    return None


def run_daily_snapshots(custom_date: Optional[str] = None):
    """
    Executes the scheduled daily snapshot recording process.
    Upserts price / NAV snapshots into daily_snapshots table.
    """
    snapshot_date = custom_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"\n[SNAPSHOT JOB] Starting Daily Snapshot Job for Date: {snapshot_date}")
    
    success_count = 0
    fail_count = 0
    
    # 1. Gather all tracked equities (Seeds + DB history)
    tracked_db = get_distinct_tracked_symbols()
    equity_tickers = {item["ticker"]: item["name"] for item in SEED_EQUITIES}
    for item in tracked_db:
        if item["asset_type"] == "equity":
            equity_tickers[item["symbol_or_scheme_code"]] = item.get("name") or item["symbol_or_scheme_code"]
            
    print(f"[*] Processing {len(equity_tickers)} Equities & Indices...")
    for ticker, name in equity_tickers.items():
        price = fetch_equity_closing_price(ticker)
        if price is not None:
            upsert_daily_snapshot(
                asset_type="equity",
                symbol_or_scheme_code=ticker,
                name=name,
                value=price,
                snapshot_date=snapshot_date,
                source="yahoo_finnhub"
            )
            print(f"  ✓ [Equity] {ticker}: ₹{price:,.2f}")
            success_count += 1
        else:
            print(f"  ✗ [Equity] Failed to fetch price for {ticker}")
            fail_count += 1
        time.sleep(0.3)
        
    # 2. Gather all tracked Mutual Funds (Seeds + DB history)
    mf_schemes = {item["code"]: item["name"] for item in SEED_MUTUAL_FUNDS}
    for item in tracked_db:
        if item["asset_type"] == "mutual_fund":
            mf_schemes[item["symbol_or_scheme_code"]] = item.get("name") or item["symbol_or_scheme_code"]
            
    print(f"\n[*] Processing {len(mf_schemes)} Mutual Fund Schemes...")
    for code, name in mf_schemes.items():
        nav = fetch_amfi_nav(code)
        if nav is not None:
            upsert_daily_snapshot(
                asset_type="mutual_fund",
                symbol_or_scheme_code=code,
                name=name,
                value=nav,
                snapshot_date=snapshot_date,
                source="mfapi_amfi"
            )
            print(f"  ✓ [MF] {code} ({name[:30]}...): NAV ₹{nav:,.4f}")
            success_count += 1
        else:
            print(f"  ✗ [MF] Failed to fetch NAV for scheme {code}")
            fail_count += 1
        time.sleep(0.2)
        
    # 3. NAVAll.txt batch sync -> mf_nav_snapshots
    mf_nav_result = run_mf_nav_snapshot(mf_schemes, snapshot_date=snapshot_date)

    print(f"\n[SNAPSHOT JOB COMPLETED] Equities+MF daily_snapshots: Saved {success_count}, Failed {fail_count}")
    print(f"[SNAPSHOT JOB COMPLETED] mf_nav_snapshots: Saved {mf_nav_result['mf_nav_success']}, Not found {mf_nav_result['mf_nav_fail']}\n")
    return {
        "status": "completed",
        "success_count": success_count,
        "fail_count": fail_count,
        "date": snapshot_date,
        **mf_nav_result,
    }

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_daily_snapshots(date_arg)
