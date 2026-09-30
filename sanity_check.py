import os
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

print("--- 1. GROQ MODEL CHECK ---")
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    print("GROQ_API_KEY not found in environment!")
else:
    headers = {"Authorization": f"Bearer {groq_api_key}"}
    try:
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
        response.raise_for_status()
        models = response.json().get("data", [])
        model_names = [m["id"] for m in models]
        print(f"llama-3.1-70b-versatile present: {'llama-3.1-70b-versatile' in model_names}")
        print("Available Groq models:")
        for m in model_names:
            if "llama" in m.lower():
                print(f"  - {m}")
    except Exception as e:
        print(f"Error checking Groq models: {e}")

print("\n--- 2. NEO4J SANITY CHECK ---")
neo4j_uri = os.environ.get("NEO4J_URI")
neo4j_user = os.environ.get("NEO4J_USERNAME")
neo4j_password = os.environ.get("NEO4J_PASSWORD")

if not all([neo4j_uri, neo4j_user, neo4j_password]):
    print("Missing Neo4j credentials in environment!")
else:
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        print(f"Connecting to {neo4j_uri}...")
        with driver.session() as session:
            result = session.run("RETURN 1 AS num")
            record = result.single()
            print(f"Query returned: {record['num']}")
        driver.close()
        print("Connection successful and closed.")
    except Exception as e:
        print(f"Neo4j connection error: {e}")
