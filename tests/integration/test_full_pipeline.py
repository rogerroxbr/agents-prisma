"""Integration test for the full PRISMA LangGraph pipeline."""
import pytest
from unittest.mock import patch, MagicMock

from src.agents.orchestrator_langgraph import MainStateGraph

@pytest.fixture
def mock_apis():
    """Mock external APIs to prevent network calls during integration tests."""
    
    with patch('src.tools.pubmed_tool.PubMedTool.search') as mock_pubmed, \
         patch('src.tools.scopus_tool.ScopusTool.search') as mock_scopus, \
         patch('src.agents.screener.ScreeningAgent.screen_batch') as mock_screener:
        
        # Mock PubMed returns 1 article
        mock_pubmed.return_value = [{
            "title": "PubMed Diabetes Study",
            "doi": "10.1111/pubmed1",
            "pmid": "111",
            "authors": ["Smith J"],
            "abstract": "A study on diabetes."
        }]
        
        # Mock Scopus returns 1 article
        mock_scopus.return_value = [{
            "title": "Scopus Diabetes Study",
            "doi": "10.2222/scopus1",
            "authors": ["Doe J"],
            "abstract": "Another study on diabetes."
        }]
        
        # Mock Screener decision (include PubMed, exclude Scopus)
        def mock_screen_logic(batch, *args, **kwargs):
            results = []
            for item in batch:
                if item.get("doi") == "10.1111/pubmed1":
                    results.append({"article": item, "decision": "include"})
                else:
                    results.append({"article": item, "decision": "exclude"})
            return results
            
        mock_screener.side_effect = mock_screen_logic
        
        yield (mock_pubmed, mock_scopus, mock_screener)


def test_full_pipeline_execution(mock_apis):
    """Test the full pipeline end-to-end execution using MainStateGraph."""
    
    graph = MainStateGraph(total_target=10)
    app = graph.compile()
    
    initial_state = {
        "query": "diabetes",
        "max_results": 5
    }
    
    # Run the compiled app
    # `invoke` processes the whole graph until END
    final_state = app.invoke(initial_state)
    
    # Assertions on Identification Phase
    assert "identification" in final_state
    ident = final_state["identification"]
    assert ident.total_found == 2
    assert ident.metadata_extracted is True
    
    # Assertions on Screening Phase
    assert "screening" in final_state
    screen = final_state["screening"]
    assert screen.batches_processed == 1
    # 2 articles reviewed
    assert len(screen.articles_reviewed) == 2
    # 1 included, 1 excluded
    assert list(screen.decisions.values()).count("include") == 1
    assert list(screen.decisions.values()).count("exclude") == 1
    
    # Assertions on Eligibility Phase (Read)
    assert "eligibility" in final_state
    elig = final_state["eligibility"]
    # Only 1 article was included, so 1 was read
    assert elig.pdfs_extracted == 1
    assert len(elig.pico_data) == 1
    
    # Assertions on Synthesis Phase
    assert "synthesis" in final_state
    synth = final_state["synthesis"]
    assert synth.flowchart_generated is True
    assert len(synth.markdown_outputs) > 0
    
    # Check overall progress
    assert final_state["progress"] == 100.0
    assert final_state["phase"] == "done"
