"""Unit tests for MarkItDownTool."""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.tools.markitdown_tool import MarkItDownTool


@pytest.fixture
def mock_md_tool():
    """Fixture to create a MarkItDownTool with mocked MarkItDown."""
    with patch("src.tools.markitdown_tool.MarkItDown") as mock_md:
        tool = MarkItDownTool(email="test@example.com")
        tool.md = MagicMock()
        return tool


@patch("src.tools.markitdown_tool.requests.get")
def test_get_pdf_url_from_unpaywall_success(mock_get, mock_md_tool):
    """Test successful Unpaywall PDF URL retrieval."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "is_oa": True,
        "best_oa_location": {"url_for_pdf": "https://example.com/test.pdf"}
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    url = mock_md_tool._get_pdf_url_from_unpaywall("10.1234/test")
    assert url == "https://example.com/test.pdf"


@patch("src.tools.markitdown_tool.requests.get")
def test_get_pdf_url_from_unpaywall_not_oa(mock_get, mock_md_tool):
    """Test Unpaywall when article is not Open Access."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "is_oa": False
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    url = mock_md_tool._get_pdf_url_from_unpaywall("10.1234/test")
    assert url is None


@patch("src.tools.markitdown_tool.requests.get")
def test_get_pdf_url_from_unpaywall_timeout(mock_get, mock_md_tool):
    """Test Unpaywall request timeout."""
    mock_get.side_effect = requests.exceptions.Timeout("Timeout")

    url = mock_md_tool._get_pdf_url_from_unpaywall("10.1234/test")
    assert url is None


@patch("src.tools.markitdown_tool.requests.get")
def test_download_pdf_success(mock_get, mock_md_tool):
    """Test successful PDF download."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {"Content-Type": "application/pdf"}
    mock_response.iter_content.return_value = [b"test data"]
    mock_get.return_value = mock_response

    temp_path = mock_md_tool._download_pdf("https://example.com/test.pdf")
    
    assert temp_path is not None
    assert os.path.exists(temp_path)
    
    with open(temp_path, "rb") as f:
        assert f.read() == b"test data"
        
    os.remove(temp_path)


@patch("src.tools.markitdown_tool.requests.get")
def test_download_pdf_failure(mock_get, mock_md_tool):
    """Test PDF download failure (HTTP error)."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
    mock_get.return_value = mock_response

    temp_path = mock_md_tool._download_pdf("https://example.com/test.pdf")
    assert temp_path is None


def test_convert_to_markdown_success(mock_md_tool):
    """Test MarkItDown conversion."""
    mock_result = MagicMock()
    mock_result.text_content = "# Test Markdown"
    mock_md_tool.md.convert.return_value = mock_result

    result = mock_md_tool.convert_to_markdown("dummy.pdf")
    assert result == "# Test Markdown"


def test_convert_to_markdown_empty(mock_md_tool):
    """Test MarkItDown conversion with empty result."""
    mock_result = MagicMock()
    mock_result.text_content = ""
    mock_md_tool.md.convert.return_value = mock_result

    result = mock_md_tool.convert_to_markdown("dummy.pdf")
    assert result == "Error: Converted text is empty."


@patch.object(MarkItDownTool, "_get_pdf_url_from_unpaywall")
@patch.object(MarkItDownTool, "_download_pdf")
@patch.object(MarkItDownTool, "convert_to_markdown")
def test_process_article_success(mock_convert, mock_download, mock_get_url, mock_md_tool):
    """Test full processing workflow."""
    mock_get_url.return_value = "https://example.com/test.pdf"
    
    # Create an actual dummy file so os.remove doesn't complain
    import tempfile
    fd, dummy_file = tempfile.mkstemp()
    os.close(fd)
    
    mock_download.return_value = dummy_file
    mock_convert.return_value = "# Success"

    result = mock_md_tool.process_article("10.1234/test")
    assert result == "# Success"
    assert not os.path.exists(dummy_file)  # Should have been cleaned up


@patch.object(MarkItDownTool, "_get_pdf_url_from_unpaywall")
def test_process_article_no_pdf(mock_get_url, mock_md_tool):
    """Test full processing workflow when no PDF URL is found."""
    mock_get_url.return_value = None

    result = mock_md_tool.process_article("10.1234/test")
    assert "Error: Could not find Open Access PDF" in result
