"""Tool for Scopus API integration."""

import logging
import time
from datetime import date
from typing import Any

import requests


class ScopusTool:
    """Scopus search tool for PRISMA pipeline (Elsevier v2 API)."""

    def __init__(self, api_key: str = "", logger: logging.Logger | None = None):
        self.base_url = "https://api.elsevier.com/content"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.api_key = api_key or ""

        # Configure logging if not provided
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def search(
        self,
        query: str,
        date_range: tuple[date, date] | None = None,
        max_results: int = 100,
        retry_attempts: int = 3,
        backoff_factor: float = 1.0,
    ) -> list[dict[str, Any]]:
        """Executes a Scopus search and returns metadata.

        Args:
            query: Search term (e.g., "diabetes AND insulin").
            date_range: Optional tuple of (YYYY-MM-DD, YYYY-MM-DD).
            max_results: Maximum number of results to return.
            retry_attempts: Number of retry attempts on failure.
            backoff_factor: Exponential backoff factor for retries.

        Returns:
            List of article metadata dicts with doi, title, authors, abstract.

        Raises:
            ValueError: If all retry attempts fail.
            requests.RequestException: On network errors.
        """
        self.logger.info(
            f"Searching Scopus for query: {query!r}",
            extra={"max_results": max_results, "retry_attempts": retry_attempts},
        )

        url = f"{self.base_url}/search/query"

        params = {
            "query": query,
            "api-key": self.api_key or "",
            "size": min(max_results, 200),  # Scopus max per request is 200
            "title-abstract keywords": query,
        }

        if date_range is not None and len(date_range) >= 2:
            params["from-date"] = str(date_range[0])
            params["to-date"] = str(date_range[1])

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(1, retry_attempts + 1):
            try:
                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code != 200:
                    error_msg = (
                        f"Scopus API HTTP {response.status_code}: {response.text[:200]}"
                    )
                    self.logger.warning(error_msg)
                    last_error = ValueError(error_msg)

                    if attempt < retry_attempts:
                        wait_time = backoff_factor * (2**attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue

                return self._parse_results(response.json())

            except requests.RequestException as e:
                error_msg = f"Scopus API network error (attempt {attempt}/{retry_attempts}): {e!s}"
                self.logger.warning(error_msg)
                last_error = e

                if attempt < retry_attempts:
                    wait_time = backoff_factor * (2**attempt)
                    time.sleep(wait_time)

        # All retries failed
        error_msg = f"Scopus search failed after {retry_attempts} attempts. Last error: {last_error}"
        self.logger.error(error_msg, extra={"query": query})
        raise last_error

    def _parse_results(self, json_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parses Scopus JSON response to standardized format."""
        results = []

        if "result" not in json_data or "item" not in json_data["result"]:
            self.logger.info("No results found for query", extra={"query": ""})
            return results

        total_results = len(json_data["result"]["item"])
        self.logger.info(f"Found {total_results} articles in Scopus response")

        for item in json_data["result"]["item"]:
            result = {
                "doi": "",
                "title": "",
                "authors": [],
                "abstract": "",
                "pub_date": None,
                "url": "",
                "source_title": "",  # Journal/conference name
                "citations_count": 0,  # Citation count if available
            }

            # Extract DOI (Scopus uses 'eid' as internal ID)
            prism = item.get("prism", {})
            result["doi"] = prism.get("eid", "")

            # Extract title
            result["title"] = prism.get("title", "")

            # Extract publication date
            pub_date = prism.get("pubDate", "")
            if pub_date:
                try:
                    result["pub_date"] = pub_date.split("-")[
                        0
                    ]  # Keep YYYY-MM-DD format
                except (IndexError, AttributeError):
                    self.logger.debug(f"Failed to parse date: {pub_date}")

            # Extract source title (journal/conference)
            result["source_title"] = prism.get("sourcetitle", "")

            # Extract URL
            eid = prism.get("eid", "")
            if eid:
                result["url"] = f"https://www.scopus.com/inward/record.uri?eid={eid}"

            # Extract authors
            author_list = []
            if "author" in item:
                author = item["author"]
                if isinstance(author, list):
                    author_list = [a.get("name", "") for a in author]
                elif isinstance(author, dict):
                    author_list = [author.get("name", "")]

            # Limit to first 10 authors (common practice)
            result["authors"] = author_list[:10]

            # Extract abstract
            if "abstract" in item:
                abs_data = item["abstract"].get("value", "")
                if abs_data:
                    result["abstract"] = abs_data
                    self.logger.debug(
                        f"Abstract extracted for: {result['title'][:50]}..."
                    )

            results.append(result)

        self.logger.info(
            f"Parsed {len(results)} articles from Scopus response",
            extra={"query": json_data.get("query", "")},
        )

        return results


__all__ = ["ScopusTool"]
