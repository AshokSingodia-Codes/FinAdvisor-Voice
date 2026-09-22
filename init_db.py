"""
Database Initialization & Migration Script for FinAdvisor-X (Neon PostgreSQL / Local DB)

Usage:
  python init_db.py
  python init_db.py "postgresql://user:pass@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
"""

import sys
import os
from dotenv import load_dotenv

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

from sqlalchemy import inspect, text
from config.settings import settings
from core.memory import (
    metadata,
    create_db_engine,
    get_database_url,
    init_db
)

def run_init(custom_url: str = None):
    target_url = custom_url or get_database_url()
    
    # Hide password in logs for security
    masked_url = target_url
    if "@" in masked_url and "://" in masked_url:
        try:
            protocol_part, rest = masked_url.split("://", 1)
            userinfo, host_part = rest.split("@", 1)
            if ":" in userinfo:
                user, _ = userinfo.split(":", 1)
                masked_url = f"{protocol_part}://{user}:******@{host_part}"
        except Exception:
            pass
    
    print("\n=======================================================")
    print("[INIT] FinAdvisor-X Database Initialization & Migration")
    print("=======================================================")
    print(f"Target Database URL: {masked_url}")
    
    db_type = "PostgreSQL (Neon)" if "postgres" in target_url else "SQLite (Local Fallback)"
    print(f"Dialect Detected:    {db_type}")
    print("-------------------------------------------------------")
    
    print("[*] Connecting to database and creating tables & indexes...")
    engine = create_db_engine(db_url=target_url)
    
    try:
        # Run table creation and constraint setup
        init_db(target_engine=engine)
        
        # Inspect created tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\n[+] Migration completed successfully! Verified tables in database:")
        for t in sorted(tables):
            cols = [c["name"] for c in inspector.get_columns(t)]
            indexes = [idx["name"] for idx in inspector.get_indexes(t)]
            print(f"  * Table: {t}")
            print(f"    - Columns: {', '.join(cols)}")
            if indexes:
                print(f"    - Indexes: {', '.join(indexes)}")
        
        # Test a query ping
        with engine.connect() as conn:
            res = conn.execute(text("SELECT 1")).scalar()
            print(f"\n[+] Connection test ping: {'OK (1)' if res == 1 else 'Failed'}")
        
        print(f"=======================================================")
        print(f"[SUCCESS] Database is ready for FinAdvisor-X!")
        print(f"=======================================================\n")
    except Exception as e:
        print(f"\n[ERROR] Error during database initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli_url = sys.argv[1] if len(sys.argv) > 1 else None
    run_init(cli_url)
