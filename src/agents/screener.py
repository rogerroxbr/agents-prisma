"""Screening agent for LLM-based article filtering."""
from typing import Dict, Any, List
import json


class ScreeningAgent:
    """LLM-based screening agent with PICO extraction and keyword validation."""
    
    def __init__(self):
        self.criteria = None
    
    def load_criteria(self, criteria_file: str = ".planning/prisma_criteria.json"):
        """Load PRISMA criteria from JSON file."""
        try:
            with open(criteria_file, 'r') as f:
                self.criteria = json.load(f)
            print(f"[SCREENING] Loaded criteria from {criteria_file}")
        except FileNotFoundError:
            print("[SCREENING] Criteria file not found, using default template")
            self.criteria = {}
    
    def screen_batch(
        self, 
        articles: List[Dict[str, Any]],
        batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Screen a batch of articles using LLM-based filtering.
        
        Args:
            articles: List of article metadata dicts
            batch_size: Number of articles to process in this batch
            
        Returns:
            List of screened articles with decision and justification
        """
        print(f"[SCREENING] Screening batch of {min(len(articles), batch_size)} articles...")
        
        screened = []
        
        for article in articles[:batch_size]:
            title = article.get("title", "").lower()
            
            # Simple keyword-based screening (can be enhanced with LLM)
            decision = self._evaluate_article(article)
            
            result = {
                "article": article,
                "decision": decision["decision"],  # include/exclude/maybe
                "reason": decision["reason"],
                "score": decision.get("score", 0),
                "pico_extracted": False  # Would be populated by LLM in production
            }
            
            screened.append(result)
        
        included = [s for s in screened if s["decision"] == "include"]
        excluded = [s for s in screened if s["decision"] == "exclude"]
        
        print(f"[SCREENING] Batch complete: {len(included)} included, {len(excluded)} excluded")
        
        return included + excluded
    
    def _evaluate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate single article against screening criteria."""
        title = article.get("title", "").lower()
        abstract = article.get("abstract", "").lower()
        
        # Default inclusion keywords (can be customized via criteria file)
        include_keywords = [
            "diabetes", "glucose", "metformin", "insulin", 
            "hypertension", "cardiovascular", "mortality"
        ]
        
        # Default exclusion keywords
        exclude_keywords = [
            "review", "meta-analysis", "editorial", "letter", 
            "case report", "animal study", "in vitro"
        ]
        
        title_included = any(kw in title for kw in include_keywords)
        title_excluded = any(kw in title for kw in exclude_keywords)
        
        # Decision logic
        if title_excluded:
            return {
                "decision": "exclude",
                "reason": f"Title contains exclusion keyword",
                "score": 0.1
            }
        
        if title_included:
            return {
                "decision": "include",
                "reason": "Title matches inclusion criteria",
                "score": 0.9
            }
        
        # Default to include for MVP (can be changed)
        return {
            "decision": "include",
            "reason": "No matching keywords found, defaulting to include",
            "score": 0.5
        }


__all__ = ["ScreeningAgent"]
