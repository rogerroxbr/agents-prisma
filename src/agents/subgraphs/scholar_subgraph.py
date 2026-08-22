"""Google Scholar Subgraph for executing Scholar searches."""

from typing import Any

from langgraph.graph import END, START, StateGraph

from src.agents.nodes.extract_metadata_node import extract_metadata_node
from src.agents.nodes.query_scholar_node import query_scholar_node
from src.agents.subgraphs.state import SearchSubgraphState


class ScholarSubgraph:
    """Scholar subgraph following the Diamond Pattern (Query -> Extract)."""

    def __init__(self):
        self.workflow = StateGraph(SearchSubgraphState)
        self._build_graph()

    def _build_graph(self):
        """Builds the nodes and edges for the subgraph."""

        self.workflow.add_node("query_scholar", query_scholar_node)
        self.workflow.add_node("extract_metadata", extract_metadata_node)

        self.workflow.add_edge(START, "query_scholar")
        self.workflow.add_edge("query_scholar", "extract_metadata")
        self.workflow.add_edge("extract_metadata", END)

    def compile(self) -> Any:
        """Compiles and returns the subgraph."""
        return self.workflow.compile()


__all__ = ["ScholarSubgraph"]
