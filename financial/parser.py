from pydantic import BaseModel
from typing import List

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

class Evidence(BaseModel):
    content: str
    source_type: str # 'vector', 'graph', 'table', 'calculation'
    document: str
    page: int
    section: str
    chunk_id: str
    table_id: str
    relevance_score: float
