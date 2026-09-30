import os
import json
from dotenv import load_dotenv

# Set pythonpath to allow absolute imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nodes.graph_traversal import GraphTraversalNode

load_dotenv()
node = GraphTraversalNode()
res = node.query_company_risks('Apple Inc.')
print("=== ACTUAL PRODUCTION QUERY RESULT ===")
for r in res:
    # Truncate text for readability
    r['text'] = r['text'][:150] + "..."
    print(json.dumps(r, indent=2))
node.close()
