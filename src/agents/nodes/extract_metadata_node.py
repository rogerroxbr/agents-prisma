"""Extract Metadata Node for Search Subgraphs."""
from typing import Any, Dict
from src.agents.subgraphs.state import SearchSubgraphState

def extract_metadata_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Extracts and normalizes metadata from raw search results.
    
    Since our search tools (PubMedTool/ScopusTool) already return fairly 
    structured JSON, this node mainly acts as an adapter/normalizer.
    """
    raw_results = state.get("raw_results", [])
    
    print(f"[EXTRACT_METADATA_NODE] Normalizing {len(raw_results)} results...")
    
    normalized_results = []
    for item in raw_results:
        # Here we could add an LLM call if the metadata was messy,
        # but for now we just ensure standard fields exist.
        normalized = {
            "title": item.get("title", "No Title"),
            "doi": item.get("doi", ""),
            "pmid": item.get("pmid", ""),
            "authors": item.get("authors", []),
            "abstract": item.get("abstract", ""),
            "pub_date": item.get("pub_date", ""),
            "url": item.get("url", ""),
            "source": item.get("source", "unknown")
        }
        normalized_results.append(normalized)
        
    return {"metadata_results": normalized_results}

__all__ = ["extract_metadata_node"]
