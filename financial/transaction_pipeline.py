"""
financial/transaction_pipeline.py
---------------------------------
Token-efficient, staged personal-document financial analysis pipeline.

Architecture:
  1. Deterministic Pre-Structuring (0 tokens):
     Extracts transaction rows (Date + Description + Amount + Dr/Cr) using regex & keyword heuristics.
     Categorizes confident rows directly without touching any LLM.
  2. Batched LLM Structuring for Ambiguous Rows ONLY:
     Only unparsed / ambiguous rows are batched into a SINGLE structured-output call.
  3. SQL Storage & Pre-Aggregation:
     Persists extracted transactions to the SQL database (`document_transactions` table).
  4. Compact Summary Builder:
     Builds pre-aggregated server-side summary (<150 tokens) for downstream LLM advisory steps,
     preventing raw transaction lists or entire PDF texts from being sent to the LLM.
  5. Token Usage Logging:
     Tracks input/output token usage per document analyzed.
"""

import re
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from sqlalchemy import Table, Column, String, Float, Integer, Index, text

from core.memory import get_db_connection, metadata as _global_metadata, engine
from core.db import get_structured_fast_chat

# ---------------------------------------------------------------------------
# 1. SQL Table Schema — document_transactions
# ---------------------------------------------------------------------------

document_transactions_table = Table(
    "document_transactions",
    _global_metadata,
    Column("id", String(64), primary_key=True),
    Column("user_id", String(64), nullable=False),
    Column("document_id", String(64), nullable=False),
    Column("conversation_id", String(64), nullable=False),
    Column("tx_date", String(32), nullable=False),
    Column("description", String(512), nullable=False),
    Column("amount", Float, nullable=False),
    Column("tx_type", String(16), nullable=False), # 'debit' or 'credit'
    Column("category", String(64), nullable=False),
    Column("confidence", Float, nullable=False, default=1.0),
    Column("created_at", String(64), nullable=False),
    Index("idx_doc_tx_user_doc", "user_id", "document_id"),
)

_global_metadata.create_all(bind=engine, tables=[document_transactions_table])


# ---------------------------------------------------------------------------
# 2. Pydantic Schemas for Structured LLM Fallback
# ---------------------------------------------------------------------------

class StructuredTransaction(BaseModel):
    date: str = Field(description="Transaction date in YYYY-MM-DD or DD/MM/YYYY format")
    description: str = Field(description="Clean merchant or transaction description")
    amount: float = Field(description="Numerical transaction amount (positive float)")
    tx_type: str = Field(description="Must be 'debit' or 'credit'")
    category: str = Field(description="Category: Income, Food & Dining, Rent & Housing, Utilities, Investment, Shopping, Healthcare, Transport, Entertainment, Other")

class AmbiguousBatchExtraction(BaseModel):
    transactions: List[StructuredTransaction] = Field(
        default_factory=list,
        description="List of successfully structured transactions extracted from ambiguous text rows"
    )


# ---------------------------------------------------------------------------
# 3. Deterministic Heuristic Categorization Dictionary
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Income": ["salary", "payroll", "dividend", "interest cr", "upi cr", "refund", "cash deposit", "neft cr", "imps cr"],
    "Food & Dining": ["swiggy", "zomato", "restaurant", "cafe", "mcdonalds", "starbucks", "blinkit", "zepto", "instamart", "supermarket", "grocery", "dmart"],
    "Rent & Housing": ["rent", "maintenance", "landlord", "society", "housing"],
    "Utilities": ["electricity", "water", "bescom", "airtel", "jio", "broadband", "gas", "cylinder", "recharge"],
    "Investment": ["zerodha", "groww", "kuvera", "mutual fund", "sip", "camsonline", "kfintech", "nps", "ppf", "fd booking", "securities"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio", "retail", "zara", "h&m"],
    "Healthcare": ["pharmacy", "apollo", "medplus", "hospital", "clinic", "diagnostic", "1mg"],
    "Transport": ["uber", "ola", "metro", "fuel", "petrol", "hpcl", "bpcl", "iocl", "toll", "fastag"],
    "Entertainment": ["netflix", "spotify", "prime video", "hotstar", "pvr", "inox", "bookmyshow"]
}


# ---------------------------------------------------------------------------
# 4. Deterministic Pre-Structuring Engine (Zero Tokens)
# ---------------------------------------------------------------------------

DATE_REGEX = re.compile(r"(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b)", re.IGNORECASE)
AMOUNT_REGEX = re.compile(r"(?:₹|\$|Rs\.?|INR)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", re.IGNORECASE)

