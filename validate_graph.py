import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
driver = GraphDatabase.driver(os.environ['NEO4J_URI'], auth=(os.environ['NEO4J_USERNAME'], os.environ['NEO4J_PASSWORD']))

print("=== 1. VERIFY FINAL CHUNK COUNT ===")
try:
    with open('processed_chunks.json', 'r') as f:
        chunks = json.load(f)
        print(f"Total chunks processed: {len(chunks)} / 105")
except Exception as e:
    print(f"Error reading processed_chunks.json: {e}")

with driver.session() as session:
    print("\n=== 2. INVESTIGATE 'Google LLC' ===")
    res = session.run("MATCH (g:Company {name: 'Google LLC'})-[r]-(n) RETURN type(r) as rel_type, labels(n) as node_labels, n.name as node_name, substring(n.text, 0, 150) as chunk_text")
    records = res.data()
    if not records:
        print("Google LLC not found or has no relationships.")
    for r in records:
        print(f"Rel: {r['rel_type']}, Target Node: {r['node_name']} ({r['node_labels']})")
        if r['chunk_text']:
            print(f"Chunk Context: {r['chunk_text']}...")

    print("\n=== 3. MENTIONED_IN SPOT CHECKS ===")
    res = session.run("MATCH (e:__Entity__)-[:MENTIONED_IN]->(c:Chunk) RETURN e.name as entity_name, labels(e) as entity_labels, substring(c.text, 0, 200) as chunk_text LIMIT 3")
    for idx, r in enumerate(res.data()):
        print(f"\nSpot Check {idx+1}:")
        print(f"Entity: {r['entity_name']} {r['entity_labels']}")
        print(f"Text: {repr(r['chunk_text'])}...")

    print("\n=== 4. MULTI-HOP TRAVERSAL TEST (Real Data) ===")
    # Find a RiskFactor that Apple faces, and what that RiskFactor might affect/depend on
    traversal_query = """
    MATCH (c:Company {name: 'Apple Inc.'})-[:FACES_RISK]->(r:RiskFactor)
    MATCH (r)-[rel]-(other)
    WHERE NOT 'Chunk' IN labels(other) AND NOT other.name = 'Apple Inc.'
    RETURN r.name as risk, type(rel) as relationship, other.name as related_entity, labels(other) as related_labels
    LIMIT 5
    """
    res = session.run(traversal_query)
    for r in res.data():
        print(f"Apple Inc. -> FACES_RISK -> ({r['risk']}) -[{r['relationship']}]-> ({r['related_entity']} {r['related_labels']})")

    print("\n=== 5. CHECK FOR TEST DATA ===")
    # Check if the fake 'supply chain disruption' from previous rounds still exists
    res = session.run("MATCH (e {name: 'supply chain disruption'}) RETURN e.name, labels(e)")
    data = res.data()
    if data:
        print(f"WARNING: Test data still exists! {data}")
    else:
        print("Confirmed: 'supply chain disruption' test data is NOT in the graph.")

driver.close()
