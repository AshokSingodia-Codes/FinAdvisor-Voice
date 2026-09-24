import time
from tools.mf_lookup import search_mutual_funds, format_mf_summary
from nodes.market_data import fetch_live_data

def test_search_mutual_funds():
    t0 = time.time()
    results = search_mutual_funds("Parag Parikh Flexi Cap")
    elapsed_ms = (time.time() - t0) * 1000
    
    assert len(results) >= 1
    assert "Parag Parikh" in results[0]["scheme_name"]
    assert results[0]["category"] == "Flexi Cap Fund"
    assert results[0]["expense_ratio_direct_pct"] == 0.62
    assert elapsed_ms < 10.0  # Must be sub-10ms

def test_fetch_live_data_mutual_fund():
    state = {
        "current_question": "Tell me about Parag Parikh Flexi Cap Fund",
        "original_question": "Tell me about Parag Parikh Flexi Cap Fund",
        "chat_history": []
    }
    
    res = fetch_live_data(state)
    assert len(res["retrieved_context"]) >= 1
    assert "Parag Parikh Flexi Cap Fund" in res["retrieved_context"][0]
    assert "Direct:" in res["retrieved_context"][0]
