"""Tool for PubMed API integration."""
from typing import List, Dict, Any
import requests
from datetime import date


class PubMedTool:
    """PubMed search tool for PRISMA pipeline."""

    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.headers = {"Content-Type": "application/json"}

    def search(self, query: str, date_range: tuple[date, date], max_results: int = 100) -> List[Dict[str, Any]]:
        """Executes a PubMed search and returns metadata."""

        # Build the URL with parameters
        url = f"{self.base_url}?db=pubmed&term={query}&retmax={max_results}"
        params = {
            "date": f"{date_range[0]} TO {date_range[1]}",
            "retmode": "json"
        }

        # Execute the request
        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise ValueError(f"PubMed API error: {response.text}")

        return self._parse_results(response.json())

    def _parse_results(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Pares PubMed JSON response to standardized format."""

        results = []

        if "results" not in json_data:
            return results

        for item in json_data["results"]:
            result = {
                "doi": item.get("doi", ""),
                "pmid": item.get("pmid", ""),
                "title": item.get("title", ""),
                "authors": [],
                "abstract": "",
                "pub_date": None,
                "url": f"https://www.ncbi.nlm.nih.gov/plo/1/{item.get('doi', '')}"
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
                result["abstract"] = item["abstract"].get("content", "")

            results.append(result)

        return results


__all__ = ["PubMedTool"]