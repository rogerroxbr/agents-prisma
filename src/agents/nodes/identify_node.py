"""Identification phase - PubMed/Scopus search via Subgraphs."""

import asyncio
from typing import Any

from src.agents.state import IdentificationState, PRISMAState
from src.agents.subgraphs.pubmed_subgraph import PubMedSubgraph
from src.agents.subgraphs.scopus_subgraph import ScopusSubgraph
from src.agents.subgraphs.scholar_subgraph import ScholarSubgraph
from src.agents.subgraphs.wos_subgraph import WosSubgraph


async def _parallel_search(state: PRISMAState) -> dict[str, list[dict[str, Any]]]:
    """Execute PubMed and Scopus subgraphs in parallel."""

    query = state.get("query", "")
    max_results = state.get("max_results", 100)

    subgraph_state = {"query": query, "max_results": max_results}

    pubmed_app = PubMedSubgraph().compile()
    scopus_app = ScopusSubgraph().compile()
    scholar_app = ScholarSubgraph().compile()
    wos_app = WosSubgraph().compile()

    print(f"[IDENTIFY_NODE] Invoking parallel subgraphs for '{query}'...")

    pubmed_res, scopus_res, scholar_res, wos_res = await asyncio.gather(
        pubmed_app.ainvoke(subgraph_state), 
        scopus_app.ainvoke(subgraph_state),
        scholar_app.ainvoke(subgraph_state),
        wos_app.ainvoke(subgraph_state)
    )

    return {
        "pubmed": pubmed_res.get("metadata_results", []),
        "scopus": scopus_res.get("metadata_results", []),
        "scholar": scholar_res.get("metadata_results", []),
        "wos": wos_res.get("metadata_results", []),
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
