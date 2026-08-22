"""Semantic Scholar Subgraph definition.

This subgraph handles fetching from Semantic Scholar and returning standardized PRISMA metadata.
"""

from typing import Any

from langgraph.graph import StateGraph, END

from src.agents.subgraphs.state import SearchSubgraphState
from src.agents.nodes.query_semantic_scholar_node import query_semantic_scholar_node
from src.agents.nodes.extract_metadata_node import extract_metadata_node


class SemanticScholarSubgraph:
    """Builds the Semantic Scholar subgraph."""

    def __init__(self):
        self.builder = StateGraph(SearchSubgraphState)
        self._build_graph()

    def _build_graph(self):
        # 1. Add nodes
        self.builder.add_node("query_semantic_scholar", query_semantic_scholar_node)
        self.builder.add_node("extract_metadata", extract_metadata_node)

        # 2. Add edges
        self.builder.set_entry_point("query_semantic_scholar")
        self.builder.add_edge("query_semantic_scholar", "extract_metadata")
        self.builder.add_edge("extract_metadata", END)

    def compile(self) -> Any:
        return self.builder.compile()


__all__ = ["SemanticScholarSubgraph"]
