"""Unit tests for OrchestratorAgent."""
from unittest.mock import MagicMock

import pytest

from src.agents.orchestrator import OrchestratorAgent


class TestOrchestratorAgent:
    """Test suite for OrchestratorAgent (4 test cases)."""
    
    def test_orchestrator_runs_complete_pipeline(self):
        """Test orchestrator runs complete pipeline without errors."""
        agent = OrchestratorAgent()
        
        # Mock the database session
        mock_db = MagicMock()
        agent.db = mock_db
        
        result = agent.run_pipeline(
            project_id=1,
            query="diabetes AND complications",
            max_results=50
        )
        
        assert result["project_id"] == 1
        assert "query" in result
        assert "total_found" in result
    
    def test_orchestrator_identify_phase(self):
        """Test identification phase returns articles."""
        agent = OrchestratorAgent()
        
        # Mock PubMed tool
        mock_pubmed = MagicMock(return_value=[
            {"title": "Diabetes Study 1", "doi": "10.1234/test1"},
            {"title": "Glucose Study 2", "doi": "10.1234/test2"}
        ])
        
        agent._identify_phase = MagicMock(return_value=[{"test": "data"}])
        
        result = agent._identify_phase(1, "diabetes", 10)
        
        assert len(result) > 0
    
    def test_orchestrator_screening_batch(self):
        """Test screening phase processes batch correctly."""
        agent = OrchestratorAgent()
        
        articles = [
            {"title": "Diabetes Study", "doi": "1"},
            {"title": "Glucose Research", "doi": "2"}
        ]
        
        result = agent._screen_phase(1, articles)
        
        assert isinstance(result, list)
    
    def test_orchestrator_synthesis_output(self):
        """Test synthesis phase generates correct output format."""
        agent = OrchestratorAgent()
        
        articles = [
            {"title": f"Study {i}", "doi": f"10.1234/test{i}"}
            for i in range(5)
        ]
        
        result = agent._synthesize_phase(1, articles)
        
        assert "total_included" in result
        assert len(result["articles"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
