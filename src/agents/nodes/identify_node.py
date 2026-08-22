"""Identification phase - PubMed/Scopus search via Subgraphs."""

import asyncio
from typing import Any

from src.agents.state import IdentificationState, PRISMAState
from src.agents.subgraphs.pubmed_subgraph import PubMedSubgraph
from src.agents.subgraphs.openalex_subgraph import OpenAlexSubgraph
from src.agents.subgraphs.semantic_scholar_subgraph import SemanticScholarSubgraph
from src.agents.subgraphs.arxiv_subgraph import ArxivSubgraph


async def _parallel_search(state: PRISMAState) -> dict[str, list[dict[str, Any]]]:
    """Execute search subgraphs in parallel."""

    query = state.get("query", "")
    max_results = state.get("max_results", 100)

    subgraph_state = {"query": query, "max_results": max_results}

    pubmed_app = PubMedSubgraph().compile()
    openalex_app = OpenAlexSubgraph().compile()
    semantic_scholar_app = SemanticScholarSubgraph().compile()
    arxiv_app = ArxivSubgraph().compile()

    print(f"[IDENTIFY_NODE] Invoking parallel subgraphs for '{query}'...")

    pubmed_res, openalex_res, semantic_scholar_res, arxiv_res = await asyncio.gather(
        pubmed_app.ainvoke(subgraph_state), 
        openalex_app.ainvoke(subgraph_state),
        semantic_scholar_app.ainvoke(subgraph_state),
        arxiv_app.ainvoke(subgraph_state)
    )

    return {
        "pubmed": pubmed_res.get("metadata_results", []),
        "openalex": openalex_res.get("metadata_results", []),
        "semantic_scholar": semantic_scholar_res.get("metadata_results", []),
        "arxiv": arxiv_res.get("metadata_results", []),
    }


def identify_node(state: PRISMAState) -> PRISMAState:
    """Pure function: Complete Identification phase with parallel PubMed/Scopus search subgraphs.

    Args:
        state: Current PRISMAState

    Returns:
        Updated state with raw metadata from both sources
    """
    query = state.get("query", "")

    print(f"[IDENTIFY_NODE] Starting parallel subgraph search for: '{query[:50]}...')")

    # Execute both subgraphs in parallel
    results_dict = asyncio.run(_parallel_search(state))

    total_found = sum(len(res) for res in results_dict.values())

    print(f"[IDENTIFY_NODE] Found {total_found} articles across sources")

    # Create or update IdentificationState
    ident_state = state.get("identification")
    if not ident_state:
        ident_state = IdentificationState()

    ident_state.sources = results_dict
    ident_state.total_found = total_found
    ident_state.metadata_extracted = True  # Extracted via extract_metadata_node

    return {
        "identification": ident_state,
        "articles_count": total_found,
        "progress": 25.0,
        "phase": "screening",
    }


__all__ = ["identify_node"]
