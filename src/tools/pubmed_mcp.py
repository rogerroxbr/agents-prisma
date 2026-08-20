"""PubMed MCP Server integration using httpx."""

from typing import Any

import httpx


class PubMedMCPClient:
    """PubMed MCP Client - connects to the official PubMed MCP server.

    URL: https://mcpservers.org/pt-BR/servers/aeghnnsw/pubmed-mcp

    This client uses httpx to communicate with the MCP server's HTTP endpoint,
    which acts as a bridge to the PubMed E-utilities API.
    """

    def __init__(self):
        self.base_url = "https://mcpservers.org/pt-BR/servers/aeghnnsw/pubmed-mcp"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def search(
        self, query: str, date_range: tuple[str, str], max_results: int = 100
    ) -> list[dict[str, Any]]:
        """Executes a PubMed search via MCP server.

        Args:
            query: Search term (e.g., "diabetes AND insulin").
            date_range: Tuple of (YYYY-MM-DD, YYYY-MM-DD).
            max_results: Maximum number of results to return per source.

        Returns:
            List of article metadata dicts with doi, title, authors, abstract.
        """
        # Build the request payload for MCP server
        params = {
            "query": query,
            "date_range": f"{date_range[0]} TO {date_range[1]}",
            "retmax": str(max_results),
            "format": "json",
        }

        self.logger.info(f"MCP Search: query={query!r}, results={max_results}")

        # Execute the request to MCP server
        response = httpx.get(self.base_url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(
                f"PubMed MCP error (status {response.status_code}): {response.text[:500]}"
            )

        return self._parse_mcp_response(response.json())

    def _parse_mcp_response(self, json_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parses PubMed MCP JSON response to standardized format.

        The MCP server returns a wrapped response with 'results' array.
        """
        results = []

        if "results" not in json_data or not isinstance(json_data["results"], list):
            self.logger.warning(
                f"MCP Response structure unexpected: {json_data.keys()}"
            )
            return results

        for item in json_data["results"]:
            result = {
                "doi": item.get("doi", ""),
                "pmid": item.get("pmid", ""),
                "title": item.get("title", ""),
                "authors": [],
                "abstract": "",
                "pub_date": None,
                "url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{item.get('doi', '')}/",
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

        self.logger.info(f"MCP Search complete: {len(results)} articles found")
        return results


__all__ = ["PubMedMCPClient"]
