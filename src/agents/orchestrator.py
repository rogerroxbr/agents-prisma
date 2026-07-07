"""Main orchestrator agent for PRISMA pipeline."""
from typing import Dict, Any, List
from datetime import datetime


class OrchestratorAgent:
    """Orchestrates the PRISMA review pipeline across all phases."""
    
    def __init__(self):
        self.db = None
    
    def run_pipeline(
        self, 
        project_id: int,
        query: str,
        max_results: int = 100,
        date_range: tuple = None
    ) -> Dict[str, Any]:
        """Run the complete PRISMA pipeline.
        
        Args:
            project_id: Database project ID
            query: Search query string
            max_results: Maximum articles to retrieve
            date_range: Optional (start_date, end_date) tuple
            
        Returns:
            Pipeline results dict with all phases' outputs
        """
        print(f"[ORCHESTRATOR] Starting PRISMA pipeline for project {project_id}")
        
        # Phase 1: Identification - Search databases
        print(f"[ORCHESTRATOR] Phase 1: Identification - Searching databases...")
        articles = self._identify_phase(project_id, query, max_results, date_range)
        
        # Create phase record
        if self.db:
            from src.db.models import Phase
            phase = Phase(
                project_id=project_id,
                phase_name="identification",
                status="completed",
                progress=25.0,
                artifacts={"articles_count": len(articles)}
            )
            self.db.add(phase)
        
        # Phase 2: Screening - Filter articles
        print(f"[ORCHESTRATOR] Phase 2: Screening - Filtering articles...")
        screened = self._screen_phase(project_id, articles[:50])  # Batch of 50
        
        if self.db:
            from src.db.models import Phase
            phase.progress = 50.0
            included_count = len([a for a in screened if a.get("decision") == "include"])
            excluded_count = len([a for a in screened if a.get("decision") == "exclude"])
            phase.artifacts = {"included": included_count, "excluded": excluded_count}
        
        # Phase 3: Eligibility - Deep reading (placeholder for MVP)
        print(f"[ORCHESTRATOR] Phase 3: Eligibility - Deep reading...")
        eligible = self._eligibility_phase(project_id, screened[:20])  # Sample
        
        if self.db:
            phase.progress = 75.0
            phase.artifacts = {"eligible_count": len(eligible)}
        
        # Phase 4: Synthesis - Final outputs
        print(f"[ORCHESTRATOR] Phase 4: Synthesis - Generating final outputs...")
        synthesis = self._synthesize_phase(project_id, eligible)
        
        if self.db:
            phase.progress = 100.0
            phase.artifacts = synthesis
        
        # Commit changes
        if self.db:
            self.db.commit()
        
        print(f"[ORCHESTRATOR] Pipeline completed!")
        
        return {
            "project_id": project_id,
            "query": query,
            "total_found": len(articles),
            "screened_count": len(screened),
            "included_count": len([a for a in screened if a.get("decision") == "include"]),
            "synthesis": synthesis
        }

    def _identify_phase(
        self, 
        project_id: int, 
        query: str, 
        max_results: int,
        date_range: tuple = None
    ) -> List[Dict[str, Any]]:
        """Phase 1: Identification - Search PubMed and Scopus."""
        # Mock results for testing (can be replaced with real API calls)
        return [{"title": f"Test Article {i}", "doi": f"10.1234/test{i}", "decision": "include"} for i in range(max_results)]
    
    def _screen_phase(self, project_id: int, articles: List[Dict]) -> List[Any]:
        """Phase 2: Screening - LLM-based filtering."""
        # Simple keyword-based screening for MVP
        included = []
        excluded = []
        
        print(f"[ORCHESTRATOR] Screening {len(articles)} articles...")
        
        for article in articles[:50]:  # Process batch of 50
            title_lower = article.get("title", "").lower()
            
            # Simple inclusion criteria (can be extended)
            if "diabetes" in title_lower or "glucose" in title_lower:
                included.append({"title": article["title"], "doi": article["doi"], "decision": "include"})
            else:
                excluded.append({"title": article["title"], "doi": article["doi"], "decision": "exclude"})
        
        print(f"[ORCHESTRATOR] Screening complete: {len(included)} included, {len(excluded)} excluded")
        
        return included + excluded
    
    def _eligibility_phase(self, project_id: int, articles: List[Any]) -> List[Any]:
        """Phase 3: Eligibility - Deep reading (placeholder for MVP)."""
        print(f"[ORCHESTRATOR] Eligibility phase - {len(articles)} articles for deep reading")
        
        # For MVP, assume all screened articles are eligible
        # In production, would use MCP MarkItDown for PDF processing
        return articles[:20]  # Sample of 20
    
    def _synthesize_phase(self, project_id: int, articles: List[Any]) -> Dict[str, Any]:
        """Phase 4: Synthesis - Generate final outputs."""
        print(f"[ORCHESTRATOR] Synthesizing {len(articles)} articles...")
        
        synthesis = {
            "total_included": len(articles),
            "articles": [
                {
                    "title": a.get("title", ""),
                    "authors": a.get("authors", []),
                    "doi": a.get("doi", ""),
                    "abstract": a.get("abstract", "")
                }
                for a in articles
            ]
        }
        
        print(f"[ORCHESTRATOR] Synthesis complete!")
        return synthesis


__all__ = ["OrchestratorAgent"]
