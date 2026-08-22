"""Query ArXiv Node for the ArXiv Subgraph."""

from src.agents.subgraphs.state import SearchSubgraphState
from src.tools.arxiv_tool import ArxivClient


def query_arxiv_node(state: SearchSubgraphState) -> SearchSubgraphState:
    """Queries ArXiv and returns raw results."""
    query = state.get("query", "")
    max_results = state.get("max_results", 100)

    print(f"[QUERY_ARXIV] Executing search for: {query}")

    tool = ArxivClient()

    try:
        raw_results = tool.search(
            query=query, max_results=max_results
        )
        print(f"[QUERY_ARXIV] Found {len(raw_results)} raw results")
    except Exception as e:
        print(f"[QUERY_ARXIV] Error querying ArXiv: {e}")
        raw_results = []

    return {"raw_results": raw_results}


__all__ = ["query_arxiv_node"]
