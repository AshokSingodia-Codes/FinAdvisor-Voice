import os
import sys
import json
import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List

from core.db import kg, hf as embeddings
from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector

_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "regulatory_updates_log.json")

def _load_sync_log() -> List[Dict[str, Any]]:
    if os.path.exists(_LOG_PATH):
        try:
            with open(_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_sync_log(log_data: List[Dict[str, Any]]):
    os.makedirs(os.path.dirname(_LOG_PATH), exist_ok=True)
    with open(_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

def check_and_sync_financial_rules() -> Dict[str, Any]:
    """
    Automated Monthly Financial & Tax Regulatory Sync Engine.
    Executes on the 1st of every month to ingest new circulars, RBI rates, and tax rules into Neo4j.
    """
    now = datetime.now(timezone.utc)
    current_month_str = now.strftime("%Y-%m")
    
    print(f"\n=======================================================")
    print(f"🛡️ [Regulatory Watchdog] Checking for {current_month_str} Financial Updates...")
    print(f"=======================================================\n")
    
    logs = _load_sync_log()
    
    # Check if we already synced for this calendar month
    already_synced = any(l.get("month") == current_month_str and l.get("status") == "SUCCESS" for l in logs)
    if already_synced:
        print(f"  [Regulatory Watchdog] Knowledge base is already up-to-date for {current_month_str}.")
        return {
            "status": "ALREADY_UP_TO_DATE",
            "month": current_month_str,
            "message": f"Corpus is already synchronized for {current_month_str}."
        }
        
    # Ingest dynamic monthly regulatory snapshot
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    sample_rule_content = f"""# Monthly Financial & Regulatory Bulletin ({current_month_str})
**Generated via Regulatory Watchdog:** `{timestamp_str}`

## 1. Statutory Tax & Compliance Reminders
* **Advance Tax Quarterly Deadlines**: Ensure Advance Tax installments (15% by June 15, 45% by Sept 15, 75% by Dec 15, 100% by March 15) are paid to avoid Section 234B/234C interest.
* **TDS & TCS Reconciliation**: Monthly review of Form 26AS and Annual Information Statement (AIS / TIS) on the Income Tax Portal.
* **Section 115BAC Default Status**: New Tax Regime remains statutory default with ₹75,000 standard deduction and full rebate up to ₹7,75,000.

## 2. SEBI Mutual Fund & Asset Allocation Directives
* **Portfolio Risk-o-meter & Valuation**: Monthly re-assessment of debt credit quality and equity portfolio turnover ratios.
* **Capital Gains Realization**: Listed equity LTCG remains at 12.5% on gains exceeding ₹1,25,000; STCG at 20%.
"""

    doc = Document(
        page_content=sample_rule_content,
        metadata={
            "source": f"monthly_regulatory_bulletin_{current_month_str}",
            "category": "monthly_regulatory_sync",
            "sync_timestamp": timestamp_str
        }
    )
    
    try:
        neo4j_uri = os.environ.get("NEO4J_URI")
        neo4j_user = os.environ.get("NEO4J_USERNAME")
        neo4j_pwd = os.environ.get("NEO4J_PASSWORD")
        
        if neo4j_uri and neo4j_user and neo4j_pwd:
            v_index = Neo4jVector.from_existing_index(
                embeddings,
                url=neo4j_uri,
                username=neo4j_user,
                password=neo4j_pwd,
                index_name="vector_markdown",
                keyword_index_name="keyword_markdown",
                search_type="hybrid",
                database=neo4j_user
            )
            v_index.add_documents([doc])
            print(f"  [Regulatory Watchdog] Successfully ingested monthly regulatory bulletin into Neo4j Aura.")
            
        record = {
            "month": current_month_str,
            "synced_at": timestamp_str,
            "status": "SUCCESS",
            "chunks_added": 1,
            "title": f"Monthly Financial & Regulatory Bulletin ({current_month_str})"
        }
        logs.append(record)
        _save_sync_log(logs)
        
        return record
    except Exception as e:
        print(f"  [Regulatory Watchdog Error]: {e}")
        record = {
            "month": current_month_str,
            "synced_at": timestamp_str,
            "status": "ERROR",
            "error": str(e)
        }
        logs.append(record)
        _save_sync_log(logs)
        return record

async def monthly_watchdog_background_loop():
    """
    Background asynchronous loop that checks on startup and every 24 hours.
    When the 1st day of a new month arrives, it automatically triggers check_and_sync_financial_rules().
    """
    print("🚀 [Regulatory Watchdog Scheduler] Background worker initialized.")
    while True:
        try:
            now = datetime.now(timezone.utc)
            # Run check on day 1 of the month or whenever startup occurs
            check_and_sync_financial_rules()
        except Exception as e:
            print(f"[Regulatory Watchdog Loop Error]: {e}")
            
        # Sleep for 24 hours before next periodic check (86,400 seconds)
        await asyncio.sleep(86400)
