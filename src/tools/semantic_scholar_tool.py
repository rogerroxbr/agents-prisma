"""Semantic Scholar API integration."""

from typing import Any
import logging
import requests


class SemanticScholarClient:
    """Semantic Scholar API Client.
    
    Extracts metadata from Semantic Scholar (https://api.semanticscholar.org/graph/v1/paper/search).
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    def search(
        self, query: str, max_results: int = 100
    ) -> list[dict[str, Any]]:
        """Executes a Semantic Scholar search.

        Args:
            query: Search term.
            max_results: Maximum number of results to return.

        Returns:
            List of article metadata dicts with doi, title, authors, abstract.
        """
        self.logger.info(f"[Semantic Scholar] Searching for: {query}")
        
        # Determine how many items we should fetch. 
        # The API limit is typically 100 max per request, we can cap it at max_results
        limit = min(max_results, 100)
        
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,abstract,externalIds,url"
        }

        results = []
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 429:
                self.logger.error("[Semantic Scholar] Rate limited (HTTP 429). You may have hit the 100 req / 5 min limit.")
                return []
                
            response.raise_for_status()
            data = response.json()
            items = data.get("data", [])
            
            for item in items:
                authors = [a.get("name", "") for a in item.get("authors", [])]
                external_ids = item.get("externalIds", {})
                doi = external_ids.get("DOI", "")
                
                results.append({
                    "doi": doi,
                    "title": item.get("title") or "",
                    "authors": authors,
                    "abstract": item.get("abstract") or "",
                    "url": item.get("url") or f"https://doi.org/{doi}" if doi else ""
                })
                
        except Exception as e:
            self.logger.error(f"[Semantic Scholar] Search error: {e}")

        self.logger.info(f"[Semantic Scholar] Found {len(results)} results")
        return results


__all__ = ["SemanticScholarClient"]