class DeterministicParser:
    @staticmethod
    def parse_line(line: str) -> Optional[Dict[str, Any]]:
        """Attempts to parse a single line or table row into a structured transaction deterministically."""
        cleaned = line.strip()
        if not cleaned or len(cleaned) < 8 or cleaned.startswith("---") or cleaned.startswith("| ---"):
            return None
        
        # Split markdown table cells if present
        if "|" in cleaned:
            cells = [c.strip() for c in cleaned.split("|") if c.strip()]
        else:
            cells = [cleaned]

        full_text = " ".join(cells)
        date_match = DATE_REGEX.search(full_text)
        if not date_match:
            return None

        tx_date = date_match.group(1)
        
        # Find amounts in string
        numbers = re.findall(r"(?:₹|\$|Rs\.?)?\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]{2,}(?:\.[0-9]{1,2})?)", full_text)
        if not numbers:
            return None
        
        # Extract amount
        try:
            raw_amt_str = numbers[-1].replace(",", "").strip()
            amount = float(raw_amt_str)
            if amount <= 0:
                return None
        except Exception:
            return None

        # Determine Dr/Cr
        lower = full_text.lower()
        if any(term in lower for term in [" cr", "(cr)", "credit", "deposit", "salary"]):
            tx_type = "credit"
        elif any(term in lower for term in [" dr", "(dr)", "debit", "withdrawal", "payment"]):
            tx_type = "debit"
        else:
            tx_type = "debit" # Default transaction is debit

        # Heuristic Categorization
        assigned_category = "Other"
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                assigned_category = cat
                break

        # Remove date and amount to clean description
        desc = full_text.replace(tx_date, "").replace(numbers[-1], "").strip(" |-")
        desc = re.sub(r"\s+", " ", desc)[:120]
        if not desc:
            desc = "Transaction"

        return {
            "date": tx_date,
            "description": desc,
            "amount": amount,
            "tx_type": tx_type,
            "category": assigned_category,
            "confidence": 1.0
        }


# ---------------------------------------------------------------------------
# 5. Token Usage Logging
# ---------------------------------------------------------------------------

class TokenUsageTracker:
    _logs: List[Dict[str, Any]] = []

    @classmethod
    def log_call(cls, document_id: str, deterministic_count: int, ambiguous_count: int, input_tokens: int, output_tokens: int):
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "document_id": document_id,
            "deterministic_rows_parsed": deterministic_count,
            "ambiguous_rows_batched": ambiguous_count,
            "llm_input_tokens": input_tokens,
            "llm_output_tokens": output_tokens,
            "total_llm_tokens": input_tokens + output_tokens
        }
        cls._logs.append(record)
        print(f"📊 [TokenTracker] Doc={document_id[:8]}.. | Deterministic={deterministic_count} rows (0 tokens) | LLM={ambiguous_count} rows ({input_tokens}+{output_tokens}={input_tokens+output_tokens} tokens)")

    @classmethod
    def get_summary_metrics(cls) -> Dict[str, Any]:
        if not cls._logs:
            return {"total_docs_analyzed": 0, "avg_tokens_per_doc": 0, "deterministic_rate_pct": 100.0}
        total_docs = len(cls._logs)
        total_tokens = sum(r["total_llm_tokens"] for r in cls._logs)
        total_det = sum(r["deterministic_rows_parsed"] for r in cls._logs)
        total_amb = sum(r["ambiguous_rows_batched"] for r in cls._logs)
        total_rows = max(total_det + total_amb, 1)
        return {
            "total_docs_analyzed": total_docs,
            "total_tokens_spent": total_tokens,
            "avg_tokens_per_doc": round(total_tokens / total_docs, 1),
            "total_rows_processed": total_rows,
            "deterministic_rows": total_det,
            "ambiguous_llm_rows": total_amb,
            "deterministic_rate_pct": round((total_det / total_rows) * 100, 2)
        }


# ---------------------------------------------------------------------------
# 6. End-to-End Staged Pipeline Execution
# ---------------------------------------------------------------------------

