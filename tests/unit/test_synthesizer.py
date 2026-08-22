import pytest
from unittest.mock import MagicMock, patch
from src.agents.synthesizer import SynthesizerAgent, SynthesisResult, ThemeGroup

def test_synthesizer_agent_synthesize():
    agent = SynthesizerAgent()
    
    # Mock the LLM chain invoke
    mock_result = SynthesisResult(
        themes=[
            ThemeGroup(
                theme_name="Metformin Efficacy",
                description="Efficacy of Metformin in patients.",
                article_ids=["10.1234/5678"]
            )
        ],
        overall_summary="Metformin is highly effective."
    )
    agent.chain = MagicMock()
    agent.chain.invoke.return_value = mock_result
    
    eligible_articles = [
        {
            "id": "10.1234/5678",
            "title": "A test article",
            "extracted_data": {
                "pico": {
                    "population": ["adults"],
                    "intervention": ["metformin"],
                    "comparison": ["placebo"],
                    "outcome": ["reduced mortality"]
                },
                "risk_of_bias": {"selection": "low"}
            }
        }
    ]
    
    result = agent.synthesize(eligible_articles)
    
    assert result.overall_summary == "Metformin is highly effective."
    assert len(result.themes) == 1
    assert result.themes[0].theme_name == "Metformin Efficacy"


def test_synthesizer_generate_markdown():
    agent = SynthesizerAgent()
    
    synthesis = SynthesisResult(
        themes=[
            ThemeGroup(
                theme_name="Metformin Efficacy",
                description="Efficacy of Metformin.",
                article_ids=["10.1234/5678"]
            )
        ],
        overall_summary="Metformin is highly effective."
    )
    
    eligible_articles = [
        {
            "id": "10.1234/5678",
            "title": "A test article",
            "extracted_data": {
                "pico": {
                    "population": ["adults"],
                    "intervention": ["metformin"],
                    "comparison": ["placebo"],
                    "outcome": ["reduced mortality"]
                },
                "risk_of_bias": {"selection": "low"}
            }
        }
    ]
    
    md_content = agent.generate_markdown_report(
        eligible_articles=eligible_articles,
        synthesis=synthesis,
        project_metadata={"name": "Test Project"}
    )
    
    assert "# Test Project" in md_content
    assert "Metformin is highly effective." in md_content
    assert "### Metformin Efficacy" in md_content
    assert "| 10.1234/5678 | adults | metformin | placebo | reduced mortality | selection: low |" in md_content
