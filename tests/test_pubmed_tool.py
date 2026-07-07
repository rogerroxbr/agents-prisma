"""Unit tests for PubMedTool."""
import pytest
from unittest.mock import MagicMock, patch
from src.tools.pubmed_tool import PubMedTool


class TestPubMedTool:
    """Test suite for PubMedTool (3 test cases)."""
    
    def test_pubmed_tool_initialization(self):
        """Test PubMedTool initializes with correct URLs."""
        tool = PubMedTool()
        
        assert tool.base_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        assert "Content-Type" in tool.headers
    
    @patch('src.tools.pubmed_tool.requests.get')
    def test_pubmed_search_success(self, mock_get):
        """Test PubMed search returns parsed results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "doi": "10.1234/test",
                    "pmid": "123456",
                    "title": "Diabetes Study",
                    "authors": [{"name": "Author One"}],
                    "abstract": {"content": "Abstract text here"},
                    "pub_date": "2024-01-01"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        tool = PubMedTool()
        results = tool.search("diabetes", (None, None), 10)
        
        assert len(results) == 1
        assert results[0]["title"] == "Diabetes Study"
    
    @patch('src.tools.pubmed_tool.requests.get')
    def test_pubmed_search_empty_results(self, mock_get):
        """Test PubMed search handles empty response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        tool = PubMedTool()
        results = tool.search("nonexistent", (None, None), 10)
        
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
