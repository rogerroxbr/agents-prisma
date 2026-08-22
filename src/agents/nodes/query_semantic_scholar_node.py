"""Query Semantic Scholar Node for the Semantic Scholar Subgraph."""

from src.agents.subgraphs.state import SearchSubgraphState
from src.tools.semantic_scholar_tool import SemanticScholarClient


def query_semantic_scholar_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Queries Semantic Scholar and returns raw results."""
    query = state.get("query", "")
    max_results = state.get("max_results", 100)

    print(f"[QUERY_SEMANTIC_SCHOLAR] Executing search for: {query}")

    tool = SemanticScholarClient()

    try:
        raw_results = tool.search(
            query=query, max_results=max_results
        )
        print(f"[QUERY_SEMANTIC_SCHOLAR] Found {len(raw_results)} raw results")
    except Exception as e:
        print(f"[QUERY_SEMANTIC_SCHOLAR] Error querying Semantic Scholar: {e}")
        raw_results = []

    return {"raw_results": raw_results}


__all__ = ["query_semantic_scholar_node"]
