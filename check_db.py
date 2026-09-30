import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USERNAME", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(uri, auth=(user, password))

def run_checks():
    with driver.session() as session:
        # 1. Check Chunk count
        result = session.run("MATCH (c:Chunk) RETURN count(c) AS count")
        chunk_count = result.single()["count"]
        print(f"Total Chunk nodes: {chunk_count}")

        # 2. Check indexes
        result = session.run("SHOW INDEXES")
        indexes = []
        for record in result:
            indexes.append({
                "name": record.get("name"),
                "type": record.get("type"),
                "entityType": record.get("entityType"),
                "labelsOrTypes": record.get("labelsOrTypes"),
                "properties": record.get("properties"),
                "state": record.get("state")
            })
        
        print("\nIndexes found:")
        for idx in indexes:
            print(f"- {idx['name']} (Type: {idx['type']}, State: {idx['state']})")
            if idx['name'] == "keyword_markdown":
                print("  -> keyword_markdown IS PRESENT!")
                
        # 3. Check graph entity / relationships count
        ent_result = session.run("MATCH (e:__Entity__) RETURN count(e) AS count")
        ent_count = ent_result.single()["count"]
        print(f"\nTotal __Entity__ nodes: {ent_count}")
        
        rel_result = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
        rel_count = rel_result.single()["count"]
        print(f"Total relationships (all types): {rel_count}")
                
if __name__ == "__main__":
    run_checks()
    driver.close()
