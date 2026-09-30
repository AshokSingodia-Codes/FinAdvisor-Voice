import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
driver = GraphDatabase.driver(
    os.environ['NEO4J_URI'], 
    auth=(os.environ['NEO4J_USERNAME'], os.environ['NEO4J_PASSWORD'])
)
try:
    with driver.session() as session:
        records = session.run('SHOW INDEXES').data()
        for r in records:
            name = r['name']
            if name not in ['index_343aff4e', 'index_f7700477']:
                print(f"{name}: state={r.get('state')}")
except Exception as e:
    print(e)
driver.close()
