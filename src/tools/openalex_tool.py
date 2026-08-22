"""OpenAlex API integration."""

import os
from typing import Any
import logging
import requests


class OpenAlexClient:
    """OpenAlex API Client.
    
    Extracts metadata from OpenAlex (https://api.openalex.org/).
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.openalex.org/works"
        
        # OpenAlex provides a "polite pool" with faster response times if an email is provided
        self.email = os.getenv("OPENALEX_EMAIL", "test@example.com")

    def search(
        self, query: str, max_results: int = 100
    ) -> list[dict[str, Any]]:
        """Executes an OpenAlex search.

        Args:
            query: Search term.
            max_results: Maximum number of results to return.

        Returns:
            List of article metadata dicts with doi, title, authors, abstract.
        """
        self.logger.info(f"[OpenAlex] Searching for: {query}")
        
        params = {
            "search": query,
            "per-page": min(max_results, 200),
            "mailto": self.email,
            "sort": "relevance_score:desc"
        }

        results = []
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("results", [])
            
            for item in items:
                # Extract authors
                authors = []
                for authorship in item.get("authorships", []):
                    author = authorship.get("author", {})
                    if author and "display_name" in author:
                        authors.append(author["display_name"])
                
                # Extract abstract (OpenAlex returns abstract as an inverted index)
                abstract = ""
                abstract_inverted_index = item.get("abstract_inverted_index")
                if abstract_inverted_index:
                    # Reconstruct abstract from inverted index
                    word_index = []
                    for word, positions in abstract_inverted_index.items():
                        for pos in positions:
                            word_index.append((pos, word))
                    word_index.sort(key=lambda x: x[0])
                    abstract = " ".join([word for _, word in word_index])

                doi_val = item.get("doi") or ""
                url_val = item.get("doi") or item.get("id") or ""
                
                results.append({
                    "doi": doi_val.replace("https://doi.org/", ""),
                    "title": item.get("title") or "",
                    "authors": authors,
                    "abstract": abstract,
                    "url": url_val
                })
                
                if len(results) >= max_results:
                    break

        except Exception as e:
            self.logger.error(f"[OpenAlex] Search error: {e}")

        self.logger.info(f"[OpenAlex] Found {len(results)} results")
        return results


__all__ = ["OpenAlexClient"]
