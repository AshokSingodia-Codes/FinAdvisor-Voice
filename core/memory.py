import sqlite3
import os
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'conversations.db')

def _get_utc_now():
    return datetime.now(timezone.utc).isoformat()

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_memory (
                conversation_id TEXT PRIMARY KEY,
                summary TEXT DEFAULT '',
                facts TEXT DEFAULT '{}',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
        # Fast query indexing
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, timestamp)')
        conn.commit()

init_db()

# --- Conversation Management ---

def create_conversation(conversation_id: Optional[str] = None, title: str = "New Chat") -> str:
    import uuid
    cid = conversation_id or str(uuid.uuid4())
    now = _get_utc_now()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at
        ''', (cid, title, now, now))
        cursor.execute('''
            INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
            VALUES (?, '', '{}', ?)
            ON CONFLICT(conversation_id) DO NOTHING
        ''', (cid, now))
        conn.commit()
    return cid

def get_conversations() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.title, c.created_at, c.updated_at,
                   COUNT(m.id) as message_count,
                   (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY timestamp DESC LIMIT 1) as last_message
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id
            ORDER BY c.updated_at DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?', (conversation_id,))
        conv_row = cursor.fetchone()
        if not conv_row:
            return None
        
        cursor.execute('''
            SELECT id, role, content, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        msg_rows = cursor.fetchall()
        
        cursor.execute('SELECT summary, facts FROM conversation_memory WHERE conversation_id = ?', (conversation_id,))
        mem_row = cursor.fetchone()
        
        facts_dict = {}
        summary_text = ""
        if mem_row:
            summary_text = mem_row["summary"] or ""
            try:
                facts_dict = json.loads(mem_row["facts"] or "{}")
            except Exception:
                facts_dict = {}
                
        return {
            "id": conv_row["id"],
            "title": conv_row["title"],
            "created_at": conv_row["created_at"],
            "updated_at": conv_row["updated_at"],
            "messages": [dict(m) for m in msg_rows],
            "facts": facts_dict,
            "summary": summary_text
        }

def rename_conversation(conversation_id: str, new_title: str) -> bool:
    new_title = new_title.strip()
    if not new_title:
        return False
    now = _get_utc_now()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ?
        ''', (new_title, now, conversation_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_conversation(conversation_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
        cursor.execute('DELETE FROM conversation_memory WHERE conversation_id = ?', (conversation_id,))
        cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- Message Storage ---

def add_message(conversation_id: str, role: str, content: str):
    now = _get_utc_now()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Ensure conversation exists
        cursor.execute('''
            INSERT INTO conversations (id, title, created_at, updated_at)
            VALUES (?, 'New Chat', ?, ?)
            ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at
        ''', (conversation_id, now, now))
        
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, role, content, now))
        
        cursor.execute('''
            INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
            VALUES (?, '', '{}', ?)
            ON CONFLICT(conversation_id) DO UPDATE SET updated_at = excluded.updated_at
        ''', (conversation_id, now))
        
        conn.commit()

def get_all_messages(conversation_id: str) -> List[Dict[str, str]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        rows = cursor.fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in rows]

def get_recent_messages(conversation_id: str, limit: int = 8) -> List[Dict[str, str]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (conversation_id, limit))
        rows = cursor.fetchall()
        # Return in chronological order
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

# --- Facts & Memory Management ---

def get_memory_facts(conversation_id: str) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT facts FROM conversation_memory WHERE conversation_id = ?', (conversation_id,))
        row = cursor.fetchone()
        if row and row["facts"]:
            try:
                return json.loads(row["facts"])
            except Exception:
                return {}
        return {}

def update_memory_facts(conversation_id: str, facts: Dict[str, Any]):
    now = _get_utc_now()
    facts_str = json.dumps(facts, ensure_ascii=False)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
            VALUES (?, '', ?, ?)
            ON CONFLICT(conversation_id) DO UPDATE SET facts = excluded.facts, updated_at = excluded.updated_at
        ''', (conversation_id, facts_str, now))
        conn.commit()

def get_memory_summary(conversation_id: str) -> str:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT summary FROM conversation_memory WHERE conversation_id = ?', (conversation_id,))
        row = cursor.fetchone()
        return row["summary"] if row and row["summary"] else ""

