import pytest
import os
import json
from unittest.mock import MagicMock, patch

from src.agents.state import PRISMAState, IdentificationState, ScreeningState, EligibilityState, SynthesisState
from src.agents.nodes.synthesize_node import synthesize_node

@patch("src.agents.nodes.synthesize_node.SynthesizerAgent")
@patch("src.agents.nodes.synthesize_node.PRISMAFlowchartGenerator")
def test_synthesize_node(MockFlowchartGen, MockSynthesizerAgent, tmp_path):
    # Setup mocks
    mock_synth_instance = MockSynthesizerAgent.return_value
    mock_synth_result = MagicMock()
    mock_synth_result.model_dump.return_value = {"mock": "dump"}
    mock_synth_instance.synthesize.return_value = mock_synth_result
    mock_synth_instance.generate_markdown_report.return_value = "# Report"

    mock_flowchart_instance = MockFlowchartGen.return_value
    mock_flowchart_instance.generate_mermaid.return_value = "```mermaid\\nflowchart TD\\n```"

    # Create dummy state
    identify_state = IdentificationState(total_found=2)
    identify_state.sources = {
        "pubmed": [
            {"id": "1", "title": "Article 1"}
        ]
    }
    
    screening_state = ScreeningState()
    screening_state.articles_reviewed = ["1"]
    screening_state.decisions = {"1": "include"}

    eligibility_state = EligibilityState()
    eligibility_state.pico_data = [
        {"article_id": "1", "population": ["adults"]}
    ]

    state = PRISMAState(
        phase="synthesize",
        progress=0.0,
        identify=identify_state,
        screening=screening_state,
        eligibility=eligibility_state,
        synthesis=SynthesisState()
    )

    # Patch os.makedirs and builtins.open
    with patch("src.agents.nodes.synthesize_node.os.makedirs") as mock_makedirs, \
         patch("builtins.open") as mock_open:
        
        result_state = synthesize_node(state)
        
        # Assertions
        assert result_state["phase"] == "done"
        assert result_state["progress"] == 100.0
        
        synth = result_state["synthesis"]
        assert synth.flowchart_generated is True
        assert len(synth.markdown_outputs) == 1
        assert "# Report" in synth.markdown_outputs[0]
        assert "```mermaid" in synth.markdown_outputs[0]
        
        # Verify files were opened for writing
        assert mock_open.call_count == 2
        # First call is markdown report, second is json report
        args, kwargs = mock_open.call_args_list[0]
        assert "synthesis_report.md" in args[0]
        
        args, kwargs = mock_open.call_args_list[1]
        assert "synthesis_report.json" in args[0]
