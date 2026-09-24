import os
import json
from typing import Dict, Any, List, Optional

_MF_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "top_mutual_funds_dataset.json")
_CACHE = None

def _load_mf_data() -> List[Dict[str, Any]]:
    global _CACHE
    if _CACHE is None:
        try:
            with open(_MF_DATA_PATH, "r", encoding="utf-8") as f:
                _CACHE = json.load(f)
        except Exception as e:
            print(f"[mf_lookup] Error loading mutual fund dataset: {e}")
            _CACHE = []
    return _CACHE

def search_mutual_funds(query: str) -> List[Dict[str, Any]]:
    """
    High-speed deterministic search across Indian Mutual Funds dataset.
    Returns matching schemes with category, returns, expense ratio, AUM, and holdings.
    Latency: < 2ms.
    """
    data = _load_mf_data()
    q_lower = query.lower()
    matches = []
    
    for scheme in data:
        name = scheme.get("scheme_name", "").lower()
        category = scheme.get("category", "").lower()
        fund_house = scheme.get("fund_house", "").lower()
        
        # Check if query keywords match scheme name, category, or fund house
        if any(term in name or term in category or term in fund_house for term in q_lower.split()):
            matches.append(scheme)
            
    return matches

def format_mf_summary(scheme: Dict[str, Any]) -> str:
    """Formats mutual fund metrics into a clean markdown card."""
    name = scheme.get("scheme_name")
    cat = scheme.get("category")
    house = scheme.get("fund_house")
    bench = scheme.get("benchmark")
    aum = scheme.get("aum_crores")
    ter_dir = scheme.get("expense_ratio_direct_pct")
    ter_reg = scheme.get("expense_ratio_regular_pct")
    r1 = scheme.get("returns_1yr_cagr_pct")
    r3 = scheme.get("returns_3yr_cagr_pct")
    r5 = scheme.get("returns_5yr_cagr_pct")
    mgr = scheme.get("fund_manager")
    exit_load = scheme.get("exit_load")
    holdings = ", ".join(scheme.get("top_holdings", []))
    
    return f"""### 📊 {name}
* **Category:** {cat} | **Fund House:** {house}
* **Benchmark:** {bench} | **AUM:** ₹{aum:,} Crores
* **Total Expense Ratio (TER):** Direct: `{ter_dir}%` | Regular: `{ter_reg}%` (Direct saves `{round(ter_reg - ter_dir, 2)}%` annually)
* **Historical CAGR Returns:** 1-Year: `+{r1}%` | 3-Year: `+{r3}%` | 5-Year: `+{r5}%`
* **Top Holdings:** {holdings}
* **Exit Load:** {exit_load}
* **Fund Manager(s):** {mgr}
"""

if __name__ == "__main__":
    results = search_mutual_funds("Parag Parikh")
    if results:
        print(format_mf_summary(results[0]))
