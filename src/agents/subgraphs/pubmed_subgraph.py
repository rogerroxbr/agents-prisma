"""PubMed Subgraph for executing PubMed searches."""
from typing import Any
from langgraph.graph import StateGraph, START, END

from src.agents.subgraphs.state import SearchSubgraphState
from src.agents.nodes.query_pubmed_node import query_pubmed_node
from src.agents.nodes.extract_metadata_node import extract_metadata_node

class PubMedSubgraph:
    """PubMed subgraph following the Diamond Pattern (Query -> Extract)."""
    
    def __init__(self):
        self.workflow = StateGraph(SearchSubgraphState)
        self._build_graph()
        
    def _build_graph(self):
        """Builds the nodes and edges for the subgraph."""
        
        self.workflow.add_node("query_pubmed", query_pubmed_node)
        self.workflow.add_node("extract_metadata", extract_metadata_node)
        
        self.workflow.add_edge(START, "query_pubmed")
        self.workflow.add_edge("query_pubmed", "extract_metadata")
        self.workflow.add_edge("extract_metadata", END)
        
    def compile(self) -> Any:
        """Compiles and returns the subgraph."""
        return self.workflow.compile()

__all__ = ["PubMedSubgraph"]
