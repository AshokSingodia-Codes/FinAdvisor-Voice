import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
driver = GraphDatabase.driver(
    os.environ['NEO4J_URI'], 
    auth=(os.environ['NEO4J_USERNAME'], os.environ['NEO4J_PASSWORD'])
)
try:
    records, _, _ = driver.execute_query("SHOW DATABASES")
    for r in records:
        print(f"DB: {r['name']} | Default: {r.get('default', 'Unknown')}")
except Exception as e:
    print(f"Error querying databases: {e}")
driver.close()
