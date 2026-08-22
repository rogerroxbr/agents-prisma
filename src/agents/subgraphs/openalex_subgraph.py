"""OpenAlex Subgraph definition.

This subgraph handles fetching from OpenAlex and returning standardized PRISMA metadata.
"""

from typing import Any

from langgraph.graph import StateGraph, END

from src.agents.subgraphs.state import SearchSubgraphState
from src.agents.nodes.query_openalex_node import query_openalex_node
from src.agents.nodes.extract_metadata_node import extract_metadata_node


class OpenAlexSubgraph:
    """Builds the OpenAlex subgraph."""

    def __init__(self):
        self.builder = StateGraph(SearchSubgraphState)
        self._build_graph()

    def _build_graph(self):
        # 1. Add nodes
        self.builder.add_node("query_openalex", query_openalex_node)
        self.builder.add_node("extract_metadata", extract_metadata_node)

        # 2. Add edges
        self.builder.set_entry_point("query_openalex")
        self.builder.add_edge("query_openalex", "extract_metadata")
        self.builder.add_edge("extract_metadata", END)

    def compile(self) -> Any:
        return self.builder.compile()


__all__ = ["OpenAlexSubgraph"]
