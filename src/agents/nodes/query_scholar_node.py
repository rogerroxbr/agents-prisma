"""Query Google Scholar node for subgraph."""

from src.agents.subgraphs.state import SearchSubgraphState
from src.tools.google_scholar_mcp_tool import GoogleScholarMCPClient


def query_scholar_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Executes search on Google Scholar.

    Args:
        state: Current SearchSubgraphState

    Returns:
        Updated state with Google Scholar results
    """
    query = state.get("query", "")
    max_results = state.get("max_results", 100)

    print(f"[QUERY_SCHOLAR] Executing search for: {query}")

    client = GoogleScholarMCPClient()
    
    try:
        results = client.search(
            query=query, 
            date_range=("2015-01-01", "2026-12-31"), # Default range or from state
            max_results=max_results
        )
        
        print(f"[QUERY_SCHOLAR] Found {len(results)} raw results")
        return {"raw_results": results}
    except Exception as e:
        print(f"[QUERY_SCHOLAR] Error querying Google Scholar: {e}")
        return {"raw_results": []}

__all__ = ["query_scholar_node"]
