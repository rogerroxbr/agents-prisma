"""Query Scopus Node for the Scopus Subgraph."""
from typing import Any, Dict
from datetime import date
from src.tools.scopus_tool import ScopusTool
from src.agents.subgraphs.state import SearchSubgraphState

def query_scopus_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Queries Scopus and returns raw results."""
    query = state.get("query", "")
    max_results = state.get("max_results", 100)
    
    print(f"[SCOPUS_NODE] Querying Scopus for: '{query}' (max: {max_results})")
    
    tool = ScopusTool()
    
    try:
        # Default dates for MVP
        default_range = (date(2000, 1, 1), date.today())
        
        raw_results = tool.search(query=query, date_range=default_range, max_results=max_results)
    except Exception as e:
        print(f"[SCOPUS_NODE] Error querying Scopus: {e}")
        raw_results = []
        
    return {"raw_results": raw_results}

__all__ = ["query_scopus_node"]
