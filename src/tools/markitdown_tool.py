"""Tool for downloading and converting PDFs to Markdown using MarkItDown."""

import logging
import os
import tempfile

import requests
from markitdown import MarkItDown

logger = logging.getLogger(__name__)


class MarkItDownTool:
    """Tool for retrieving PDF from a DOI and converting it to markdown."""

    def __init__(self, email: str = "test@example.com"):
        self.email = email
        try:
            self.md = MarkItDown()
        except Exception as e:
            logger.error(f"[MarkItDownTool] Failed to initialize MarkItDown: {e}")
            self.md = None

    def _get_pdf_url_from_unpaywall(self, doi: str) -> str | None:
        """Use Unpaywall API to find an Open Access PDF URL for a DOI."""
        if not doi:
            return None
            
        try:
            url = f"https://api.unpaywall.org/v2/{doi}?email={self.email}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get("is_oa") and data.get("best_oa_location"):
                pdf_url = data["best_oa_location"].get("url_for_pdf")
                if pdf_url:
                    return str(pdf_url)
        except requests.exceptions.Timeout:
            logger.error(f"[MarkItDownTool] Timeout querying Unpaywall for {doi}")
        except requests.exceptions.RequestException as e:
            logger.error(f"[MarkItDownTool] Request error querying Unpaywall for {doi}: {e}")
        except Exception as e:
            logger.error(f"[MarkItDownTool] Unexpected error querying Unpaywall for {doi}: {e}")
        return None

    def _download_pdf(self, url: str) -> str | None:
        """Download a PDF from a URL to a temporary file and return its path."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if content type is actually PDF (optional, but good practice)
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower() and 'application/octet-stream' not in content_type.lower():
                 logger.warning(f"[MarkItDownTool] Warning: URL {url} returned non-PDF content type: {content_type}")
                 
            fd, temp_path = tempfile.mkstemp(suffix=".pdf")
            with os.fdopen(fd, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return temp_path
        except requests.exceptions.Timeout:
            logger.error(f"[MarkItDownTool] Timeout downloading PDF from {url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"[MarkItDownTool] Request error downloading PDF from {url}: {e}")
        except Exception as e:
            logger.error(f"[MarkItDownTool] Unexpected error downloading PDF from {url}: {e}")
        return None

    def convert_to_markdown(self, file_path: str) -> str:
        """Convert a local file to Markdown using MarkItDown."""
        if not self.md:
            return "Error: MarkItDown library not properly initialized."
            
        try:
            result = self.md.convert(file_path)
            if not result or not result.text_content:
                return "Error: Converted text is empty."
            return str(result.text_content)
        except Exception as e:
            logger.error(f"[MarkItDownTool] Error converting {file_path} to markdown: {e}")
            return f"Error converting document: {e!s}"

    def process_article(self, doi: str) -> str:
        """Main method: retrieve DOI PDF and convert it to Markdown."""
        logger.info(f"[MarkItDownTool] Processing article DOI: {doi}")
        pdf_url = self._get_pdf_url_from_unpaywall(doi)

        if not pdf_url:
            return "Error: Could not find Open Access PDF for this DOI."

        logger.info(f"[MarkItDownTool] Found OA PDF URL: {pdf_url}")
        temp_pdf_path = self._download_pdf(pdf_url)

        if not temp_pdf_path:
            return "Error: Failed to download PDF."

        logger.info("[MarkItDownTool] Downloaded to temporary file. Converting to Markdown...")
        markdown_text = self.convert_to_markdown(temp_pdf_path)

        # Cleanup
        try:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
        except Exception as e:
            logger.warning(f"[MarkItDownTool] Warning: Could not delete temp file {temp_pdf_path}: {e}")

        return markdown_text
