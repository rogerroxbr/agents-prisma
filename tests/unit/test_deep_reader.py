"""Unit tests for DeepReaderAgent."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from src.agents.deep_reader import DeepReaderAgent


class DummyResult(BaseModel):
    population: str = "Test Population"
    intervention: str = "Test Intervention"
    comparison: str = "Test Comparison"
    outcome: str = "Test Outcome"
    risk_of_bias: str = "Low Risk"
    methodology: str = "Test Methodology"
    confidence_score: float = 0.9


@pytest.fixture
def mock_deep_reader():
    """Fixture to create a DeepReaderAgent with mocked LLM."""
    with patch("src.agents.deep_reader.ChatOpenAI"):
        reader = DeepReaderAgent()
        reader.structured_llm = MagicMock()
        return reader


def test_analyze_article_success(mock_deep_reader):
    """Test successful deep reading extraction."""
    mock_deep_reader.structured_llm.invoke.return_value = DummyResult()

    article = {"title": "Test Title"}
    markdown_text = "# Test Markdown"

    result = mock_deep_reader.analyze_article(article, markdown_text)

    assert result["population"] == "Test Population"
    assert result["comparator"] == "Test Comparison"
    assert result["confidence"] == 0.9
    assert result["markdown"] == markdown_text


def test_analyze_article_failure(mock_deep_reader):
    """Test deep reading extraction with exception."""
    mock_deep_reader.structured_llm.invoke.side_effect = Exception("LLM Error")

    article = {"title": "Test Title"}
    markdown_text = "# Test Markdown"

    result = mock_deep_reader.analyze_article(article, markdown_text, retries=1)

    assert result["population"] == "Error during extraction"
    assert result["confidence"] == 0.0
    assert result["markdown"] == markdown_text


def test_build_prompt_truncation(mock_deep_reader):
    """Test that the prompt truncates long markdown text."""
    long_markdown = "a" * 40000
    prompt = mock_deep_reader._build_prompt("Title", long_markdown)

    assert "CONTENT TRUNCATED" in prompt
    # The truncated text is 30000 chars, plus the prompt template text
    assert len(prompt) < 31000
