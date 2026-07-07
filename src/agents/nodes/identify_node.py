"""Identification phase - PubMed/Scopus search (pure function)."""
from typing import Any, Dict, List
import asyncio

from src.agents.state import PRISMAState, IdentificationState

# Import existing tools and instantiate them
try:
    from src.tools.pubmed_tool import PubMedTool
    PubmedMCP = PubMedTool()  # Instantiate the tool
except ImportError:
    PubmedMCP = None
    
try:
    from src.tools.scopus_tool import ScopusTool
    ScopusMCP = ScopusTool()  # Instantiate the tool
except ImportError:
    ScopusMCP = None


def query_pubmed_node(state: PRISMAState) -> List[Dict[str, Any]]:
    """Pure function: Query PubMed API for raw metadata.
    
    Args:
        state: Current PRISMAState
        
    Returns:
        List of raw PubMed search results
    """
    query = state.get("query", "")
    max_results = state.get("max_results", 100)
    
    if not PubmedMCP or not query:
        return []
    
    try:
        date_range = state.get("date_range")
        results = PubmedMCP.search(query, date_range=date_range, max_results=max_results)
        return results[:max_results]
    except Exception as e:
        print(f"[IDENTIFY_NODE] PubMed query error: {e}")
        return []


def query_scopus_node(state: PRISMAState) -> List[Dict[str, Any]]:
    """Pure function: Query Scopus API for raw metadata.
    
    Args:
        state: Current PRISMAState
        
    Returns:
        List of raw Scopus search results
    """
    query = state.get("query", "")
    max_results = state.get("max_results", 100)
    
    if not ScopusMCP or not query:
        return []
    
    try:
        date_range = state.get("date_range")
        results = ScopusMCP.search(query, date_range=date_range, max_results=max_results)
        return results[:max_results]
    except Exception as e:
        print(f"[IDENTIFY_NODE] Scopus query error: {e}")
        return []


async def _parallel_search(state: PRISMAState) -> Dict[str, List[Dict[str, Any]]]:
    """Execute PubMed and Scopus queries in parallel."""
    
    pubmed_results = await asyncio.to_thread(query_pubmed_node, state)
    scopus_results = await asyncio.to_thread(query_scopus_node, state)
    
    return {
        "pubmed": pubmed_results,
        "scopus": scopus_results
    }


def identify_node(state: PRISMAState) -> PRISMAState:
    """Pure function: Complete Identification phase with parallel PubMed/Scopus search.
    
    Args:
        state: Current PRISMAState
        
    Returns:
        Updated state with raw metadata from both sources
    """
    query = state.get("query", "")
    max_results = state.get("max_results", 100)
    
    print(f"[IDENTIFY_NODE] Starting parallel search for: '{query[:50]}...')")
    
    # Execute both sources in parallel
    results_dict = asyncio.run(_parallel_search(state))
    
    total_found = sum(len(res) for res in results_dict.values())
    
    print(f"[IDENTIFY_NODE] Found {total_found} articles across sources")
    
    # Create or update IdentificationState
    ident_state = state.get("identification")
    if not ident_state:
        ident_state = IdentificationState()
        
    ident_state.sources = results_dict
    ident_state.total_found = total_found
    ident_state.metadata_extracted = False
    
    # Note: Returning a partial state dict for LangGraph to merge
    return {
        "identification": ident_state,
        "articles_count": total_found,
        "progress": 25.0,
        "phase": "screening"
    }


__all__ = ["identify_node", "query_pubmed_node", "query_scopus_node"]
