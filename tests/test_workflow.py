import pytest
from graph.workflow import app_graph

def test_graph_compiles():
    # Simple structural test to ensure the LangGraph state graph compiles correctly
    # If there are dangling edges or invalid node references, this would fail upon import or compilation.
    assert app_graph is not None
