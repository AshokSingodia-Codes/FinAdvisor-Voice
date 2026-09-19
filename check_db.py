import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
uri = os.environ.get('NEO4J_URI')
user = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session(database=user) as session:
    result = session.run("MATCH (c:Chunk) RETURN c.source AS source, count(c) as count")
    print("Database Contents by Source:")
    for record in result:
        print(f"- {record['source']}: {record['count']} chunks")
