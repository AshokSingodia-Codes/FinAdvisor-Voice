import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
NEO4J_URI = os.environ['NEO4J_URI']
NEO4J_USERNAME = os.environ['NEO4J_USERNAME']
NEO4J_PASSWORD = os.environ['NEO4J_PASSWORD']
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session() as session:
    res = session.run('MATCH (c:Company {name: "Apple Inc."}) WHERE NOT c:__Entity__ DETACH DELETE c RETURN count(c)')
    print(f"Deleted {res.single()[0]} stale nodes.")
    res = session.run('MATCH (e:__Entity__) DETACH DELETE e RETURN count(e)')
    print(f"Cleared {res.single()[0]} graph entities.")
driver.close()
