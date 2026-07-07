"""State definitions for Search Subgraphs."""
from typing import TypedDict, List, Dict, Any

class SearchSubgraphState(TypedDict):
    """State for search subgraphs (PubMed and Scopus)."""
    query: str
    max_results: int
    raw_results: List[Dict[str, Any]]
    metadata_results: List[Dict[str, Any]]
