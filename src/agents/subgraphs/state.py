"""State definitions for Search Subgraphs."""

from typing import Any, TypedDict


class SearchSubgraphState(TypedDict):
    """State for search subgraphs (PubMed and Scopus)."""

    query: str
    max_results: int
    raw_results: list[dict[str, Any]]
    metadata_results: list[dict[str, Any]]
