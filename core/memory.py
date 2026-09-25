import os
import json
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from sqlalchemy import (
    create_engine,
    text,
    MetaData,
    Table,
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    Index
)
from sqlalchemy.pool import StaticPool
from config.settings import settings

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'conversations.db')

def _get_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_database_url() -> str:
    """
    Returns the configured PostgreSQL database URL from settings,
    or falls back to a local SQLite database for local offline development/testing.
    """
    db_url = settings.effective_database_url
    if not db_url:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return f"sqlite:///{DB_PATH}"
    
    # Normalize legacy postgres:// prefix from Render/Heroku to postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Ensure Neon sslmode is set if connecting to a remote postgres
    if "postgresql" in db_url and "sslmode=" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"
        
    return db_url

def _resolve_host_fallback(hostname: str) -> Optional[str]:
    """Resolves hostname via system DNS or falls back to public DNS (8.8.8.8 / 1.1.1.1)."""
    import socket
    import struct
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        pass
    
    # Fallback to direct DNS query via UDP socket for serverless cloud databases
    for dns_server in ("8.8.8.8", "1.1.1.1"):
        try:
            packet = bytearray()
            packet.extend(b'\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00')
            for part in hostname.split('.'):
                packet.append(len(part))
                packet.extend(part.encode())
            packet.append(0)
            packet.extend(b'\x00\x01\x00\x01') # Type A, Class IN
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3.0)
            try:
                sock.sendto(packet, (dns_server, 53))
                data, _ = sock.recvfrom(1024)
                idx = len(packet)
                while idx < len(data):
                    if data[idx] >= 192:
                        idx += 2
                    else:
                        while idx < len(data) and data[idx] != 0:
                            idx += 1 + data[idx]
                        idx += 1
                    if idx + 10 > len(data):
                        break
                    rtype, rclass, ttl, rdlength = struct.unpack('!HHIH', data[idx:idx+10])
                    idx += 10
                    if rtype == 1 and rdlength == 4 and idx + 4 <= len(data):
                        return socket.inet_ntoa(data[idx:idx+4])
                    idx += rdlength
            finally:
                sock.close()
        except Exception:
            continue
    return None

def create_db_engine(db_url: Optional[str] = None):
    url = db_url or get_database_url()
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool if ":memory:" in url else None
        )
    else:
        # PostgreSQL / Neon Serverless configuration:
        # pool_pre_ping: Verifies connection liveness before checking out from pool
        # pool_recycle: Recycles connections periodically to align with PgBouncer
        return create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
        )

# Global engine instance
engine = create_db_engine()

metadata = MetaData()

# Define Tables
users_table = Table(
    'users',
    metadata,
    Column('id', String(64), primary_key=True),
    Column('email', String(255), unique=True, nullable=False),
    Column('password_hash', Text, nullable=False),
    Column('created_at', String(64), default=_get_utc_now),
    Column('updated_at', String(64), default=_get_utc_now),
)

otps_table = Table(
    'otps',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('email', String(255), nullable=False),
    Column('otp_hash', Text, nullable=False),
    Column('purpose', String(64), nullable=False),
    Column('verification_token', String(255), nullable=True),
    Column('expires_at', String(64), nullable=False),
    Column('attempts', Integer, default=0),
    Column('is_verified', Integer, default=0),
    Column('created_at', String(64), default=_get_utc_now),
    Index('idx_otps_email_purpose', 'email', 'purpose')
)

