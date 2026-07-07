"""Unit tests for ScreeningAgent (with pytest-mock)."""
import pytest
from src.agents.screener import ScreeningAgent, ScreeningDecision, PICOExtracted


@pytest.fixture
def mock_llm(mocker):
    """Mock the ChatOpenAI and its structured output to return deterministic decisions."""
    mock_chat_class = mocker.patch('src.agents.screener.ChatOpenAI')
    mock_chat_instance = mocker.MagicMock()
    mock_structured = mocker.MagicMock()
    
    # When structured_llm.invoke is called, return a predefined decision
    def mock_invoke(prompt_text):
        if "diabetes" in prompt_text.lower():
            return ScreeningDecision(
                decision="include",
                reason="Relevant article about diabetes",
                confidence_score=0.9,
                extracted_pico=PICOExtracted(
                    population="Diabetic patients",
                    intervention="Insulin",
                    comparison="Placebo",
                    outcome="Blood glucose"
                )
            )
        else:
            return ScreeningDecision(
                decision="exclude",
                reason="Not relevant to diabetes",
                confidence_score=0.95,
                extracted_pico=None
            )
            
    mock_structured.invoke.side_effect = mock_invoke
    mock_chat_instance.with_structured_output.return_value = mock_structured
    mock_chat_class.return_value = mock_chat_instance
    return mock_chat_class


class TestScreeningAgent:
    
    def test_screener_initialization(self, mock_llm):
        """Test Screener initializes without errors."""
        agent = ScreeningAgent()
        assert agent.criteria is not None
        assert "screening" in agent.criteria.get("stages", {})
    
    def test_screener_load_criteria_success(self, tmp_path, mock_llm):
        """Test loading criteria from JSON file."""
        criteria_file = tmp_path / "criteria.json"
        criteria_file.write_text('{"stages": {"screening": {"inclusion_criteria": ["diabetes"]}}}')
        
        agent = ScreeningAgent()
        agent.load_criteria(str(criteria_file))
        
        assert agent.criteria is not None
        assert "screening" in agent.criteria.get("stages", {})
    
    def test_screener_load_criteria_missing_file(self, tmp_path, mock_llm):
        """Test loading criteria when file doesn't exist uses default."""
        criteria_file = tmp_path / "nonexistent.json"
        
        agent = ScreeningAgent()
        agent.load_criteria(str(criteria_file))
        
        assert "inclusion_criteria" in agent.criteria
    
    def test_screener_screen_batch_includes_keywords(self, mock_llm):
        """Test screening includes articles with matching keywords via LLM mock."""
        agent = ScreeningAgent()
        
        articles = [
            {"title": "Diabetes Study 1", "abstract": "About diabetes"},
            {"title": "Glucose Research", "abstract": "About glucose and diabetes"}
        ]
        
        result = agent.screen_batch(articles, batch_size=50)
        included = [r for r in result if r["decision"] == "include"]
        assert len(included) == 2
        assert result[0]["pico_extracted"]["population"] == "Diabetic patients"
    
    def test_screener_screen_batch_excludes_keywords(self, mock_llm):
        """Test screening excludes articles when LLM decides to exclude."""
        agent = ScreeningAgent()
        
        articles = [
            {"title": "Systematic Review", "abstract": "Unrelated topic"},
            {"title": "Meta Analysis Study", "abstract": "Random text"}
        ]
        
        result = agent.screen_batch(articles, batch_size=50)
        excluded = [r for r in result if r["decision"] == "exclude"]
        assert len(excluded) == 2
    
    def test_screener_fallback_evaluation(self, mock_llm):
        """Test fallback is used when LLM throws an exception."""
        agent = ScreeningAgent()
        
        # Make the mock throw an exception
        agent.structured_llm.invoke.side_effect = Exception("LLM connection error")
        
        articles = [
            {"title": "Meta Analysis Study", "abstract": "Random text"}
        ]
        
        result = agent.screen_batch(articles, batch_size=50)
        # Fallback keyword "meta-analysis" in title causes exclusion
        assert result[0]["decision"] == "exclude"
        assert "Fallback" in result[0]["reason"]
    
    def test_screener_screen_batch_empty_list(self, mock_llm):
        """Test screening handles empty article list."""
        agent = ScreeningAgent()
        result = agent.screen_batch([], batch_size=50)
        assert len(result) == 0
    
    def test_screener_screen_batch_single_article(self, mock_llm):
        """Test screening single article."""
        agent = ScreeningAgent()
        articles = [{"title": "Single Study", "abstract": "diabetes context"}]
        result = agent.screen_batch(articles, batch_size=1)
        assert len(result) == 1
    
    def test_screener_screen_batch_larger_than_limit(self, mock_llm):
        """Test screening respects batch size limit."""
        agent = ScreeningAgent()
        articles = [{"title": f"Study {i}", "abstract": "diabetes"} for i in range(100)]
        result = agent.screen_batch(articles, batch_size=50)
        assert len(result) <= 50
    
    def test_screener_screen_batch_with_score(self, mock_llm):
        """Test screening returns confidence score."""
        agent = ScreeningAgent()
        articles = [{"title": "Diabetes Study", "abstract": "diabetes"}]
        result = agent.screen_batch(articles, batch_size=1)
        assert "score" in result[0]
        assert result[0]["score"] == 0.9
    
    def test_screener_screen_batch_article_structure(self, mock_llm):
        """Test screened article maintains original structure."""
        agent = ScreeningAgent()
        original = {"title": "Study", "doi": "10.1234/test", "abstract": "diabetes"}
        articles = [original]
        result = agent.screen_batch(articles, batch_size=1)
        assert result[0]["article"]["doi"] == "10.1234/test"
    
    def test_screener_screen_batch_decision_values(self, mock_llm):
        """Test screening returns valid decision values."""
        agent = ScreeningAgent()
        articles = [{"title": "Test Study", "abstract": "diabetes"}]
        result = agent.screen_batch(articles, batch_size=1)
        assert result[0]["decision"] in ["include", "exclude"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
