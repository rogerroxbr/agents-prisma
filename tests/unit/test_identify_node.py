"""Unit tests for identify_node and subgraphs."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from src.agents.nodes.identify_node import identify_node

@pytest.fixture
def mock_subgraphs():
    """Mock the compiled subgraphs used in identify_node."""
    with patch('src.agents.nodes.identify_node.PubMedSubgraph') as MockPubMed, \
         patch('src.agents.nodes.identify_node.ScopusSubgraph') as MockScopus:
        
        mock_pubmed_app = MagicMock()
        mock_scopus_app = MagicMock()
        
        async def mock_pubmed_ainvoke(*args, **kwargs):
            return {"metadata_results": [{"title": "PubMed Article 1", "doi": "10.123/pm1"}]}
            
        async def mock_scopus_ainvoke(*args, **kwargs):
            return {"metadata_results": [{"title": "Scopus Article 1", "doi": "10.123/sc1"}]}
        
        mock_pubmed_app.ainvoke = mock_pubmed_ainvoke
        mock_scopus_app.ainvoke = mock_scopus_ainvoke
        
        MockPubMed.return_value.compile.return_value = mock_pubmed_app
        MockScopus.return_value.compile.return_value = mock_scopus_app
        
        yield (mock_pubmed_app, mock_scopus_app)


def test_identify_node(mock_subgraphs):
    """Test identify_node integrates subgraphs properly."""
    
    initial_state = {
        "query": "diabetes",
        "max_results": 10
    }
    
    # Run the node
    new_state = identify_node(initial_state)
    
    assert "identification" in new_state
    ident_state = new_state["identification"]
    
    assert ident_state.total_found == 2
    assert ident_state.metadata_extracted is True
    assert "pubmed" in ident_state.sources
    assert "scopus" in ident_state.sources
    
    assert ident_state.sources["pubmed"][0]["title"] == "PubMed Article 1"
    assert ident_state.sources["scopus"][0]["title"] == "Scopus Article 1"
    
    assert new_state["phase"] == "screening"
    assert new_state["progress"] == 25.0
