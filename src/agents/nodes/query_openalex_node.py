"""Query OpenAlex Node for the OpenAlex Subgraph."""

from src.agents.subgraphs.state import SearchSubgraphState
from src.tools.openalex_tool import OpenAlexClient


def query_openalex_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Queries OpenAlex and returns raw results."""
    query = state.get("query", "")
    max_results = state.get("max_results", 100)

    print(f"[QUERY_OPENALEX] Executing search for: {query}")

    tool = OpenAlexClient()

    try:
        raw_results = tool.search(
            query=query, max_results=max_results
        )
        print(f"[QUERY_OPENALEX] Found {len(raw_results)} raw results")
    except Exception as e:
        print(f"[QUERY_OPENALEX] Error querying OpenAlex: {e}")
        raw_results = []

    return {"raw_results": raw_results}


__all__ = ["query_openalex_node"]
