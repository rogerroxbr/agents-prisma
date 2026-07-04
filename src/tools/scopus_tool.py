"""Tool for Scopus API integration."""
from typing import List, Dict, Any
import requests


class ScopusTool:
    """Scopus search tool for PRISMA pipeline (Elsevier v2 API)."""

    def __init__(self):
        self.base_url = "https://api.elsevier.com/content"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # TODO: Add API key from environment variable
        self.api_key = ""

    def search(self, query: str, date_range: tuple[str, str] | None = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """Executes a Scopus search and returns metadata.

        Args:
            query: Search term (e.g., "diabetes AND insulin").
            date_range: Optional tuple of (YYYY-MM-DD, YYYY-MM-DD).
            max_results: Maximum number of results to return.

        Returns:
            List of article metadata dicts with doi, title, authors, abstract.
        """
        self.logger.info(f"Searching Scopus for query: {query!r}")

        # Build the URL with parameters
        url = f"{self.base_url}/search/query"

        params = {
            "query": query,
            "api-key": self.api_key or "",  # TODO: Add API key
            "size": max_results,
            "title-abstract keywords": query,
        }

        if date_range is not None and len(date_range) >= 2:
            params["from-date"] = date_range[0]
            params["to-date"] = date_range[1]

        # Execute the request
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise ValueError(f"Scopus API error: {response.text}")

        return self._parse_results(response.json())

    def _parse_results(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parses Scopus JSON response to standardized format."""

        results = []

        if "result" not in json_data or "item" not in json_data["result"]:
            return results

        for item in json_data["result"]["item"]:
            result = {
                "doi": item.get("prism", {}).get("eid", ""),  # Scopus uses 'eid' instead of DOI
                "title": item.get("prism", {}).get("title", ""),
                "authors": [],
                "abstract": "",
                "pub_date": None,
                "url": f"https://www.scopus.com/inward/record.uri?eid={item.get('prism', {}).get('eid')}"
            }

            # Extract authors if available
            if "author" in item:
                author = item["author"]
                if isinstance(author, list):
                    result["authors"] = [a.get("name", "") for a in author]
                elif isinstance(author, dict):
                    result["authors"] = [author.get("name", "")]

            # Extract abstract
            if "abstract" in item:
                result["abstract"] = item["abstract"].get("value", "")

            results.append(result)

        return results


__all__ = ["ScopusTool"]
