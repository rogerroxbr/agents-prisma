"""Tool for downloading and converting PDFs to Markdown using MarkItDown."""

import os
import tempfile

import requests
from markitdown import MarkItDown


class MarkItDownTool:
    """Tool for retrieving PDF from a DOI and converting it to markdown."""

    def __init__(self, email: str = "test@example.com"):
        self.email = email
        self.md = MarkItDown()

    def _get_pdf_url_from_unpaywall(self, doi: str) -> str | None:
        """Use Unpaywall API to find an Open Access PDF URL for a DOI."""
        try:
            url = f"https://api.unpaywall.org/v2/{doi}?email={self.email}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("is_oa") and data.get("best_oa_location"):
                    return data["best_oa_location"].get("url_for_pdf")
        except Exception as e:
            print(f"[MarkItDownTool] Error querying Unpaywall for {doi}: {e}")
        return None

    def _download_pdf(self, url: str) -> str | None:
        """Download a PDF from a URL to a temporary file and return its path."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            if response.status_code == 200:
                fd, temp_path = tempfile.mkstemp(suffix=".pdf")
                with os.fdopen(fd, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return temp_path
        except Exception as e:
            print(f"[MarkItDownTool] Error downloading PDF from {url}: {e}")
        return None

    def convert_to_markdown(self, file_path: str) -> str:
        """Convert a local file to Markdown using MarkItDown."""
        try:
            result = self.md.convert(file_path)
            return result.text_content
        except Exception as e:
            print(f"[MarkItDownTool] Error converting {file_path} to markdown: {e}")
            return f"Error converting document: {e!s}"

    def process_article(self, doi: str) -> str:
        """Main method: retrieve DOI PDF and convert it to Markdown."""
        print(f"[MarkItDownTool] Processing article DOI: {doi}")
        pdf_url = self._get_pdf_url_from_unpaywall(doi)

        if not pdf_url:
            return "Error: Could not find Open Access PDF for this DOI."

        print(f"[MarkItDownTool] Found OA PDF URL: {pdf_url}")
        temp_pdf_path = self._download_pdf(pdf_url)

        if not temp_pdf_path:
            return "Error: Failed to download PDF."

        print(
            "[MarkItDownTool] Downloaded to temporary file. Converting to Markdown..."
        )
        markdown_text = self.convert_to_markdown(temp_pdf_path)

        # Cleanup
        try:
            os.remove(temp_pdf_path)
        except Exception as e:
            print(
                f"[MarkItDownTool] Warning: Could not delete temp file {temp_pdf_path}: {e}"
            )

        return markdown_text
