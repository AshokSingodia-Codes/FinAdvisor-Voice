from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()
driver = GraphDatabase.driver(os.environ['NEO4J_URI'], auth=(os.environ['NEO4J_USERNAME'], os.environ['NEO4J_PASSWORD']))
with driver.session() as session:
    res = session.run("MATCH (g:Company {name: 'Google LLC'})-[:MENTIONED_IN]->(c) RETURN c.text")
    for row in res:
        print("GOOGLE CHUNK:")
        print(row[0])
driver.close()
