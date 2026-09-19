import sys
import os
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We detect if we can connect to Neo4j. If not, we mock the heavy dependencies so the script can still run
# and test the other routes (Router, Math, Live Data, Direct Chat).
import socket
neo4j_running = False
try:
    with socket.create_connection(("127.0.0.1", 7687), timeout=1):
        neo4j_running = True
except OSError:
    neo4j_running = False

if not neo4j_running:
    print("Neo4j not detected. Mocking graph dependencies for the simulation...")
    mock_neo4j = MagicMock()
    sys.modules['langchain_neo4j'] = mock_neo4j
    sys.modules['langchain_neo4j.graphs.neo4j_graph'] = mock_neo4j
    mock_hf = MagicMock()
    sys.modules['langchain_huggingface'] = mock_hf
    sys.modules['langchain_huggingface.embeddings'] = mock_hf
    sys.modules['langchain_huggingface.embeddings.huggingface'] = mock_hf

# Now import the graph
from graph.workflow import app_graph

def run_simulation():
    questions = [
        "Hi, I am looking for financial advice.",
        "What is the current stock price and recent news for Apple?",
        "Calculate the WACC if equity is 100, debt is 50, cost of equity is 0.08, cost of debt is 0.04, and tax rate is 0.20.",
        "What is the difference between Direct and Indirect Taxation?"
    ]
    
    report_content = "# Automated Conversation Simulation Report\n\n"
    if not neo4j_running:
        report_content += "> [!WARNING]\n> Neo4j was not running during this simulation. The textbook retrieval question will show an error or mock output, but the routing decision will still be validated.\n\n"
    
    for q in questions:
        report_content += f"## User Query: {q}\n"
        print(f"\nProcessing: {q}")
        
        try:
            state = {"original_question": q, "current_question": q, "retrieved_context": []}
            
            # Run the conversation through the LangGraph AI flow
            result = app_graph.invoke(state)
            
            decision = result.get("routing_decision", "N/A")
            draft = result.get("draft_answer", "N/A")
            final = result.get("final_answer", "N/A")
            
            report_content += f"**Routing Decision**: `{decision}`\n\n"
            report_content += f"**Draft Answer**:\n{draft}\n\n"
            report_content += f"**Final Answer**:\n{final}\n\n"
            report_content += "---\n\n"
            
        except Exception as e:
            report_content += f"**Error occurred during execution**: {str(e)}\n\n"
            report_content += "---\n\n"
            
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/conversation_simulation_report.md"
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(report_content)
    print(f"\nSimulation complete! Report saved to {report_path}")

if __name__ == "__main__":
    run_simulation()
