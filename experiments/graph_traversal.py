import os
from neo4j import GraphDatabase
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class GraphTraversalNode:
    def __init__(self, uri: str = None, username: str = None, password: str = None):
        uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def query_company_risks(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Executes a parameterized Cypher template to traverse Company -> RiskFactor -> Chunk.
        Never uses string interpolation for user input (injection safety).
        """
        cypher_query = """
        MATCH (c:Company {name: $company_name})-[:FACES_RISK]->(r:RiskFactor)-[:MENTIONED_IN]->(chunk:Chunk)
        RETURN r.name AS risk_factor, chunk.text AS text, chunk.id AS chunk_id
        LIMIT 5
        """
        
        with self.driver.session() as session:
            result = session.run(cypher_query, company_name=company_name)
            records = [dict(record) for record in result]
            
        return records

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the graph traversal node.
        Includes a fallback to hybrid_search if graph returns nothing.
        """
        question = state.get("question", "").lower()
        
        # Extremely basic entity extraction for testing purposes
        company = "Apple Inc." if "apple" in question else None
        
        if company:
            results = self.query_company_risks(company)
            if results:
                # Format results for the state
                evidence = []
                for r in results:
                    evidence.append({
                        "content": f"Risk Factor: {r['risk_factor']}\nDetails: {r['text']}",
                        "metadata": {"chunk_id": r['chunk_id'], "source_type": "graph_traversal"}
                    })
                return {"documents": evidence, "resolved_query": f"Graph query for risks of {company}"}
                
        # Hard fallback if no entities found or graph returns empty
        return {"next": "hybrid_search"}
