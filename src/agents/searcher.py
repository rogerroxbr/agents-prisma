"""Searcher agent for multi-database scientific literature search."""
from typing import Dict, Any, List
from datetime import date


class SearcherAgent:
    """Searches multiple scientific databases (PubMed, Scopus, WoS, Google Scholar)."""
    
    def __init__(self):
        self.pubmed_tool = None
        self.scopus_tool = None
    
    def search_pubmed(
        self, 
        query: str,
        date_range: tuple = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Search PubMed EMBASE API."""
        from src.tools.pubmed_tool import PubMedTool
        
        self.pubmed_tool = PubMedTool()
        
        try:
            results = self.pubmed_tool.search(query, date_range, max_results)
            print(f"[SEARCHER] PubMed search returned {len(results)} results")
            return results
        except Exception as e:
            print(f"[SEARCHER] PubMed search failed: {e}")
            return []
    
    def search_scopus(
        self, 
        query: str,
        date_range: tuple = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Search Scopus API (Elsevier v2)."""
        from src.tools.scopus_tool import ScopusTool
        
        self.scopus_tool = ScopusTool()
        
        try:
            results = self.scopus_tool.search(query, date_range, max_results)
            print(f"[SEARCHER] Scopus search returned {len(results)} results")
            return results
        except Exception as e:
            print(f"[SEARCHER] Scopus search failed: {e}")
            return []
    
    def search_web_of_science(
        self, 
        query: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Search Web of Science API (placeholder for MVP)."""
        print(f"[SEARCHER] Web of Science search placeholder")
        return []
    
    def search_google_scholar(
        self, 
        query: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Search Google Scholar (placeholder for MVP)."""
        print(f"[SEARCHER] Google Scholar search placeholder")
        return []
    
    def multi_source_search(
        self, 
        query: str,
        max_results: int = 100,
        date_range: tuple = None
    ) -> Dict[str, Any]:
        """Execute multi-source search across all databases."""
        print(f"[SEARCHER] Starting multi-source search for: {query}")
        
        results = {
            "pubmed": self.search_pubmed(query, date_range, max_results),
            "scopus": self.search_scopus(query, date_range, max_results),
            "web_of_science": self.search_web_of_science(query, max_results),
            "google_scholar": self.search_google_scholar(query, max_results)
        }
        
        total = sum(len(r) for r in results.values())
        print(f"[SEARCHER] Total results: {total}")
        
        return results


__all__ = ["SearcherAgent"]
