from datetime import datetime

import pytest

from src.agents.state import (
    ArticleMetadata,
    EligibilityState,
    IdentificationState,
    ScreeningState,
    SynthesisState,
)


def test_article_metadata_valid():
    """Test creating a valid ArticleMetadata instance."""
    article = ArticleMetadata(
        doi="10.1038/s41586-020-2649-2",
        title="A valid title",
        authors=["John Doe", "Jane Smith"],
        source="pubmed"
    )
    assert article.doi == "10.1038/s41586-020-2649-2"
    assert article.title == "A valid title"
    assert article.source == "pubmed"

def test_article_metadata_invalid_doi():
    """Test validation failure for invalid DOI."""
    with pytest.raises(ValueError, match="Invalid DOI format"):
        ArticleMetadata(
            doi="invalid-doi",
            title="A valid title",
            source="pubmed"
        )

def test_article_metadata_invalid_authors():
    """Test validation failure for invalid authors."""
    with pytest.raises(ValueError, match="Authors must have at least one valid name"):
        ArticleMetadata(
            title="A valid title",
            authors=["   ", ""],
            source="scopus"
        )

def test_article_metadata_invalid_source():
    """Test validation failure for invalid source."""
    with pytest.raises(ValueError, match="String should match pattern"):
        ArticleMetadata(
            title="A valid title",
            source="invalid_source"
        )

def test_identification_state_default():
    """Test default instantiation of IdentificationState."""
    state = IdentificationState()
    assert state.sources == {}
    assert state.total_found == 0
    assert not state.metadata_extracted
    assert not state.raw_response_processed

def test_identification_state_with_data():
    """Test IdentificationState with sample data."""
    state = IdentificationState(
        sources={"pubmed": [{"id": "123"}], "scopus": [{"id": "456"}]},
        total_found=2,
        metadata_extracted=True,
        raw_response_processed=True
    )
    assert "pubmed" in state.sources
    assert state.total_found == 2

def test_screening_state_default():
    """Test default instantiation of ScreeningState."""
    state = ScreeningState()
    assert state.batches_processed == 0
    assert state.articles_reviewed == []
    assert state.decisions == {}

def test_screening_state_with_data():
    """Test ScreeningState with decisions."""
    state = ScreeningState(
        batches_processed=1,
        articles_reviewed=[1, 2],
        decisions={1: "include", 2: "exclude"},
        current_batch_size=50,
        pending_review_count=48
    )
    assert state.decisions[1] == "include"
    assert state.pending_review_count == 48

def test_eligibility_state_default():
    """Test default EligibilityState."""
    state = EligibilityState()
    assert state.pdfs_extracted == 0
    assert state.pico_data == []

def test_eligibility_state_with_data():
    """Test EligibilityState with data."""
    state = EligibilityState(
        pdfs_extracted=5,
        pico_data=[{"population": "adults", "intervention": "drug X"}],
        markdown_outputs=["# Results"],
        extraction_confidence=0.95
    )
    assert len(state.pico_data) == 1
    assert state.extraction_confidence == 0.95

def test_synthesis_state_default():
    """Test default SynthesisState."""
    state = SynthesisState()
    assert not state.flowchart_generated
    assert state.obsidian_format is True
    assert state.json_backup is True

def test_synthesis_state_with_data():
    """Test SynthesisState with data."""
    state = SynthesisState(
        markdown_outputs=["# Synthesis"],
        flowchart_generated=True,
        obsidian_format=False,
        json_backup=False
    )
    assert state.flowchart_generated
    assert not state.obsidian_format

def test_state_serialization():
    """Test serialization of Pydantic models to dict."""
    state = ScreeningState(
        batches_processed=2,
        decisions={100: "include", 101: "exclude"}
    )
    state_dict = state.model_dump()
    assert isinstance(state_dict, dict)
    assert state_dict["batches_processed"] == 2
    assert state_dict["decisions"] == {100: "include", 101: "exclude"}

def test_state_deserialization():
    """Test deserialization from dict back to Pydantic models."""
    state_dict = {
        "batches_processed": 3,
        "articles_reviewed": [10, 11],
        "decisions": {10: "include", 11: "exclude"},
        "current_batch_size": 25,
        "pending_review_count": 0
    }
    state = ScreeningState(**state_dict)
    assert state.batches_processed == 3
    assert state.decisions[10] == "include"

def test_article_metadata_serialization():
    """Test datetime serialization in ArticleMetadata."""
    dt = datetime(2023, 1, 1, 12, 0, 0)
    article = ArticleMetadata(
        title="Test Serialization",
        source="pubmed",
        created_at=dt
    )
    article_dict = article.model_dump()
    assert isinstance(article_dict["created_at"], datetime)
    
    article_json = article.model_dump_json()
    assert "2023-01-01T12:00:00" in article_json