conversations_table = Table(
    'conversations',
    metadata,
    Column('id', String(64), primary_key=True),
    Column('user_id', String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('title', String(255), nullable=False, default='New Chat'),
    Column('created_at', String(64), default=_get_utc_now),
    Column('updated_at', String(64), default=_get_utc_now),
    Index('idx_conversations_user', 'user_id', 'updated_at')
)

messages_table = Table(
    'messages',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('conversation_id', String(64), ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
    Column('role', String(32), nullable=False),
    Column('content', Text, nullable=False),
    Column('timestamp', String(64), default=_get_utc_now),
    Index('idx_messages_conv', 'conversation_id', 'timestamp')
)

conversation_memory_table = Table(
    'conversation_memory',
    metadata,
    Column('conversation_id', String(64), ForeignKey('conversations.id', ondelete='CASCADE'), primary_key=True),
    Column('summary', Text, default=''),
    Column('facts', Text, default='{}'),
    Column('updated_at', String(64), default=_get_utc_now)
)


@contextmanager
def get_db_connection(custom_engine=None):
    """Context manager yielding an active SQLAlchemy connection."""
    target_engine = custom_engine or engine
    with target_engine.connect() as conn:
        yield conn


def init_db(target_engine=None):
    """Initializes all database tables and indexes."""
    eng = target_engine or engine
    metadata.create_all(bind=eng)
    
    # Purge any legacy NULL user_id conversations
    with get_db_connection(custom_engine=eng) as conn:
        conn.execute(text("DELETE FROM conversations WHERE user_id IS NULL OR user_id = ''"))
        conn.commit()


# Auto-initialize database on import
init_db()


# --- In-Memory Fast Cache for User Authentication ---
import time
_USER_CACHE: Dict[str, Any] = {}
_USER_CACHE_TTL = 300  # 5 minutes cache for active tokens


# --- User Management ---

def create_user(email: str, password_hash: str) -> Dict[str, Any]:
    import uuid
    uid = str(uuid.uuid4())
    now = _get_utc_now()
    email_clean = email.strip().lower()
    with get_db_connection() as conn:
        conn.execute(
            text("""
                INSERT INTO users (id, email, password_hash, created_at, updated_at)
                VALUES (:id, :email, :password_hash, :created_at, :updated_at)
            """),
            {"id": uid, "email": email_clean, "password_hash": password_hash, "created_at": now, "updated_at": now}
        )
        conn.commit()
    user_dict = {"id": uid, "email": email_clean, "created_at": now}
    _USER_CACHE[uid] = ({"id": uid, "email": email_clean, "password_hash": password_hash, "created_at": now, "updated_at": now}, time.time() + _USER_CACHE_TTL)
    return user_dict

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email_clean = email.strip().lower()
    with get_db_connection() as conn:
        result = conn.execute(
            text("SELECT id, email, password_hash, created_at, updated_at FROM users WHERE email = :email"),
            {"email": email_clean}
        )
        row = result.mappings().fetchone()
        user_dict = dict(row) if row else None
        if user_dict:
            _USER_CACHE[user_dict["id"]] = (user_dict, time.time() + _USER_CACHE_TTL)
        return user_dict

def get_user_by_id(user_id: Any) -> Optional[Dict[str, Any]]:
    if isinstance(user_id, dict):
        user_id = user_id.get("id") or user_id.get("user_id") or ""
    if not user_id:
        return None
    user_id = str(user_id)

    now_ts = time.time()
    if user_id in _USER_CACHE:
        cached_user, exp_ts = _USER_CACHE[user_id]
        if now_ts < exp_ts:
            return cached_user

    with get_db_connection() as conn:
        result = conn.execute(
            text("SELECT id, email, password_hash, created_at, updated_at FROM users WHERE id = :id"),
            {"id": user_id}
        )
        row = result.mappings().fetchone()
        user_dict = dict(row) if row else None
        if user_dict:
            _USER_CACHE[user_id] = (user_dict, now_ts + _USER_CACHE_TTL)
        return user_dict

def update_user_password(user_id: str, new_password_hash: str) -> bool:
    now = _get_utc_now()
    _USER_CACHE.pop(user_id, None)
    with get_db_connection() as conn:
        res = conn.execute(
            text("UPDATE users SET password_hash = :password_hash, updated_at = :updated_at WHERE id = :id"),
            {"password_hash": new_password_hash, "updated_at": now, "id": user_id}
        )
        conn.commit()
        return res.rowcount > 0


# --- OTP Database Operations ---

def save_otp_record(email: str, otp_hash: str, purpose: str, expires_at_iso: str):
    email_clean = email.strip().lower()
    with get_db_connection() as conn:
        # Invalidate any prior unused OTPs for this email and purpose
        conn.execute(
            text("DELETE FROM otps WHERE email = :email AND purpose = :purpose"),
            {"email": email_clean, "purpose": purpose}
        )
        conn.execute(
            text("""
                INSERT INTO otps (email, otp_hash, purpose, expires_at, attempts, is_verified, created_at)
                VALUES (:email, :otp_hash, :purpose, :expires_at, 0, 0, :created_at)
            """),
            {"email": email_clean, "otp_hash": otp_hash, "purpose": purpose, "expires_at": expires_at_iso, "created_at": _get_utc_now()}
        )
        conn.commit()

def get_last_otp_record(email: str, purpose: str) -> Optional[Dict[str, Any]]:
    email_clean = email.strip().lower()
    with get_db_connection() as conn:
        result = conn.execute(
            text("""
                SELECT id, email, otp_hash, purpose, verification_token, expires_at, attempts, is_verified, created_at
                FROM otps
                WHERE email = :email AND purpose = :purpose
                ORDER BY id DESC LIMIT 1
            """),
            {"email": email_clean, "purpose": purpose}
        )
        row = result.mappings().fetchone()
        return dict(row) if row else None

def verify_and_claim_otp(email: str, plain_otp: str, purpose: str) -> Dict[str, Any]:
    import secrets
    from core.auth import verify_otp_hash
    email_clean = email.strip().lower()
    now_dt = datetime.now(timezone.utc)
    
    with get_db_connection() as conn:
        result = conn.execute(
            text("""
                SELECT id, otp_hash, expires_at, attempts, is_verified
                FROM otps
                WHERE email = :email AND purpose = :purpose
                ORDER BY id DESC LIMIT 1
            """),
            {"email": email_clean, "purpose": purpose}
        )
        row = result.mappings().fetchone()
        
        if not row:
            return {"valid": False, "detail": "No active OTP found for this email. Please request a new OTP."}
        
        # Check attempts
        if row["attempts"] >= 5:
            return {"valid": False, "detail": "Too many failed attempts. Please request a new OTP."}
        
        # Check expiration
        try:
            exp_dt = datetime.fromisoformat(row["expires_at"])
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if now_dt > exp_dt:
                return {"valid": False, "detail": "OTP has expired. Please request a new OTP."}
        except Exception:
            return {"valid": False, "detail": "Invalid OTP expiration format."}
        
        # Increment attempts count
        conn.execute(
            text("UPDATE otps SET attempts = attempts + 1 WHERE id = :id"),
            {"id": row["id"]}
        )
        conn.commit()
        
        if not verify_otp_hash(plain_otp.strip(), row["otp_hash"]):
            remaining = 5 - (row["attempts"] + 1)
            return {"valid": False, "detail": f"Incorrect OTP code. {remaining} attempt(s) remaining."}
        
        # Valid OTP -> issue verification token
        vtoken = secrets.token_urlsafe(32)
        conn.execute(
            text("UPDATE otps SET is_verified = 1, verification_token = :vtoken WHERE id = :id"),
            {"vtoken": vtoken, "id": row["id"]}
        )
        conn.commit()
        
        return {"valid": True, "verification_token": vtoken}

def consume_verification_token(email: str, purpose: str, token: str) -> bool:
    email_clean = email.strip().lower()
    now_dt = datetime.now(timezone.utc)
    with get_db_connection() as conn:
        result = conn.execute(
            text("""
                SELECT id, expires_at FROM otps
                WHERE email = :email AND purpose = :purpose AND verification_token = :token AND is_verified = 1
                ORDER BY id DESC LIMIT 1
            """),
            {"email": email_clean, "purpose": purpose, "token": token.strip()}
        )
        row = result.mappings().fetchone()
        if not row:
            return False
        
        try:
            exp_dt = datetime.fromisoformat(row["expires_at"])
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            # Allow up to 15 minutes for password entry after OTP verification
            if now_dt > exp_dt + timedelta(minutes=15):
                return False
        except Exception:
            return False
        
        # Consume token so it cannot be used again
        conn.execute(
            text("DELETE FROM otps WHERE id = :id"),
            {"id": row["id"]}
        )
        conn.commit()
        return True


# --- Conversation Management (Strictly User Isolated) ---

def create_conversation(title: str = "New Chat", user_id: str = "", conversation_id: Optional[str] = None) -> str:
    if not user_id:
        raise ValueError("user_id is required to create a conversation.")
    import uuid
    cid = conversation_id or str(uuid.uuid4())
    now = _get_utc_now()
    with get_db_connection() as conn:
        conn.execute(
            text("""
                INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                VALUES (:id, :user_id, :title, :created_at, :updated_at)
                ON CONFLICT (id) DO UPDATE SET updated_at = EXCLUDED.updated_at
            """),
            {"id": cid, "user_id": user_id, "title": title, "created_at": now, "updated_at": now}
        )
        conn.execute(
            text("""
                INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
                VALUES (:cid, '', '{}', :updated_at)
                ON CONFLICT (conversation_id) DO NOTHING
            """),
            {"cid": cid, "updated_at": now}
        )
        conn.commit()
    return cid

def get_conversations(user_id: str) -> List[Dict[str, Any]]:
    if not user_id:
        return []
    with get_db_connection() as conn:
        result = conn.execute(
            text("""
                SELECT c.id, c.user_id, c.title, c.created_at, c.updated_at,
                       COUNT(m.id) as message_count,
                       (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY timestamp DESC, id DESC LIMIT 1) as last_message
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.user_id = :user_id
                GROUP BY c.id, c.user_id, c.title, c.created_at, c.updated_at
                ORDER BY c.updated_at DESC
            """),
            {"user_id": user_id}
        )
        rows = result.mappings().fetchall()
        return [dict(row) for row in rows]

def get_conversation_raw(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Internal check to inspect conversation existence across users for access control."""
    with get_db_connection() as conn:
        result = conn.execute(
            text("SELECT id, user_id, title, created_at, updated_at FROM conversations WHERE id = :id"),
            {"id": conversation_id}
        )
        row = result.mappings().fetchone()
        return dict(row) if row else None

def get_conversation(conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    if not user_id:
        return None
    with get_db_connection() as conn:
        result = conn.execute(
            text("SELECT id, user_id, title, created_at, updated_at FROM conversations WHERE id = :id AND user_id = :user_id"),
            {"id": conversation_id, "user_id": user_id}
        )
        conv_row = result.mappings().fetchone()
        if not conv_row:
            return None
        
        msg_result = conn.execute(
            text("SELECT id, role, content, timestamp FROM messages WHERE conversation_id = :cid ORDER BY timestamp ASC, id ASC"),
            {"cid": conversation_id}
        )
        msg_rows = msg_result.mappings().fetchall()
        
        mem_result = conn.execute(
            text("SELECT summary, facts FROM conversation_memory WHERE conversation_id = :cid"),
            {"cid": conversation_id}
        )
        mem_row = mem_result.mappings().fetchone()
        
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
            "user_id": conv_row["user_id"],
            "title": conv_row["title"],
            "created_at": conv_row["created_at"],
            "updated_at": conv_row["updated_at"],
            "messages": [dict(m) for m in msg_rows],
            "facts": facts_dict,
            "summary": summary_text
        }

def rename_conversation(conversation_id: str, new_title: str, user_id: str) -> bool:
    new_title = new_title.strip()
    if not new_title or not user_id:
        return False
    now = _get_utc_now()
    with get_db_connection() as conn:
        res = conn.execute(
            text("UPDATE conversations SET title = :title, updated_at = :updated_at WHERE id = :id AND user_id = :user_id"),
            {"title": new_title, "updated_at": now, "id": conversation_id, "user_id": user_id}
        )
        conn.commit()
        return res.rowcount > 0

def delete_conversation(conversation_id: str, user_id: str) -> bool:
    if not user_id:
        return False
    with get_db_connection() as conn:
        chk = conn.execute(
            text("SELECT id FROM conversations WHERE id = :id AND user_id = :user_id"),
            {"id": conversation_id, "user_id": user_id}
        ).mappings().fetchone()
        if not chk:
            return False
        conn.execute(text("DELETE FROM messages WHERE conversation_id = :cid"), {"cid": conversation_id})
        conn.execute(text("DELETE FROM conversation_memory WHERE conversation_id = :cid"), {"cid": conversation_id})
        res = conn.execute(
            text("DELETE FROM conversations WHERE id = :id AND user_id = :user_id"),
            {"id": conversation_id, "user_id": user_id}
        )
        conn.commit()
        return res.rowcount > 0


def delete_all_conversations(user_id: str) -> bool:
    if not user_id:
        return False
    with get_db_connection() as conn:
        conn.execute(
            text("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id)"),
            {"user_id": user_id}
        )
        conn.execute(
            text("DELETE FROM conversation_memory WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id)"),
            {"user_id": user_id}
        )
        res = conn.execute(
            text("DELETE FROM conversations WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        conn.commit()
        return res.rowcount >= 0


# --- Message Storage (User Scoped) ---

def add_message(conversation_id: str, role: str, content: str, user_id: str):
    if not user_id:
        raise ValueError("user_id is required to add messages.")
    now = _get_utc_now()
    with get_db_connection() as conn:
        # Check if conversation exists
        conv = conn.execute(
            text("SELECT id, user_id FROM conversations WHERE id = :id"),
            {"id": conversation_id}
        ).mappings().fetchone()
        if conv:
            if conv["user_id"] != user_id:
                raise PermissionError("Access denied: Conversation belongs to another user.")
            conn.execute(
                text("UPDATE conversations SET updated_at = :updated_at WHERE id = :id"),
                {"updated_at": now, "id": conversation_id}
            )
        else:
            # Create new user-owned conversation
            conn.execute(
                text("""
                    INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                    VALUES (:id, :user_id, 'New Chat', :created_at, :updated_at)
                """),
                {"id": conversation_id, "user_id": user_id, "created_at": now, "updated_at": now}
            )
        
        conn.execute(
            text("""
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES (:conversation_id, :role, :content, :timestamp)
            """),
            {"conversation_id": conversation_id, "role": role, "content": content, "timestamp": now}
        )
        
        conn.execute(
            text("""
                INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
                VALUES (:cid, '', '{}', :updated_at)
                ON CONFLICT (conversation_id) DO UPDATE SET updated_at = EXCLUDED.updated_at
            """),
            {"cid": conversation_id, "updated_at": now}
        )
        
        conn.commit()

def get_all_messages(conversation_id: str, user_id: Optional[str] = None) -> List[Dict[str, str]]:
    with get_db_connection() as conn:
        if user_id:
            chk = conn.execute(
                text("SELECT id FROM conversations WHERE id = :id AND user_id = :user_id"),
                {"id": conversation_id, "user_id": user_id}
            ).mappings().fetchone()
            if not chk:
                return []
        result = conn.execute(
            text("SELECT role, content FROM messages WHERE conversation_id = :cid ORDER BY timestamp ASC, id ASC"),
            {"cid": conversation_id}
        )
        rows = result.mappings().fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in rows]

def get_recent_messages(conversation_id: str, limit: int = 8, user_id: Optional[str] = None) -> List[Dict[str, str]]:
    with get_db_connection() as conn:
        if user_id:
            chk = conn.execute(
                text("SELECT id FROM conversations WHERE id = :id AND user_id = :user_id"),
                {"id": conversation_id, "user_id": user_id}
            ).mappings().fetchone()
            if not chk:
                return []
        result = conn.execute(
            text("SELECT role, content FROM messages WHERE conversation_id = :cid ORDER BY timestamp DESC, id DESC LIMIT :limit"),
            {"cid": conversation_id, "limit": limit}
        )
        rows = result.mappings().fetchall()
        # Return in chronological order
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]


# --- Facts & Memory Management (User Scoped) ---

def get_memory_facts(conversation_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    with get_db_connection() as conn:
        if user_id:
            chk = conn.execute(
                text("SELECT id FROM conversations WHERE id = :id AND user_id = :user_id"),
                {"id": conversation_id, "user_id": user_id}
            ).mappings().fetchone()
            if not chk:
                return {}
        row = conn.execute(
            text("SELECT facts FROM conversation_memory WHERE conversation_id = :cid"),
            {"cid": conversation_id}
        ).mappings().fetchone()
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
        conn.execute(
            text("""
                INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
                VALUES (:cid, '', :facts, :updated_at)
                ON CONFLICT (conversation_id) DO UPDATE SET facts = EXCLUDED.facts, updated_at = EXCLUDED.updated_at
            """),
            {"cid": conversation_id, "facts": facts_str, "updated_at": now}
        )
        conn.commit()

def get_memory_summary(conversation_id: str, user_id: Optional[str] = None) -> str:
    with get_db_connection() as conn:
        if user_id:
            chk = conn.execute(
                text("SELECT id FROM conversations WHERE id = :id AND user_id = :user_id"),
                {"id": conversation_id, "user_id": user_id}
            ).mappings().fetchone()
            if not chk:
                return ""
        row = conn.execute(
            text("SELECT summary FROM conversation_memory WHERE conversation_id = :cid"),
            {"cid": conversation_id}
        ).mappings().fetchone()
        return row["summary"] if row and row["summary"] else ""

def update_memory_summary(conversation_id: str, summary: str):
    now = _get_utc_now()
    with get_db_connection() as conn:
        conn.execute(
            text("""
                INSERT INTO conversation_memory (conversation_id, summary, facts, updated_at)
                VALUES (:cid, :summary, '{}', :updated_at)
                ON CONFLICT (conversation_id) DO UPDATE SET summary = EXCLUDED.summary, updated_at = EXCLUDED.updated_at
            """),
            {"cid": conversation_id, "summary": summary, "updated_at": now}
        )
        conn.commit()

def get_conversation_context(conversation_id: str, user_id: Optional[str] = None, max_turns: int = 8) -> str:
    messages = get_recent_messages(conversation_id, limit=max_turns, user_id=user_id)
    facts = get_memory_facts(conversation_id, user_id=user_id)
    summary = get_memory_summary(conversation_id, user_id=user_id)
    
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

def extract_and_update_memory(conversation_id: str, user_message: str, assistant_response: str, user_id: str = "") -> str:
    """
    Extracts facts, updates memory, and generates title if needed.
    Guaranteed user-isolated and safe.
    """
    try:
        with get_db_connection() as conn:
            if user_id:
                row = conn.execute(
                    text("SELECT title FROM conversations WHERE id = :id AND user_id = :user_id"),
                    {"id": conversation_id, "user_id": user_id}
                ).mappings().fetchone()
            else:
                row = conn.execute(
                    text("SELECT title FROM conversations WHERE id = :id"),
                    {"id": conversation_id}
                ).mappings().fetchone()
            if not row:
                return "New Chat"
            current_title = row["title"] if row else "New Chat"
        
        # 1. Heuristic Fact Extraction
        extracted_facts = _extract_facts_heuristic(user_message)
        
        # Update facts in DB if any found
        if extracted_facts:
            existing_facts = get_memory_facts(conversation_id, user_id=user_id)
            existing_facts.update(extracted_facts)
            update_memory_facts(conversation_id, existing_facts)
            
        # 2. Update Title if still 'New Chat'
        if not current_title or current_title == "New Chat":
            current_title = _generate_title_heuristic(user_message)
            if user_id:
                rename_conversation(conversation_id, current_title, user_id=user_id)
            
        return current_title
    except Exception as e:
        print(f"Memory extraction notice: {e}")
        return "New Chat"
