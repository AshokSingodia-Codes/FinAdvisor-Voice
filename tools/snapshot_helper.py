from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from core.memory import get_historical_snapshot, upsert_daily_snapshot

PERIOD_DAYS_MAP = {
    "1d": 1,
    "1w": 7,
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
}

def calculate_period_return(
    asset_type: str,
    symbol_or_scheme_code: str,
    current_value: float,
    period: str = "1w"
) -> Dict[str, Any]:
    """
    Given an asset type ('equity' | 'mutual_fund'), symbol or AMFI scheme code,
    and current live value (price or NAV), queries daily_snapshots for the nearest
    historical date at the requested period offset and computes the percentage change.
    
    Returns:
      {
        "status": "success" | "no_history",
        "asset_type": asset_type,
        "symbol_or_scheme_code": symbol_or_scheme_code,
        "period": period.upper(),
        "current_value": current_value,
        "past_value": past_value,
        "past_date": past_date,
        "pct_change": pct_change,
        "formatted_summary": str
      }
    """
    clean_period = period.strip().lower()
    days_offset = PERIOD_DAYS_MAP.get(clean_period, 7)
    
    today = datetime.now(timezone.utc).date()
    target_date = (today - timedelta(days=days_offset)).strftime("%Y-%m-%d")
    
    past_record = get_historical_snapshot(
        asset_type=asset_type,
        symbol_or_scheme_code=symbol_or_scheme_code,
        target_date=target_date
    )
    
    if not past_record or past_record.get("value") is None or past_record.get("value") <= 0:
        return {
            "status": "no_history",
            "asset_type": asset_type,
            "symbol_or_scheme_code": symbol_or_scheme_code,
            "period": clean_period.upper(),
            "current_value": current_value,
            "past_value": None,
            "past_date": None,
            "pct_change": None,
            "formatted_summary": f"No historical {clean_period.upper()} snapshot recorded yet for {symbol_or_scheme_code}. Showing latest live value: ₹{current_value:,.2f}."
        }
        
    past_value = float(past_record["value"])
    past_date = past_record["snapshot_date"]
    
    pct_change = round(((current_value - past_value) / past_value) * 100.0, 2)
    direction_emoji = "📈" if pct_change >= 0 else "📉"
    sign = "+" if pct_change > 0 else ""
    
    summary = (
        f"{direction_emoji} **{clean_period.upper()} Return ({symbol_or_scheme_code}):** "
        f"`{sign}{pct_change}%` (from ₹{past_value:,.2f} on {past_date} to ₹{current_value:,.2f} today)"
    )
    
    return {
        "status": "success",
        "asset_type": asset_type,
        "symbol_or_scheme_code": symbol_or_scheme_code,
        "period": clean_period.upper(),
        "current_value": current_value,
        "past_value": past_value,
        "past_date": past_date,
        "pct_change": pct_change,
        "formatted_summary": summary
    }
