import os
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

print('--- 1. VERIFYING GROQ MODELS ---')
api_key = os.environ.get('GROQ_API_KEY')
headers = {'Authorization': f'Bearer {api_key}'}
try:
    resp = requests.get('https://api.groq.com/openai/v1/models', headers=headers).json()
    models = [m['id'] for m in resp.get('data', [])]
    is_qwen = "qwen/qwen3.8-27b" in models
    print(f'Is qwen/qwen3.8-27b in Groq models? {is_qwen}')
    print(f'Available models: {models}')
except Exception as e:
    print('Failed to fetch models:', e)

NEO4J_URI = os.environ['NEO4J_URI']
NEO4J_USERNAME = os.environ['NEO4J_USERNAME']
NEO4J_PASSWORD = os.environ['NEO4J_PASSWORD']
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

print('\n--- 3. CHECKING METRICS ---')
with driver.session() as session:
    res = session.run('MATCH (m:Metric) RETURN m.name as name')
    for r in res:
        print(f'Metric Node: {r["name"]}')
    
    res = session.run('MATCH (src)-[r]->(m:Metric) RETURN src.name, type(r), m.name, properties(r) LIMIT 10')
    print('Relationships pointing to Metric:')
    for r in res:
        print(f'{r[0]} -[{r[1]} {r[3]}]-> {r[2]}')
        
print('\n--- 4. CHECKING COMPANIES ---')
with driver.session() as session:
    res = session.run('MATCH (c:Company) RETURN c.name as name')
    for r in res:
        print(f'Company Node: {r["name"]}')

print('\n--- 5. CHECKING MENTIONED_IN CITATIONS ---')
with driver.session() as session:
    res = session.run('MATCH (e)-[:MENTIONED_IN]->(c:Chunk) RETURN e.name, c.id, c.text LIMIT 3')
    for r in res:
        print(f'\nEntity: {r[0]}')
        print(f'Chunk ID: {r[1]}')
        print(f'Text preview: {r[2][:300]}...')

driver.close()
