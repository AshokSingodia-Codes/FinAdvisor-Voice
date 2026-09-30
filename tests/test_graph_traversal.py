import unittest
from nodes.graph_traversal import GraphTraversalNode

class TestGraphTraversal(unittest.TestCase):
    def setUp(self):
        self.node = GraphTraversalNode()

    def tearDown(self):
        self.node.close()
        
    def test_injection_safety(self):
        # Count nodes before malicious query
        with self.node.driver.session() as session:
            initial_count = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            
        # Using a maliciously crafted string to ensure parameterization protects the query
        malicious_input = "Apple Inc.\" }) MATCH (n) DETACH DELETE n //"
        
        # This should execute safely as a parameter, match nothing, and return an empty list
        results = self.node.query_company_risks(malicious_input)
        self.assertEqual(results, [])
        
        # Count nodes after malicious query to prove DETACH DELETE didn't execute
        with self.node.driver.session() as session:
            final_count = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            
        self.assertEqual(initial_count, final_count, "Node count changed! SQL injection may have succeeded.")
        
if __name__ == "__main__":
    unittest.main()
