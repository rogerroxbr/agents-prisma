"""Tests for PubMedTool integration."""
import pytest
from src.tools.pubmed_tool import PubMedTool


class TestPubMedTool:
    """Test suite for PubMedTool."""

    def test_initialization(self):
        """Verify tool initializes with correct base URL."""
        tool = PubMedTool()
        assert tool.base_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        assert "Content-Type" in tool.headers

    def test_search_with_date_range(self, caplog):
        """Test search with date filter applied."""
        tool = PubMedTool()
        results = tool.search("diabetes", ("2024-01-01", "2026-12-31"))

        assert isinstance(results, list)
        for r in results:
            assert any(k in ["doi", "pmid", "title"] for k in r.keys())


class TestSearcherAgent:
    """Test suite for SearcherAgent."""

    def test_initialization(self):
        """Verify agent initializes with PubMedTool instance."""
        from src.agents.searcher import SearcherAgent

        agent = SearcherAgent()
        assert hasattr(agent, "pubmed_tool")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
