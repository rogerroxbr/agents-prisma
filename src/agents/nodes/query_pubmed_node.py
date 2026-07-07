"""Query PubMed Node for the PubMed Subgraph."""
from typing import Any, Dict
from datetime import date
from src.tools.pubmed_tool import PubMedTool
from src.agents.subgraphs.state import SearchSubgraphState

def query_pubmed_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Queries PubMed and returns raw results."""
    query = state.get("query", "")
    max_results = state.get("max_results", 100)
    
    print(f"[PUBMED_NODE] Querying PubMed for: '{query}' (max: {max_results})")
    
    tool = PubMedTool()
    
    try:
        # For MVP, we pass dummy dates or a wide range. 
        # Ideally this would come from state or config.
        default_range = (date(2000, 1, 1), date.today())
        
        # The tool currently parses and returns a clean dictionary.
        # So "raw_results" is already fairly structured by the tool.
        raw_results = tool.search(query=query, date_range=default_range, max_results=max_results)
    except Exception as e:
        print(f"[PUBMED_NODE] Error querying PubMed: {e}")
        raw_results = []
        
    return {"raw_results": raw_results}

__all__ = ["query_pubmed_node"]
