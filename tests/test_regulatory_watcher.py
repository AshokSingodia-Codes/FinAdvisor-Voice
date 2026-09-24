import os
import json
import pytest
from core.regulatory_watcher import check_and_sync_financial_rules, _load_sync_log, _save_sync_log, _LOG_PATH

def test_regulatory_sync_execution(mocker):
    # Mock Neo4jVector to test the logic without requiring external connection in unit test
    mocker.patch('langchain_neo4j.Neo4jVector.from_existing_index')
    
    # Clean previous log test state
    if os.path.exists(_LOG_PATH):
        try:
            os.remove(_LOG_PATH)
        except Exception:
            pass
            
    res = check_and_sync_financial_rules()
    assert res["status"] in ["SUCCESS", "ALREADY_UP_TO_DATE"]
    assert "month" in res
    
    # Run a second time to ensure idempotency (does not duplicate syncs in the same month)
    res2 = check_and_sync_financial_rules()
    assert res2["status"] == "ALREADY_UP_TO_DATE"
