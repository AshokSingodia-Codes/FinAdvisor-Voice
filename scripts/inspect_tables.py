import pdfplumber
import json
import os
from pydantic import BaseModel
from typing import List, Optional

class FinancialTable(BaseModel):
    table_id: str
    title: str
    page: int
    section: str
    unit: str
    currency: str
    columns: List[str]
    rows: List[List[str]]
    footnotes: List[str]
    source_document: str

def is_financial_table(table: List[List[str]]) -> bool:
    """Heuristic to determine if a table is financial (contains numbers and multiple rows)."""
    if not table or len(table) < 2: return False
    
    # Check if any cell has numbers
    has_numbers = False
    for row in table:
        for cell in row:
            if cell and any(char.isdigit() for char in cell):
                has_numbers = True
                break
        if has_numbers: break
        
    return has_numbers

def extract_tables():
    pdf_path = "Annual Report/NASDAQ_AAPL_2024.pdf"
    output_path = "reports/table_extraction_report.json"
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return
        
    extracted_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for i, raw_table in enumerate(tables):
                # Clean table (remove None values)
                clean_table = [[str(cell).strip() if cell else "" for cell in row] for row in raw_table]
                
                if is_financial_table(clean_table):
                    # Basic extraction
                    columns = clean_table[0] if len(clean_table) > 0 else []
                    rows = clean_table[1:] if len(clean_table) > 1 else []
                    
                    # Heuristics for units/currency (simplified)
                    currency = "USD" if any("$" in cell for row in clean_table for cell in row) else "Unknown"
                    unit = "Millions" if "millions" in page.extract_text().lower() else "Unknown"
                    
                    fin_table = FinancialTable(
                        table_id=f"table_{page_num}_{i}",
                        title=f"Table from Page {page_num}",
                        page=page_num,
                        section="Unknown", # Requires advanced heuristic or LLM
                        unit=unit,
                        currency=currency,
                        columns=columns,
                        rows=rows,
                        footnotes=[],
                        source_document="NASDAQ_AAPL_2024.pdf"
                    )
                    
                    extracted_tables.append(fin_table.model_dump())
                    
                    # Just grab first 5 for the inspection report
                    if len(extracted_tables) >= 5:
                        break
            if len(extracted_tables) >= 5:
                break
                
    with open(output_path, "w") as f:
        json.dump(extracted_tables, f, indent=2)
        
    print(f"Successfully extracted {len(extracted_tables)} financial tables to {output_path}")

if __name__ == "__main__":
    extract_tables()
