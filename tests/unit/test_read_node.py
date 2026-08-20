"""Unit tests for the read_node."""

from unittest.mock import MagicMock, patch

from src.agents.nodes.read_node import read_node
from src.agents.state import PRISMAState, ScreeningState


@patch("src.agents.nodes.read_node.MarkItDownTool")
@patch("src.agents.nodes.read_node.DeepReaderAgent")
def test_read_node_no_screened_articles(mock_reader_cls, mock_md_cls):
    """Test read_node with no screening state."""
    state = PRISMAState(screening=None)
    result = read_node(state)
    assert result == {"phase": "synthesize"}


@patch("src.agents.nodes.read_node.MarkItDownTool")
@patch("src.agents.nodes.read_node.DeepReaderAgent")
def test_read_node_no_included_articles(mock_reader_cls, mock_md_cls):
    """Test read_node where all articles were excluded."""
    screen_state = ScreeningState(
        total_screened=1,
        included_count=0,
        excluded_count=1,
        decisions={123: {"decision": "exclude"}}
    )
    state = PRISMAState(screening=screen_state)
    result = read_node(state)
    assert result == {"phase": "synthesize"}


@patch("src.agents.nodes.read_node.MarkItDownTool")
@patch("src.agents.nodes.read_node.DeepReaderAgent")
def test_read_node_success(mock_reader_cls, mock_md_cls):
    """Test read_node with included articles."""
    # Mock tools
    mock_md = MagicMock()
    mock_md.process_article.return_value = "# Mocked Markdown"
    mock_md_cls.return_value = mock_md

    mock_reader = MagicMock()
    mock_reader.analyze_article.return_value = {
        "population": "Pop",
        "intervention": "Int",
        "comparator": "Comp",
        "outcome": "Out",
        "risk_of_bias": "Low",
        "methodology": "RCT",
        "confidence": 0.9,
    }
    mock_reader_cls.return_value = mock_reader

    # Mock state
    art_id = hash("10.1234/test")
    
    screen_state = ScreeningState(
        total_screened=1,
        included_count=1,
        excluded_count=0,
        decisions={art_id: {"decision": "include", "reason": "test"}}
    )
    
    ident_state = MagicMock()
    ident_state.sources = {
        "pubmed": [
            {"title": "Test Title", "doi": "10.1234/test"}
        ]
    }
    
    state = PRISMAState(screening=screen_state, identification=ident_state)
    
    # Run node
    result = read_node(state)
    
    assert "eligibility" in result
    eligibility = result["eligibility"]
    
    assert eligibility.pdfs_extracted == 1
    assert len(eligibility.pico_data) == 1
    assert eligibility.pico_data[0]["population"] == "Pop"
    assert eligibility.extraction_confidence == 0.9
    assert len(eligibility.markdown_outputs) == 1
    assert "Mocked Markdown" in eligibility.markdown_outputs[0]
