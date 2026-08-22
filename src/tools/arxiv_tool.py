"""ArXiv API integration using the arxiv python package."""

from typing import Any
import logging
import arxiv

class ArxivClient:
    """ArXiv Client using the official python wrapper.
    
    Extracts metadata from ArXiv.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # ArXiv Client is thread-safe and can be reused
        self.client = arxiv.Client()

    def search(
        self, query: str, max_results: int = 100
    ) -> list[dict[str, Any]]:
        """Executes an ArXiv search.

        Args:
            query: Search term (e.g., "diabetes treatments").
            max_results: Maximum number of results to return.

        Returns:
            List of article metadata dicts with doi, title, authors, abstract.
        """
        self.logger.info(f"[ArXiv] Searching for: {query}")
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        try:
            for result in self.client.results(search):
                results.append({
                    "doi": result.doi or "",
                    "title": result.title or "",
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary.replace("\n", " ") or "",
                    "url": result.pdf_url or result.entry_id
                })
        except Exception as e:
            self.logger.error(f"[ArXiv] Search error: {e}")

        self.logger.info(f"[ArXiv] Found {len(results)} results")
        return results

__all__ = ["ArxivClient"]
