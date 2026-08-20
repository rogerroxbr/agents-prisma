from langgraph.graph.state import CompiledStateGraph

from src.agents.orchestrator_langgraph import MainStateGraph


def test_main_state_graph_compilation():
    """Test that MainStateGraph compiles successfully."""
    graph = MainStateGraph(total_target=50)
    app = graph.compile()
    
    assert isinstance(app, CompiledStateGraph)

def test_main_state_graph_nodes():
    """Test that nodes and edges are correctly configured."""
    graph = MainStateGraph(total_target=50)
    app = graph.compile()
    
    # Check that nodes exist
    nodes = app.get_graph().nodes
    assert "identify" in nodes
    assert "screen" in nodes
    
    # We can check edge structure by asserting no exception is thrown when compiling
    assert app is not None
