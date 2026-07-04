"""Searcher Agent - PubMed API integration."""
from typing import Optional, List, Dict, Any
import logging

from src.tools.pubmed_tool import PubMedTool


class SearcherAgent:
    """Search agent for identifying articles via PubMed API."""

    def __init__(self):
        self.logger = logging.getLogger(f"agents.searcher.{id(self)}")
        self.tool = PubMedTool()

    def search_articles(
        self, query: str, date_range: tuple[str, str] | None = None, max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Searches PubMed for articles matching the query.

        Args:
            query: Search term (e.g., "diabetes AND insulin").
            date_range: Optional tuple of (YYYY-MM-DD, YYYY-MM-DD).
            max_results: Maximum number of results to return.

        Returns:
            List of article metadata dicts with doi, pmid, title, authors, abstract.
        """
        self.logger.info(f"Searching PubMed for query: {query!r}")

        # Build date filter if provided
        params = {}
        if date_range is not None and len(date_range) >= 2:
            params["date"] = f"{date_range[0]} TO {date_range[1]}"

        results = self.tool.search(query, tuple(date_range or ("", "")), max_results)

        for r in results:
            self.logger.info(f"Found article: PMID={r.get('pmid')}, DOI={r.get('doi')}")
        
        return results


__all__ = ["SearcherAgent"]
