"""Integration test for the full PRISMA LangGraph pipeline."""
import pytest

from src.agents.orchestrator_langgraph import MainStateGraph


@pytest.fixture
def mock_apis(mocker):
    """Mock external APIs to prevent network calls during integration tests."""
    mock_pubmed = mocker.patch('src.tools.pubmed_tool.PubMedTool.search')
    mock_scopus = mocker.patch('src.tools.scopus_tool.ScopusTool.search')
    mock_screener = mocker.patch('src.agents.screener.ScreeningAgent.screen_batch')
    mock_md_tool = mocker.patch('src.agents.nodes.read_node.MarkItDownTool')
    mock_reader = mocker.patch('src.agents.nodes.read_node.DeepReaderAgent')
    mock_synthesizer = mocker.patch('src.agents.nodes.synthesize_node.SynthesizerAgent')
    
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
    
    # Mock Read Node components
    mock_md_instance = mocker.MagicMock()
    mock_md_instance.process_article.return_value = "Mock Markdown Text"
    mock_md_tool.return_value = mock_md_instance
    
    mock_reader_instance = mocker.MagicMock()
    mock_reader_instance.analyze_article.return_value = {
        "population": "Mock Population",
        "intervention": "Mock Intervention",
        "comparator": "Mock Comparator",
        "outcome": "Mock Outcome",
        "risk_of_bias": "Low",
        "methodology": "RCT",
        "confidence": 0.9,
        "markdown": "Mock Markdown Text"
    }
    mock_reader.return_value = mock_reader_instance
    
    # Mock SynthesizerAgent
    mock_synth_instance = mocker.MagicMock()
    from src.agents.synthesizer import SynthesisResult, ThemeGroup
    mock_synth_instance.synthesize.return_value = SynthesisResult(
        themes=[ThemeGroup(theme_name="Mock Theme", description="Mock Desc", article_ids=["10.1111/pubmed1"])],
        overall_summary="Mock Summary"
    )
    mock_synth_instance.generate_markdown_report.return_value = "Mock Report Content"
    mock_synthesizer.return_value = mock_synth_instance
    
    return (mock_pubmed, mock_scopus, mock_screener, mock_md_tool, mock_reader, mock_synthesizer)


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
    decisions_list = [d.get("decision") if isinstance(d, dict) else d for d in screen.decisions.values()]
    assert decisions_list.count("include") == 1
    assert decisions_list.count("exclude") == 1
    
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
