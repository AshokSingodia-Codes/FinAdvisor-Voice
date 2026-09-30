from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
user = os.getenv('NEO4J_USERNAME', 'neo4j')
pwd = os.getenv('NEO4J_PASSWORD', 'password')
driver = GraphDatabase.driver(uri, auth=(user, pwd))

with driver.session() as session:
    session.run("""
    MATCH (c:Chunk) WITH c LIMIT 1 
    MERGE (comp:__Entity__ {name: 'Apple Inc.'}) SET comp:Company 
    MERGE (risk:__Entity__ {name: 'supply chain disruption'}) SET risk:RiskFactor 
    MERGE (comp)-[:FACES_RISK]->(risk) 
    MERGE (risk)-[:MENTIONED_IN]->(c)
    """)
    print("Mock data inserted.")
driver.close()