def process_and_store_document_transactions(
    raw_text: str,
    document_id: str,
    user_id: str,
    conversation_id: str
) -> Dict[str, Any]:
    """
    Executes the 2-stage transaction extraction pipeline:
      Stage 1: Deterministic regex parsing over lines/tables (0 tokens).
      Stage 2: Batched structured LLM call for ambiguous rows only.
      Stage 3: Persists structured records into SQL.
    """
    lines = raw_text.splitlines()
    confident_txs: List[Dict[str, Any]] = []
    ambiguous_lines: List[str] = []

    for line in lines:
        parsed = DeterministicParser.parse_line(line)
        if parsed:
            confident_txs.append(parsed)
        else:
            # Check if line looks like potential financial row
            stripped = line.strip()
            if any(char.isdigit() for char in stripped) and len(stripped) > 10 and not stripped.startswith("#"):
                if len(ambiguous_lines) < 20:  # Bound ambiguous batch ceiling
                    ambiguous_lines.append(stripped)

    # Stage 2: Batched LLM call ONLY if ambiguous lines exist
    llm_txs: List[Dict[str, Any]] = []
    in_tokens = 0
    out_tokens = 0

    if ambiguous_lines:
        try:
            batch_text = "\n".join(ambiguous_lines)
            chain = get_structured_fast_chat(AmbiguousBatchExtraction)
            prompt = f"Extract and structure any valid bank or financial transaction rows from the text below. Ignore non-transaction text.\n\nText:\n{batch_text}"
            res: AmbiguousBatchExtraction = chain.invoke(prompt)
            
            # Estimate tokens
            in_tokens = len(prompt.split()) * 2
            out_tokens = len(str(res).split()) * 2
            
            for t in res.transactions:
                llm_txs.append({
                    "date": t.date,
                    "description": t.description,
                    "amount": t.amount,
                    "tx_type": t.tx_type.lower() if t.tx_type.lower() in ("debit", "credit") else "debit",
                    "category": t.category,
                    "confidence": 0.9
                })
        except Exception as e:
            print(f"[pipeline] Ambiguous batch extraction skipped ({e})")

    TokenUsageTracker.log_call(
        document_id=document_id,
        deterministic_count=len(confident_txs),
        ambiguous_count=len(ambiguous_lines),
        input_tokens=in_tokens,
        output_tokens=out_tokens
    )

    all_txs = confident_txs + llm_txs

    # Stage 3: Store in SQL database
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    stored_count = 0

    if all_txs:
        with get_db_connection() as conn:
            for tx in all_txs:
                conn.execute(
                    document_transactions_table.insert().values(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        document_id=document_id,
                        conversation_id=conversation_id,
                        tx_date=tx["date"],
                        description=tx["description"],
                        amount=float(tx["amount"]),
                        tx_type=tx["tx_type"],
                        category=tx["category"],
                        confidence=float(tx["confidence"]),
                        created_at=now_str
                    )
                )
            conn.commit()
            stored_count = len(all_txs)

    return {
        "document_id": document_id,
        "total_transactions_stored": stored_count,
        "deterministic_count": len(confident_txs),
        "llm_extracted_count": len(llm_txs),
        "tokens_spent": in_tokens + out_tokens
    }


# ---------------------------------------------------------------------------
# 7. Compact Context Builder for Downstream LLM Advice (<150 tokens)
# ---------------------------------------------------------------------------

def build_compact_financial_summary(user_id: str, document_id: str, conversation_id: str) -> str:
    """
    Computes SQL aggregations directly and returns a compact (<150 token) structured summary.
    Downstream LLM advice nodes receive ONLY this summary, never raw transaction lists.
    """
    with get_db_connection() as conn:
        # Total Inflow (Credit)
        inflow_res = conn.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM document_transactions WHERE user_id=:u AND document_id=:d AND tx_type='credit'"),
            {"u": user_id, "d": document_id}
        ).scalar() or 0.0

        # Total Outflow (Debit)
        outflow_res = conn.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM document_transactions WHERE user_id=:u AND document_id=:d AND tx_type='debit'"),
            {"u": user_id, "d": document_id}
        ).scalar() or 0.0

        # Top 3 expense categories
        cat_rows = conn.execute(
            text("SELECT category, SUM(amount) as cat_total FROM document_transactions WHERE user_id=:u AND document_id=:d AND tx_type='debit' GROUP BY category ORDER BY cat_total DESC LIMIT 3"),
            {"u": user_id, "d": document_id}
        ).fetchall()

    net_savings = inflow_res - outflow_res
    savings_rate = (net_savings / inflow_res * 100) if inflow_res > 0 else 0.0

    top_cat_lines = []
    for row in cat_rows:
        top_cat_lines.append(f"  - {row[0]}: ₹{row[1]:,.2f}")
    top_cats_str = "\n".join(top_cat_lines) if top_cat_lines else "  - Miscellaneous: ₹0.00"

    summary = (
        f"📊 **Aggregated Financial Profile (from uploaded document)**:\n"
        f"- Total Inflow (Income/Credits): ₹{inflow_res:,.2f}\n"
        f"- Total Outflow (Expenses/Debits): ₹{outflow_res:,.2f}\n"
        f"- Net Monthly Savings: ₹{net_savings:,.2f} ({savings_rate:.1f}% Savings Rate)\n"
        f"- Top Expense Categories:\n{top_cats_str}"
    )
    return summary
