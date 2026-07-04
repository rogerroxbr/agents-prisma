"""Searcher Agent - Multi-source API integration."""
from typing import Optional, List, Dict, Any
import logging

from src.tools.pubmed_tool import PubMedTool


class SearcherAgent:
    """Multi-agent search for identifying articles via scientific APIs."""

    def __init__(self):
        self.logger = logging.getLogger(f"agents.searcher.{id(self)}")
        self.pubmed_tool = PubMedTool()

    def search_articles(
        self, query: str, date_range: tuple[str, str] | None = None, max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Searches multiple databases for articles matching the query.

        Args:
            query: Search term (e.g., "diabetes AND insulin").
            date_range: Optional tuple of (YYYY-MM-DD, YYYY-MM-DD).
            max_results: Maximum number of results to return per source.

        Returns:
            List of article metadata dicts with doi, title, authors, abstract.
        """
        self.logger.info(f"Searching databases for query: {query!r}")

        # Search PubMed (primary source)
        pubmed_results = self.pubmed_tool.search(query, date_range or ("", ""), max_results)

        for r in pubmed_results:
            self.logger.info(f"Found article: PMID={r.get('pmid')}, DOI={r.get('doi')}")

        return pubmed_results


__all__ = ["SearcherAgent"]
