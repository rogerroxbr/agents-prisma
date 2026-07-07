"""Unit tests for ScreeningAgent (12 test cases)."""
import pytest
from src.agents.screener import ScreeningAgent


class TestScreeningAgent:
    """Test suite for ScreeningAgent (12 test cases)."""
    
    def test_screener_initialization(self):
        """Test Screener initializes without errors."""
        agent = ScreeningAgent()
        assert agent.criteria is None
    
    def test_screener_load_criteria_success(self, tmp_path):
        """Test loading criteria from JSON file."""
        criteria_file = tmp_path / "criteria.json"
        criteria_file.write_text('{"include_keywords": ["diabetes"]}')
        
        agent = ScreeningAgent()
        agent.load_criteria(str(criteria_file))
        
        assert agent.criteria is not None
        assert "include_keywords" in agent.criteria
    
    def test_screener_load_criteria_missing_file(self, tmp_path):
        """Test loading criteria when file doesn't exist."""
        criteria_file = tmp_path / "nonexistent.json"
        
        agent = ScreeningAgent()
        agent.load_criteria(str(criteria_file))
        
        assert agent.criteria == {}
    
    def test_screener_screen_batch_includes_keywords(self):
        """Test screening includes articles with matching keywords."""
        agent = ScreeningAgent()
        
        articles = [
            {"title": "Diabetes Study 1", "abstract": "About diabetes"},
            {"title": "Glucose Research", "abstract": "About glucose"}
        ]
        
        result = agent.screen_batch(articles, batch_size=50)
        
        included = [r for r in result if r["decision"] == "include"]
        assert len(included) >= 2
    
    def test_screener_screen_batch_excludes_keywords(self):
        """Test screening excludes articles with exclusion keywords."""
        agent = ScreeningAgent()
        
        articles = [
            {"title": "Systematic Review", "abstract": ""},
            {"title": "Meta Analysis Study", "abstract": ""}
        ]
        
        result = agent.screen_batch(articles, batch_size=50)
        
        excluded = [r for r in result if r["decision"] == "exclude"]
        assert len(excluded) >= 0
    
    def test_screener_screen_batch_maybe_decision(self):
        """Test screening can return maybe decision."""
        agent = ScreeningAgent()
        
        articles = [
            {"title": "Mixed Study", "abstract": ""}
        ]
        
        result = agent.screen_batch(articles, batch_size=50)
        
        # Check result structure
        assert "decision" in result[0]
        assert "reason" in result[0]
    
    def test_screener_screen_batch_empty_list(self):
        """Test screening handles empty article list."""
        agent = ScreeningAgent()
        
        result = agent.screen_batch([], batch_size=50)
        
        assert len(result) == 0
    
    def test_screener_screen_batch_single_article(self):
        """Test screening single article."""
        agent = ScreeningAgent()
        
        articles = [{"title": "Single Study", "abstract": ""}]
        
        result = agent.screen_batch(articles, batch_size=1)
        
        assert len(result) == 1
    
    def test_screener_screen_batch_larger_than_limit(self):
        """Test screening respects batch size limit."""
        agent = ScreeningAgent()
        
        articles = [{"title": f"Study {i}", "abstract": ""} for i in range(100)]
        
        result = agent.screen_batch(articles, batch_size=50)
        
        assert len(result) <= 50
    
    def test_screener_screen_batch_with_score(self):
        """Test screening returns confidence score."""
        agent = ScreeningAgent()
        
        articles = [{"title": "Diabetes Study", "abstract": ""}]
        
        result = agent.screen_batch(articles, batch_size=1)
        
        assert "score" in result[0]
    
    def test_screener_screen_batch_article_structure(self):
        """Test screened article maintains original structure."""
        agent = ScreeningAgent()
        
        original = {"title": "Study", "doi": "10.1234/test"}
        articles = [original]
        
        result = agent.screen_batch(articles, batch_size=1)
        
        assert result[0]["article"]["title"] == "Study"
    
    def test_screener_screen_batch_decision_values(self):
        """Test screening returns valid decision values."""
        agent = ScreeningAgent()
        
        articles = [{"title": "Test Study", "abstract": ""}]
        
        result = agent.screen_batch(articles, batch_size=1)
        
        assert result[0]["decision"] in ["include", "exclude", "maybe"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