def update_memory_summary(conversation_id: str, summary: str):
    now = _get_utc_now()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
            VALUES (?, ?, '{}', ?)
            ON CONFLICT(conversation_id) DO UPDATE SET summary = excluded.summary, updated_at = excluded.updated_at
        ''', (conversation_id, summary, now))
        conn.commit()

def get_conversation_context(conversation_id: str, max_turns: int = 8) -> str:
    messages = get_recent_messages(conversation_id, limit=max_turns)
    facts = get_memory_facts(conversation_id)
    summary = get_memory_summary(conversation_id)
    
    sections = []
    
    # 1. Extracted Facts
    if facts:
        fact_lines = [f"- **{k}**: {v}" for k, v in facts.items()]
        sections.append("### Conversation Extracted User Financial Profile & Facts:\n" + "\n".join(fact_lines))
        
    # 2. Conversation Summary
    if summary:
        sections.append(f"### Earlier Conversation Summary:\n{summary}")
        
    # 3. Recent Messages
    if not messages:
        sections.append("### Recent Conversation History:\nNone (First interaction in this chat)")
    else:
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"[{role}]: {msg['content']}")
        sections.append("### Recent Conversation History (use this for 'this', 'that', and references):\n" + "\n".join(formatted))
        
    return "\n\n".join(sections)

# --- Heuristic & LLM Extraction ---

def _extract_facts_heuristic(text: str) -> Dict[str, str]:
    """Deterministic, instantaneous extraction for key Indian financial terms."""
    facts = {}
    lower = text.lower()
    
    # Age
    age_m = re.search(r'\b(\d{1,2})\s*[- ]*(?:year|yr)s?[- ]*old\b', lower) or re.search(r'\bage\s*(?:is|:)?\s*(\d{1,2})\b', lower)
    if age_m:
        facts["Age"] = f"{age_m.group(1)} years old"
        
    # Student
    if "student" in lower:
        facts["Occupation / Status"] = "Student"
        
    # Income / Salary
    income_m = re.search(r'(?:earn|salary|income|earning|make)\s*(?:of|is|around|about)?\s*([₹Rs\.]*\s*[\d,]+(?:\s*(?:lakh|lac|k|crore|cr|per month|/month|pm))?)', text, re.IGNORECASE)
    if income_m:
        val = income_m.group(1).strip()
        if "per month" not in val.lower() and "/month" not in val.lower() and "pm" not in val.lower() and "year" not in val.lower() and "per annum" not in val.lower():
            val += " per month"
        facts["Monthly Income"] = val
        
    # Expenses
    expense_m = re.search(r'(?:expense|expenses|spending|spend|cost)\s*(?:is|are|of|around|about)?\s*([₹Rs\.]*\s*[\d,]+(?:\s*(?:lakh|lac|k|crore|cr|per month|/month|pm))?)', text, re.IGNORECASE)
    if expense_m:
        facts["Monthly Expenses"] = expense_m.group(1).strip()
        
    # Savings
    savings_m = re.search(r'(?:saving|savings|saved|have)\s*(?:is|are|of|around|about)?\s*([₹Rs\.]*\s*[\d,]+(?:\s*(?:lakh|lac|k|crore|cr))?\s*(?:in savings|saved|available)?)', text, re.IGNORECASE)
    if savings_m and ("saving" in lower or "saved" in lower):
        facts["Savings"] = savings_m.group(1).strip()
    elif "1 lakh in savings" in lower or "1 lakh savings" in lower:
        facts["Savings"] = "₹1,00,000 (1 Lakh)"
        
    # Investment / SIP
    sip_m = re.search(r'(?:sip|invest|investing)\s*(?:of|is|around|about)?\s*([₹Rs\.]*\s*[\d,]+(?:\s*(?:lakh|lac|k|crore|cr|per month|/month|pm))?)', text, re.IGNORECASE)
    if sip_m and ("sip" in lower or "invest" in lower):
        facts["Investment Target / SIP"] = sip_m.group(1).strip()
        
    return facts

def _generate_title_heuristic(text: str) -> str:
    """Generate a clean 2-4 word title heuristically."""
    clean = text.strip()
    lower = clean.lower()
    
    if "student" in lower and ("budget" in lower or "earn" in lower or "money" in lower or "invest" in lower):
        return "Student Financial Planning"
    if "reliance" in lower:
        return "Reliance Stock Analysis"
    if "tcs" in lower:
        return "TCS Stock Analysis"
    if "hdfc" in lower:
        return "HDFC Bank Analysis"
    if "nifty" in lower or "sensex" in lower:
        return "Market Indices Discussion"
    if "sip" in lower or "mutual fund" in lower:
        return "SIP Investment Planning"
    if "tax" in lower or "taxation" in lower:
        return "Taxation & Planning"
    if "wacc" in lower or "cagr" in lower or "npv" in lower or "dcf" in lower:
        return "Financial Metrics Calculation"
    if "budget" in lower or "expense" in lower or "save" in lower:
        return "Personal Budgeting & Savings"
    if "portfolio" in lower:
        return "Portfolio Review & Allocation"
        
    words = clean.split()
    if len(words) <= 4:
        return clean[:35].title()
    return " ".join(words[:4]).title()

def extract_and_update_memory(conversation_id: str, user_message: str, assistant_response: str) -> str:
    """
    Extracts facts, updates memory, and generates title if needed.
    Guaranteed safe and fast.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title FROM conversations WHERE id = ?', (conversation_id,))
            row = cursor.fetchone()
            current_title = row["title"] if row else "New Chat"
        
        # 1. Heuristic Fact Extraction
        extracted_facts = _extract_facts_heuristic(user_message)
        
        # Update facts in DB if any found
        if extracted_facts:
            existing_facts = get_memory_facts(conversation_id)
            existing_facts.update(extracted_facts)
            update_memory_facts(conversation_id, existing_facts)
            
        # 2. Update Title if still 'New Chat'
        if not current_title or current_title == "New Chat":
            current_title = _generate_title_heuristic(user_message)
            rename_conversation(conversation_id, current_title)
            
        return current_title
    except Exception as e:
        print(f"Memory extraction notice: {e}")
        return "New Chat"
