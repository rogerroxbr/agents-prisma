"""Query Web of Science node for subgraph."""

from src.agents.subgraphs.state import SearchSubgraphState
from src.tools.web_of_science_tool import WebOfScienceClient


def query_wos_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Executes search on Web of Science.

    Args:
        state: Current SearchSubgraphState

    Returns:
        Updated state with Web of Science results
    """
    query = state.get("query", "")
    max_results = state.get("max_results", 100)

    print(f"[QUERY_WOS] Executing search for: {query}")

    client = WebOfScienceClient()
    
    try:
        results = client.search(
            query=query, 
            date_range=("2015-01-01", "2026-12-31"), # Default range or from state
            max_results=max_results
        )
        
        print(f"[QUERY_WOS] Found {len(results)} raw results")
        return {"raw_results": results}
    except Exception as e:
        print(f"[QUERY_WOS] Error querying Web of Science: {e}")
        return {"raw_results": []}

__all__ = ["query_wos_node"]
