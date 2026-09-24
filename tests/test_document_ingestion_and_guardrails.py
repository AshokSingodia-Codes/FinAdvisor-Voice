import pytest
from core.document_store import (
    _format_table_as_markdown,
    _chunk_text,
    validate_financial_domain,
    NonFinancialDocumentError
)

def test_format_table_as_markdown():
    table_data = [
        ["Line Item", "FY25 (INR)", "FY26 (INR)", "Growth %"],
        ["Revenue", "1200", "1560", "+30%"],
        ["Net Profit", "180", "300", "+66.7%"]
    ]
    md = _format_table_as_markdown(table_data)
    assert "| Line Item | FY25 (INR) | FY26 (INR) | Growth % |" in md
    assert "| --- | --- | --- | --- |" in md
    assert "| Revenue | 1200 | 1560 | +30% |" in md
    assert "| Net Profit | 180 | 300 | +66.7% |" in md

def test_table_and_math_aware_chunking():
    doc_content = """# FINANCIAL PERFORMANCE REPORT 2026
Company: Apex Innovations Pvt Ltd

### Financial Data Table:
| Metric | 2025 | 2026 | Change |
| --- | --- | --- | --- |
| EBITDA | 450M | 620M | +37.7% |
| Operating Cash Flow | 310M | 480M | +54.8% |

### Financial Math & Formulas:
- Return on Equity (ROE) = Net Income / Shareholder Equity = 120 / 600 = 20.0%
- Weighted Average Cost of Capital (WACC) = (E/V * Re) + (D/V * Rd * (1 - T)) = 9.45%
"""
    chunks = _chunk_text(doc_content, chunk_size=800, overlap=100)
    assert len(chunks) >= 1
    # Check that table and formulas are retained in the chunk text
    combined_chunks = " ".join(chunks)
    assert "EBITDA" in combined_chunks
    assert "Operating Cash Flow" in combined_chunks
    assert "Weighted Average Cost of Capital" in combined_chunks

def test_validate_financial_domain_accepts_financial_text():
    fin_text = "Balance sheet reveals gross revenue of Rs 50,00,000 with net profit of Rs 12,00,000 and GST payable."
    assert validate_financial_domain(fin_text, "annual_report.pdf") is True

def test_validate_financial_domain_rejects_non_financial_text():
    non_fin_text = "The quick brown fox jumps over the lazy sleeping dog in the enchanted forest during the autumn afternoon."
    assert validate_financial_domain(non_fin_text, "story.txt") is False
